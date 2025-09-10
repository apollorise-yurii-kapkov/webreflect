from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime
import json

from app.models.analysis import AnalysisJob, AnalysisResult
from app.models.crawl import CrawledPage
from app.services.crawler import WebsiteCrawler
from app.services.analyzer import WebsiteAnalyzer
from app.services.cost_tracking_service import get_cost_tracking_service
from app.core.database import get_db
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.core.redis import redis_client
from app.schemas.analysis import MessagingAnalysis, MessagingScores


class AnalysisService:
    """Service for managing website analysis workflow."""
    
    def __init__(self):
        self.crawler = WebsiteCrawler()
        self.analyzer = WebsiteAnalyzer()
    
    async def create_analysis_job(self, db: AsyncSession, url: str) -> AnalysisJob:
        """Create a new analysis job."""
        # Validate URL first
        is_valid = await self.crawler.validate_url(url)
        if not is_valid:
            raise ValueError("URL is not accessible")
        
        # Create job
        job = AnalysisJob(url=url, status="pending")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Cache job status
        await redis_client.set_json(
            f"job_status:{job.id}",
            {"status": "pending", "progress": 0},
            expire=3600
        )
        
        return job
    
    async def get_analysis_job(self, db: AsyncSession, job_id: UUID) -> Optional[AnalysisJob]:
        """Get analysis job with results."""
        query = select(AnalysisJob).options(
            selectinload(AnalysisJob.result),
            selectinload(AnalysisJob.pages)
        ).where(AnalysisJob.id == job_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def process_analysis_job(self, db: AsyncSession, job_id: UUID) -> Dict:
        """Process analysis job - crawl and analyze website."""
        try:
            # Get job
            job = await self.get_analysis_job(db, job_id)
            if not job:
                raise ValueError("Job not found")
            
            # Update status to processing
            await self._update_job_status(db, job_id, "processing", 10)
            
            # Step 1: Crawl website
            await self._update_job_status(db, job_id, "processing", 20, "Crawling website...")
            pages_data = await self.crawler.crawl_website(job.url)
            
            if not pages_data:
                await self._update_job_status(db, job_id, "failed", 0, "Failed to crawl website")
                return {"status": "failed", "error": "Failed to crawl website"}
            
            # Step 2: Save crawled pages
            await self._update_job_status(db, job_id, "processing", 40, "Saving crawled data...")
            await self._save_crawled_pages(db, job_id, pages_data)
            
            # Step 3: Analyze content
            await self._update_job_status(db, job_id, "processing", 60, "Analyzing content...")
            analysis_result = await self.analyzer.analyze_website_content(pages_data)
            
            # Step 4: Save analysis results
            await self._update_job_status(db, job_id, "processing", 80, "Saving results...")
            await self._save_analysis_result(db, job_id, analysis_result)
            
            # Step 5: Complete job
            await self._update_job_status(db, job_id, "completed", 100, "Analysis complete")
            
            return {
                "status": "completed",
                "job_id": str(job_id),
                "result": analysis_result
            }
            
        except Exception as e:
            await self._update_job_status(db, job_id, "failed", 0, str(e))
            raise
    
    async def _update_job_status(self, db: AsyncSession, job_id: UUID, status: str, progress: int, message: str = None):
        """Update job status in database and cache."""
        # Update database
        update_values = {
            "status": status,
            "error_message": message if status == "failed" else None
        }
        
        # Set completed_at when job is completed
        if status == "completed":
            from datetime import datetime, timezone
            update_values["completed_at"] = datetime.now(timezone.utc)
        
        stmt = update(AnalysisJob).where(AnalysisJob.id == job_id).values(**update_values)
        await db.execute(stmt)
        await db.commit()
        
        # Update cache
        cache_data = {
            "status": status,
            "progress": progress
        }
        if message:
            cache_data["message"] = message
        
        await redis_client.set_json(f"job_status:{job_id}", cache_data, expire=3600)
    
    async def _save_crawled_pages(self, db: AsyncSession, job_id: UUID, pages_data: List[Dict]):
        """Save crawled pages to database."""
        for page_data in pages_data:
            page = CrawledPage(
                job_id=job_id,
                url=page_data.get('url'),
                title=page_data.get('title'),
                content=page_data.get('content'),
                meta_description=page_data.get('meta_description'),
                h1_tags=page_data.get('h1_tags', []),
                cta_texts=page_data.get('cta_texts', [])
            )
            db.add(page)
        
        await db.commit()
    
    async def _save_analysis_result(self, db: AsyncSession, job_id: UUID, analysis_data: Dict):
        """Save analysis results to database."""
        result = AnalysisResult(
            job_id=job_id,
            content_summary=analysis_data.get('content_summary'),
            messaging_analysis=analysis_data.get('messaging_analysis') if isinstance(analysis_data.get('messaging_analysis'), (dict, str)) else (analysis_data.get('messaging_analysis').dict() if analysis_data.get('messaging_analysis') else None),
            scores=analysis_data.get('scores') if isinstance(analysis_data.get('scores'), (dict, str)) else (analysis_data.get('scores').dict() if analysis_data.get('scores') else None),
            quick_wins=analysis_data.get('quick_wins', []),
            raw_content=analysis_data.get('content_summary')
        )
        
        db.add(result)
        await db.commit()
    
    async def get_job_status(self, job_id: UUID) -> Dict:
        """Get job status from cache or database."""
        # Try cache first
        cached_status = await redis_client.get_json(f"job_status:{job_id}")
        if cached_status:
            return cached_status
        
        # Fallback to database
        return {"status": "unknown", "progress": 0}

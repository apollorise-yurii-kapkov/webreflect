from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update

from app.models.analysis import AnalysisJob, AnalysisResult
from app.models.crawl import CrawledPage
from app.services.crawler import WebsiteCrawler
from app.services.analyzer import WebsiteAnalyzer
from app.core.redis import redis_client
from app.core.database import get_db


class AnalysisService:
    """Coordinates the analysis pipeline."""

    def __init__(self):
        self.crawler = WebsiteCrawler()
        self.analyzer = WebsiteAnalyzer()

    async def create_analysis_job(self, db: AsyncSession, url: str) -> AnalysisJob:
        if not await self.crawler.validate_url(url):
            raise ValueError("URL is not accessible")

        job = AnalysisJob(url=url, status="pending")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        await redis_client.set_json(f"job_status:{job.id}", {"status": "pending", "progress": 0}, expire=3600)
        return job

    async def get_analysis_job(self, db: AsyncSession, job_id: UUID) -> Optional[AnalysisJob]:
        q = select(AnalysisJob).options(
            selectinload(AnalysisJob.result),
            selectinload(AnalysisJob.pages),
        ).where(AnalysisJob.id == job_id)
        res = await db.execute(q)
        return res.scalar_one_or_none()

    async def process_analysis_job(self, job_id: UUID) -> Dict:
        """
        Background task entrypoint.
        ВАЖНО: создаём НОВУЮ сессию БД внутри таска, не используем request-scoped session.
        """
        async for db in get_db():  # открываем собственную сессию на время задачи
            return await self._process_with_session(db, job_id)

    async def _process_with_session(self, db: AsyncSession, job_id: UUID) -> Dict:
        try:
            job = await self.get_analysis_job(db, job_id)
            if not job:
                raise ValueError("Job not found")

            await self._update_status(db, job_id, "processing", 10)
            await self._update_status(db, job_id, "processing", 20, "Crawling website...")
            pages = await self.crawler.crawl_website(job.url)
            if not pages:
                await self._update_status(db, job_id, "failed", 0, "Failed to crawl website")
                return {"status": "failed", "error": "Failed to crawl website"}

            await self._update_status(db, job_id, "processing", 40, "Saving crawled data...")
            await self._save_pages(db, job_id, pages)

            await self._update_status(db, job_id, "processing", 60, "Analyzing content...")
            results = await self.analyzer.analyze_website_content(pages, str(job_id))

            await self._update_status(db, job_id, "processing", 80, "Saving results...")
            await self._save_results(db, job_id, results)

            await self._update_status(db, job_id, "completed", 100, "Analysis complete")
            return {"status": "completed", "job_id": str(job_id), "result": results}
        except Exception as e:
            await self._update_status(db, job_id, "failed", 0, str(e))
            raise

    async def _update_status(self, db: AsyncSession, job_id: UUID, status: str, progress: int, message: str = None):
        values = {"status": status, "error_message": message if status == "failed" else None}
        if status == "completed":
            from datetime import datetime, timezone
            values["completed_at"] = datetime.now(timezone.utc)
        stmt = update(AnalysisJob).where(AnalysisJob.id == job_id).values(**values)
        await db.execute(stmt)
        await db.commit()

        cache = {"status": status, "progress": progress}
        if message:
            cache["message"] = message
        await redis_client.set_json(f"job_status:{job_id}", cache, expire=3600)

    async def _save_pages(self, db: AsyncSession, job_id: UUID, pages: List[Dict]):
        for p in pages:
            db.add(CrawledPage(
                job_id=job_id,
                url=p.get("url"),
                title=p.get("title"),
                content=p.get("content"),
                meta_description=p.get("meta_description"),
                h1_tags=p.get("h1_tags", []),
                cta_texts=p.get("cta_texts", []),
            ))
        await db.commit()

    async def _save_results(self, db: AsyncSession, job_id: UUID, data: Dict):
        result = AnalysisResult(
            job_id=job_id,
            content_summary=data.get("content_summary"),
            messaging_analysis=(
                data.get("messaging_analysis")
                if isinstance(data.get("messaging_analysis"), (dict, str))
                else data.get("messaging_analysis").dict() if data.get("messaging_analysis") else None
            ),
            scores=(
                data.get("scores")
                if isinstance(data.get("scores"), (dict, str))
                else data.get("scores").dict() if data.get("scores") else None
            ),
            quick_wins=data.get("quick_wins", []),
            raw_content=data.get("content_summary"),
        )
        db.add(result)
        await db.commit()

    async def get_job_status(self, job_id: UUID) -> Dict:
        cached = await redis_client.get_json(f"job_status:{job_id}")
        return cached if cached else {"status": "unknown", "progress": 0}

    async def share_analysis_job(self, db: AsyncSession, job_id: UUID) -> bool:
        stmt = update(AnalysisJob).where(AnalysisJob.id == job_id).values(is_shared=True)
        res = await db.execute(stmt)
        await db.commit()
        return res.rowcount > 0

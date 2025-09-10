from typing import Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisJobResponse,
    AnalysisResultResponse,
    AnalysisStatusResponse
)

router = APIRouter()
analysis_service = AnalysisService()


@router.post("/reflect", response_model=AnalysisJobResponse)
async def start_website_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Start website analysis process."""
    try:
        # Create analysis job
        job = await analysis_service.create_analysis_job(db, str(request.url))
        
        # Start background processing
        background_tasks.add_task(
            analysis_service.process_analysis_job,
            db,
            job.id
        )
        
        return AnalysisJobResponse(
            job_id=job.id,
            url=job.url,
            status=job.status,
            created_at=job.created_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to start analysis")


@router.get("/reflect/{job_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get analysis job status."""
    try:
        # Get job from database
        job = await analysis_service.get_analysis_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get cached status for progress
        cached_status = await analysis_service.get_job_status(job_id)
        progress = cached_status.get("progress", 0)
        
        # Build response data
        response_data = {
            "job_id": job.id,
            "url": job.url,
            "status": job.status,
            "progress": progress,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message
        }
        
        # Include result data if job is completed
        if job.status == "completed" and job.result:
            response_data["result"] = {
                "content_summary": job.result.content_summary,
                "messaging_analysis": job.result.messaging_analysis,
                "scores": job.result.scores,
                "quick_wins": job.result.quick_wins
            }
        
        return AnalysisStatusResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get job status")


@router.get("/reflect/{job_id}/result", response_model=AnalysisResultResponse)
async def get_analysis_result(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get complete analysis result."""
    try:
        # Get job with results
        job = await analysis_service.get_analysis_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != "completed":
            raise HTTPException(status_code=400, detail="Analysis not completed yet")
        
        # Build response
        result_data = {
            "job_id": job.id,
            "url": job.url,
            "status": job.status,
            "completed_at": job.completed_at,
            "error_message": job.error_message
        }
        
        if job.result:
            result_data.update({
                "content_summary": job.result.content_summary,
                "messaging_analysis": job.result.messaging_analysis,
                "scores": job.result.scores,
                "quick_wins": job.result.quick_wins
            })
        
        return AnalysisResultResponse(**result_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get analysis result")


@router.get("/reflect/{job_id}/pages")
async def get_crawled_pages(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get crawled pages for a job."""
    try:
        job = await analysis_service.get_analysis_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        pages_data = []
        for page in job.pages:
            pages_data.append({
                "url": page.url,
                "title": page.title,
                "meta_description": page.meta_description,
                "h1_tags": page.h1_tags,
                "cta_texts": page.cta_texts,
                "crawled_at": page.crawled_at
            })
        
        return {"pages": pages_data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get crawled pages")

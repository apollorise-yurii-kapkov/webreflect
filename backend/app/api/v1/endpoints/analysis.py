from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisJobResponse,
    AnalysisStatusResponse,
    AnalysisResultResponse,
)

router = APIRouter()
service = AnalysisService()


@router.post("/reflect", response_model=AnalysisJobResponse)
async def start_website_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Start a website analysis job; return job id immediately."""
    try:
        job = await service.create_analysis_job(db, str(request.url))
        # ВАЖНО: НЕ передаём db в фоновую задачу!
        background_tasks.add_task(service.process_analysis_job, job.id)
        return AnalysisJobResponse(
            job_id=job.id,
            url=job.url,
            status=job.status,
            created_at=job.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to start analysis")


@router.get("/reflect/{job_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Return current status (with partial result if completed)."""
    try:
        job = await service.get_analysis_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        cached = await service.get_job_status(job_id)
        progress = cached.get("progress", 0)

        data: Dict[str, Any] = {
            "job_id": job.id,
            "url": job.url,
            "status": job.status,
            "progress": progress,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message,
        }

        if job.status == "completed" and job.result:
            data["result"] = {
                "content_summary": job.result.content_summary,
                "messaging_analysis": job.result.messaging_analysis,
                "scores": job.result.scores,
                "quick_wins": job.result.quick_wins,
            }

        return AnalysisStatusResponse(**data)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get job status")


@router.get("/reflect/{job_id}/result", response_model=AnalysisResultResponse)
async def get_analysis_result(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the final analysis result."""
    try:
        job = await service.get_analysis_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != "completed":
            raise HTTPException(status_code=400, detail="Analysis not completed yet")

        result: Dict[str, Any] = {
            "job_id": job.id,
            "url": job.url,
            "status": job.status,
            "completed_at": job.completed_at,
            "error_message": job.error_message,
        }
        if job.result:
            result.update({
                "content_summary": job.result.content_summary,
                "messaging_analysis": job.result.messaging_analysis,
                "scores": job.result.scores,
                "quick_wins": job.result.quick_wins,
            })
        return AnalysisResultResponse(**result)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get analysis result")


@router.get("/reflect/{job_id}/pages")
async def get_crawled_pages(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get crawled pages (without raw HTML)."""
    try:
        job = await service.get_analysis_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        pages_data = [{
            "url": p.url,
            "title": p.title,
            "meta_description": p.meta_description,
            "h1_tags": p.h1_tags,
            "cta_texts": p.cta_texts,
            "crawled_at": p.crawled_at,
        } for p in job.pages]

        return {"pages": pages_data}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get crawled pages")


@router.post("/reflect/{job_id}/share")
async def share_analysis_report(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Make a completed analysis report publicly accessible."""
    try:
        job = await service.get_analysis_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != "completed":
            raise HTTPException(status_code=400, detail="Cannot share incomplete analysis")

        await service.share_analysis_job(db, job_id)
        return {"shared": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to share analysis report")


@router.get("/shared/{job_id}", response_model=AnalysisStatusResponse)
async def get_shared_analysis_report(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint to fetch a shared completed report."""
    try:
        job = await service.get_analysis_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Report not found")
        if job.status != "completed":
            raise HTTPException(status_code=400, detail="Analysis not completed")

        data: Dict[str, Any] = {
            "job_id": job.id,
            "url": job.url,
            "status": job.status,
            "progress": 100,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message,
        }
        if job.result:
            data["result"] = {
                "content_summary": job.result.content_summary,
                "messaging_analysis": job.result.messaging_analysis,
                "scores": job.result.scores,
                "quick_wins": job.result.quick_wins,
            }
        return AnalysisStatusResponse(**data)
    except HTTPException:
        raise
    except Exception:
        # Важно: здесь НЕ должно быть опечатки "status code"
        raise HTTPException(status_code=500, detail="Failed to get shared report")

from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.cost_tracking_service import get_cost_tracking_service, CostTrackingService
from pydantic import BaseModel

router = APIRouter()


class CostStatsResponse(BaseModel):
    total_cost: float
    month_total: float
    today_total: float
    top_services: list


class DailyCostsResponse(BaseModel):
    date: str
    total_cost: float
    service_breakdown: dict
    entry_count: int


class MonthlyCostsResponse(BaseModel):
    period: str
    total_cost: float
    daily_breakdown: dict
    service_totals: dict
    entry_count: int


@router.get("/stats", response_model=CostStatsResponse)
async def get_cost_stats(
    cost_service: CostTrackingService = Depends(get_cost_tracking_service)
):
    """Get overall cost statistics."""
    try:
        stats = cost_service.get_cost_stats()
        return CostStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost stats: {str(e)}")


@router.get("/daily", response_model=DailyCostsResponse)
async def get_daily_costs(
    target_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    cost_service: CostTrackingService = Depends(get_cost_tracking_service)
):
    """Get cost breakdown for a specific day."""
    try:
        if target_date:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        else:
            date_obj = datetime.utcnow()
        
        costs = cost_service.get_daily_costs(date_obj)
        return DailyCostsResponse(**costs)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily costs: {str(e)}")


@router.get("/monthly", response_model=MonthlyCostsResponse)
async def get_monthly_costs(
    year: Optional[int] = Query(None, description="Year"),
    month: Optional[int] = Query(None, description="Month (1-12)"),
    cost_service: CostTrackingService = Depends(get_cost_tracking_service)
):
    """Get cost breakdown for a specific month."""
    try:
        if year is None or month is None:
            now = datetime.utcnow()
            year = year or now.year
            month = month or now.month
        
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
        
        costs = cost_service.get_monthly_costs(year, month)
        return MonthlyCostsResponse(**costs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monthly costs: {str(e)}")


@router.get("/export")
async def export_costs(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    service: Optional[str] = Query(None, description="Filter by service"),
    cost_service: CostTrackingService = Depends(get_cost_tracking_service)
):
    """Export cost data for a date range."""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        costs = cost_service.get_costs_by_period(start_dt, end_dt, service)
        
        export_data = []
        for cost in costs:
            export_data.append({
                "id": str(cost.id),
                "service": cost.service,
                "operation": cost.operation,
                "cost_amount": cost.cost_amount,
                "currency": cost.currency,
                "tokens_used": cost.tokens_used,
                "requests_count": cost.requests_count,
                "data_processed_mb": cost.data_processed_mb,
                "job_id": str(cost.job_id) if cost.job_id else None,
                "description": cost.description,
                "occurred_at": cost.occurred_at.isoformat() if cost.occurred_at else None,
                "created_at": cost.created_at.isoformat()
            })
        
        return {
            "period": f"{start_date} to {end_date}",
            "service_filter": service,
            "total_entries": len(export_data),
            "total_cost": sum(item["cost_amount"] for item in export_data),
            "data": export_data
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export costs: {str(e)}")

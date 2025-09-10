from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import Depends
import json
import logging

from app.models.cost_tracking import CostEntry, CostSummary
from app.core.database import get_db

logger = logging.getLogger(__name__)


class CostTrackingService:
    """Service for tracking and analyzing operational costs."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_cost(
        self,
        service: str,
        operation: str,
        cost_amount: float,
        job_id: Optional[str] = None,
        tokens_used: Optional[int] = None,
        requests_count: Optional[int] = None,
        data_processed_mb: Optional[float] = None,
        description: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        occurred_at: Optional[datetime] = None
    ) -> CostEntry:
        """Log a new cost entry."""
        try:
            cost_entry = CostEntry(
                service=service,
                operation=operation,
                cost_amount=cost_amount,
                job_id=job_id,
                tokens_used=tokens_used,
                requests_count=requests_count,
                data_processed_mb=data_processed_mb,
                description=description,
                extra_data=json.dumps(extra_data) if extra_data else None,
                occurred_at=occurred_at or datetime.utcnow()
            )
            
            self.db.add(cost_entry)
            await self.db.commit()
            await self.db.refresh(cost_entry)
            
            logger.info(f"Logged cost: {service}.{operation} = ${cost_amount}")
            return cost_entry
            
        except Exception as e:
            logger.error(f"Failed to log cost entry: {e}")
            await self.db.rollback()
            raise
    
    def get_costs_by_period(
        self,
        start_date: datetime,
        end_date: datetime,
        service: Optional[str] = None
    ) -> List[CostEntry]:
        """Get cost entries for a specific period."""
        query = self.db.query(CostEntry).filter(
            and_(
                CostEntry.occurred_at >= start_date,
                CostEntry.occurred_at <= end_date
            )
        )
        
        if service:
            query = query.filter(CostEntry.service == service)
        
        return query.order_by(CostEntry.occurred_at.desc()).all()
    
    def get_daily_costs(self, date: datetime) -> Dict[str, Any]:
        """Get cost breakdown for a specific day."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        costs = self.get_costs_by_period(start_of_day, end_of_day)
        
        total_cost = sum(cost.cost_amount for cost in costs)
        
        # Group by service
        service_breakdown = {}
        for cost in costs:
            if cost.service not in service_breakdown:
                service_breakdown[cost.service] = {
                    'total_cost': 0,
                    'operations': {},
                    'requests': 0,
                    'tokens': 0
                }
            
            service_breakdown[cost.service]['total_cost'] += cost.cost_amount
            
            if cost.operation not in service_breakdown[cost.service]['operations']:
                service_breakdown[cost.service]['operations'][cost.operation] = 0
            service_breakdown[cost.service]['operations'][cost.operation] += cost.cost_amount
            
            if cost.requests_count:
                service_breakdown[cost.service]['requests'] += cost.requests_count
            if cost.tokens_used:
                service_breakdown[cost.service]['tokens'] += cost.tokens_used
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'total_cost': total_cost,
            'service_breakdown': service_breakdown,
            'entry_count': len(costs)
        }
    
    def get_monthly_costs(self, year: int, month: int) -> Dict[str, Any]:
        """Get cost breakdown for a specific month."""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        costs = self.get_costs_by_period(start_date, end_date)
        
        total_cost = sum(cost.cost_amount for cost in costs)
        
        # Daily breakdown
        daily_costs = {}
        service_totals = {}
        
        for cost in costs:
            day_key = cost.occurred_at.strftime('%Y-%m-%d')
            if day_key not in daily_costs:
                daily_costs[day_key] = 0
            daily_costs[day_key] += cost.cost_amount
            
            if cost.service not in service_totals:
                service_totals[cost.service] = 0
            service_totals[cost.service] += cost.cost_amount
        
        return {
            'period': f"{year}-{month:02d}",
            'total_cost': total_cost,
            'daily_breakdown': daily_costs,
            'service_totals': service_totals,
            'entry_count': len(costs)
        }
    
    def get_cost_stats(self) -> Dict[str, Any]:
        """Get overall cost statistics."""
        # Total costs
        total_query = self.db.query(func.sum(CostEntry.cost_amount)).scalar()
        total_cost = total_query or 0
        
        # This month
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        month_costs = self.get_costs_by_period(month_start, now)
        month_total = sum(cost.cost_amount for cost in month_costs)
        
        # Today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_costs = self.get_costs_by_period(today_start, now)
        today_total = sum(cost.cost_amount for cost in today_costs)
        
        # Top services
        service_query = self.db.query(
            CostEntry.service,
            func.sum(CostEntry.cost_amount).label('total')
        ).group_by(CostEntry.service).order_by(func.sum(CostEntry.cost_amount).desc()).limit(5)
        
        top_services = [
            {'service': row.service, 'total_cost': float(row.total)}
            for row in service_query.all()
        ]
        
        return {
            'total_cost': float(total_cost),
            'month_total': float(month_total),
            'today_total': float(today_total),
            'top_services': top_services
        }
    
    async def log_openai_cost(
        self,
        model: str,
        tokens_used: int,
        cost_per_token: float,
        job_id: Optional[str] = None,
        operation: str = "text-generation"
    ) -> CostEntry:
        """Helper method to log OpenAI API costs."""
        cost_amount = tokens_used * cost_per_token
        
        return await self.log_cost(
            service="openai",
            operation=f"{model}-{operation}",
            cost_amount=cost_amount,
            job_id=job_id,
            tokens_used=tokens_used,
            requests_count=1,
            description=f"OpenAI {model} API call",
            extra_data={
                "model": model,
                "cost_per_token": cost_per_token
            }
        )
    
    async def log_crawling_cost(
        self,
        pages_crawled: int,
        cost_per_page: float,
        job_id: Optional[str] = None,
        data_size_mb: Optional[float] = None
    ) -> CostEntry:
        """Helper method to log web crawling costs."""
        cost_amount = pages_crawled * cost_per_page
        
        return await self.log_cost(
            service="crawling",
            operation="web-crawl",
            cost_amount=cost_amount,
            job_id=job_id,
            requests_count=pages_crawled,
            data_processed_mb=data_size_mb,
            description=f"Crawled {pages_crawled} pages",
            extra_data={
                "pages_crawled": pages_crawled,
                "cost_per_page": cost_per_page
            }
        )


def get_cost_tracking_service(db: Session = Depends(get_db)) -> CostTrackingService:
    """Get cost tracking service instance."""
    return CostTrackingService(db)

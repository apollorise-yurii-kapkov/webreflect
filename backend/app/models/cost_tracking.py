from sqlalchemy import Column, String, Float, DateTime, Text, Integer, Uuid
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class CostEntry(Base):
    """Model for tracking operational costs and expenses."""
    __tablename__ = "cost_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service = Column(String(100), nullable=False, index=True)  # e.g., "openai", "crawl4ai", "redis", "postgres"
    operation = Column(String(100), nullable=False)  # e.g., "gpt-4-analysis", "website-crawl", "storage"
    cost_amount = Column(Float, nullable=False)  # Cost in USD
    currency = Column(String(3), nullable=False, default="USD")
    
    # Usage metrics
    tokens_used = Column(Integer, nullable=True)  # For AI services
    requests_count = Column(Integer, nullable=True)  # Number of API calls
    data_processed_mb = Column(Float, nullable=True)  # Amount of data processed
    
    # Context
    job_id = Column(String(36), nullable=True, index=True)  # Link to analysis job
    description = Column(Text, nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    occurred_at = Column(DateTime(timezone=True), nullable=True)  # When the cost was incurred

    def __repr__(self):
        return f"<CostEntry(service='{self.service}', operation='{self.operation}', cost=${self.cost_amount})>"


class CostSummary(Base):
    """Model for storing daily/monthly cost summaries."""
    __tablename__ = "cost_summaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    period_type = Column(String(20), nullable=False)  # "daily", "monthly", "yearly"
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    total_cost = Column(Float, nullable=False, default=0.0)
    service_breakdown = Column(Text, nullable=True)  # JSON string with per-service costs
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<CostSummary(period='{self.period_type}', total=${self.total_cost})>"

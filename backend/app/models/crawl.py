from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class CrawledPage(Base):
    """Crawled page model."""
    
    __tablename__ = "crawled_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(2048), nullable=False)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    meta_description = Column(Text, nullable=True)
    h1_tags = Column(ARRAY(Text), nullable=True)
    cta_texts = Column(ARRAY(Text), nullable=True)
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("AnalysisJob", back_populates="pages")

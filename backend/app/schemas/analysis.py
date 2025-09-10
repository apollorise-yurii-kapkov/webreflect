from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from uuid import UUID


class AnalysisRequest(BaseModel):
    """Request schema for website analysis."""
    url: HttpUrl = Field(..., description="Website URL to analyze")


class AnalysisJobResponse(BaseModel):
    """Response schema for analysis job creation."""
    job_id: UUID
    url: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessagingScores(BaseModel):
    """Messaging analysis scores."""
    clarity: int = Field(..., ge=0, le=100, description="Message clarity score")
    consistency: int = Field(..., ge=0, le=100, description="Message consistency score")
    differentiation: int = Field(..., ge=0, le=100, description="Differentiation score")
    proof: int = Field(..., ge=0, le=100, description="Social proof score")
    cta_strength: int = Field(..., ge=0, le=100, description="CTA effectiveness score")
    audience_fit: int = Field(..., ge=0, le=100, description="Target audience fit score")
    overall: int = Field(..., ge=0, le=100, description="Overall messaging score")


class MessagingAnalysis(BaseModel):
    """Detailed messaging analysis."""
    primary_message: str = Field(..., description="Main message the site conveys")
    target_audience: str = Field(..., description="Identified target audience")
    value_proposition: str = Field(..., description="Core value proposition")
    tone_and_voice: str = Field(..., description="Brand tone and voice analysis")
    key_themes: List[str] = Field(..., description="Main themes and topics")
    strengths: List[str] = Field(..., description="Messaging strengths")
    weaknesses: List[str] = Field(..., description="Areas for improvement")


class AnalysisResultResponse(BaseModel):
    """Complete analysis result response."""
    job_id: UUID
    url: str
    status: str
    content_summary: Optional[str] = None
    messaging_analysis: Optional[MessagingAnalysis] = None
    scores: Optional[MessagingScores] = None
    quick_wins: Optional[List[str]] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class CrawledPageResponse(BaseModel):
    """Crawled page response schema."""
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_tags: Optional[List[str]] = None
    cta_texts: Optional[List[str]] = None
    crawled_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisStatusResponse(BaseModel):
    """Analysis job status response."""
    job_id: UUID
    url: str
    status: str
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

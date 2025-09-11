from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    PROJECT_NAME: str = "Website Reflection"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/website_reflection"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Basic Auth for API protection
    API_USERNAME: str = "admin"
    API_PASSWORD: str = "secure_password_2024"
    
    # CORS - restrict to frontend domain only
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-frontend-domain.com",  # Add production frontend domain
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Crawling settings
    MAX_PAGES_PER_SITE: int = 30
    CRAWL_TIMEOUT: int = 30
    MAX_CONTENT_LENGTH: int = 50000
    
    # AI Analysis settings
    MAX_TOKENS_PER_ANALYSIS: int = 4000
    ANALYSIS_MODEL: str = "gpt-5-nano"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

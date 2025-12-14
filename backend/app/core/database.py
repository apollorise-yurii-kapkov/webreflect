from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Import all models to register them
        from app.models import analysis, crawl
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

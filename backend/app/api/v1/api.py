from fastapi import APIRouter

from app.api.v1.endpoints import analysis, costs, limits

api_router = APIRouter()

api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(costs.router, prefix="/costs", tags=["costs"])
api_router.include_router(limits.router, prefix="/limits", tags=["limits"])

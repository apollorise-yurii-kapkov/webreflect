from fastapi import APIRouter

from app.api.v1.endpoints import analysis, costs

api_router = APIRouter()

api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(costs.router, prefix="/costs", tags=["costs"])

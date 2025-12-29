from fastapi import APIRouter, Depends, Request
from app.core.config import settings

router = APIRouter()

@router.get("/status")
async def get_limit_status(request: Request):
    """Get daily limit status for the current user."""
    # This logic mirrors the middleware check
    daily_limit = 10  # Hardcoded in middleware
    cookie_name = "wr_daily_requests"
    
    count = 0
    
    cookie_value = request.cookies.get(cookie_name)
    if cookie_value:
        try:
            parts = cookie_value.split(":")
            if len(parts) == 2:
                count = int(parts[0])
                # Check if reset needed (would be handled by middleware on next request anyway)
                # But for display purposes, we can trust the cookie count roughly
        except:
            pass
            
    remaining = max(0, daily_limit - count)
    
    return {
        "limit": daily_limit,
        "used": count,
        "remaining": remaining
    }

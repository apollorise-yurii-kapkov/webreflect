import time
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from app.core.config import settings


class DailyLimitMiddleware:
    """Rate limiting middleware based on cookies - 10 requests per day per device."""
    
    COOKIE_NAME = "wr_daily_requests"
    MAX_REQUESTS_PER_DAY = 10
    DAY_IN_SECONDS = 86400  # 24 hours
    
    def __init__(self):
        pass
    
    def _get_cookie_value(self, request: Request) -> Optional[str]:
        """Get daily requests cookie value."""
        return request.cookies.get(self.COOKIE_NAME)
    
    def _parse_cookie(self, cookie_value: str) -> tuple[int, float]:
        """Parse cookie value: count,reset_timestamp."""
        try:
            parts = cookie_value.split(":")
            if len(parts) == 2:
                count = int(parts[0])
                reset_timestamp = float(parts[1])
                return count, reset_timestamp
        except (ValueError, IndexError):
            pass
        return 0, time.time()
    
    def _create_cookie_value(self, count: int, reset_timestamp: float) -> str:
        """Create cookie value string."""
        return f"{count}:{reset_timestamp}"
    
    def _should_reset(self, reset_timestamp: float) -> bool:
        """Check if daily limit should be reset."""
        current_time = time.time()
        return current_time >= reset_timestamp
    
    def _get_reset_timestamp(self) -> float:
        """Get timestamp for next day reset (midnight UTC)."""
        now = datetime.utcnow()
        # Reset at next midnight UTC
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return next_midnight.timestamp()
    
    async def __call__(self, request: Request, call_next):
        """Daily limit middleware - only applies to POST /api/v1/analysis/reflect."""
        # Skip for health checks and other endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Only apply to the POST /api/v1/analysis/reflect endpoint
        if request.method != "POST" or "/analysis/reflect" not in str(request.url.path):
            return await call_next(request)
        
        cookie_value = self._get_cookie_value(request)
        current_time = time.time()
        
        # Initialize or parse cookie
        if cookie_value:
            count, reset_timestamp = self._parse_cookie(cookie_value)
            
            # Reset if day has passed
            if self._should_reset(reset_timestamp):
                count = 0
                reset_timestamp = self._get_reset_timestamp()
        else:
            count = 0
            reset_timestamp = self._get_reset_timestamp()
        
        # Check limit
        if count >= self.MAX_REQUESTS_PER_DAY:
            remaining_seconds = int(reset_timestamp - current_time)
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Daily limit exceeded. You can make {self.MAX_REQUESTS_PER_DAY} requests per day. Please try again later.",
                    "limit": self.MAX_REQUESTS_PER_DAY,
                    "retry_after_seconds": remaining_seconds,
                    "retry_after_human": f"{hours}h {minutes}m"
                }
            )
            # Set cookie even on limit exceeded to track reset time
            new_cookie_value = self._create_cookie_value(count, reset_timestamp)
            # Determine if we're in production (HTTPS)
            is_production = any("https://" in str(origin) for origin in settings.BACKEND_CORS_ORIGINS)
            response.set_cookie(
                key=self.COOKIE_NAME,
                value=new_cookie_value,
                max_age=self.DAY_IN_SECONDS,
                httponly=True,
                samesite="lax",
                secure=is_production
            )
            return response
        
        # Increment count
        count += 1
        new_cookie_value = self._create_cookie_value(count, reset_timestamp)
        
        # Process request
        response = await call_next(request)
        
        # Set/update cookie in response
        # Determine if we're in production (HTTPS)
        is_production = any("https://" in str(origin) for origin in settings.BACKEND_CORS_ORIGINS)
        response.set_cookie(
            key=self.COOKIE_NAME,
            value=new_cookie_value,
            max_age=self.DAY_IN_SECONDS,
            httponly=True,
            samesite="lax",
            secure=is_production
        )
        
        # Add headers for client info
        response.headers["X-RateLimit-Limit"] = str(self.MAX_REQUESTS_PER_DAY)
        response.headers["X-RateLimit-Remaining"] = str(self.MAX_REQUESTS_PER_DAY - count)
        response.headers["X-RateLimit-Reset"] = str(int(reset_timestamp))
        
        return response


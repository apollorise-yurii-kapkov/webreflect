import time
from typing import Dict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import asyncio

class RateLimitMiddleware:
    """Simple in-memory rate limiting middleware."""
    
    def __init__(self, calls: int = 100, period: int = 30):
        self.calls = calls  # Max calls per period
        self.period = period  # Period in seconds
        self.clients: Dict[str, Dict] = {}
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory leak."""
        current_time = time.time()
        to_remove = []
        
        for ip, data in self.clients.items():
            if current_time - data.get("first_request", 0) > self.period * 2:
                to_remove.append(ip)
        
        for ip in to_remove:
            del self.clients[ip]
    
    async def __call__(self, request: Request, call_next):
        """Rate limiting middleware."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
    #     client_ip = self._get_client_ip(request)
    #     current_time = time.time()
        
    #     # Initialize client data if not exists
    #     if client_ip not in self.clients:
    #         self.clients[client_ip] = {
    #             "count": 0,
    #             "first_request": current_time,
    #             "last_request": current_time
    #         }
        
    #     client_data = self.clients[client_ip]
        
    #     # Reset counter if period has passed
    #     if current_time - client_data["first_request"] > self.period:
    #         client_data["count"] = 0
    #         client_data["first_request"] = current_time
        
    #     # Check rate limit
    #     if client_data["count"] >= self.calls:
    #         return JSONResponse(
    #             status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    #             content={
    #                 "detail": f"Rate limit exceeded. Max {self.calls} requests per {self.period} seconds.",
    #                 "retry_after": self.period - (current_time - client_data["first_request"])
    #             }
    #         )
        
    #     # Increment counter
    #     client_data["count"] += 1
    #     client_data["last_request"] = current_time
        
    #     # Cleanup old entries periodically
    #     if len(self.clients) > 1000:  # Cleanup when too many entries
    #         self._cleanup_old_entries()
        
        return await call_next(request)

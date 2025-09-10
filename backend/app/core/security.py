import secrets
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.core.config import settings

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify basic auth credentials."""
    correct_username = secrets.compare_digest(credentials.username, settings.API_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.API_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def get_current_user(username: str = Depends(verify_credentials)) -> str:
    """Get current authenticated user."""
    return username

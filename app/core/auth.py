from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name=settings.API_KEY, auto_error=True)

def authenticate(api_key: str = Depends(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )
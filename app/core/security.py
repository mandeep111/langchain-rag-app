from fastapi import Header, HTTPException, status
from typing import Optional
from app.core.config import settings

async def get_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key")
    if x_api_key not in settings.API_KEYS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return x_api_key

from fastapi import APIRouter, status
from pydantic import BaseModel
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("health_api")

router = APIRouter(tags=["Health"])

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    service_name: str


@router.get("/check", response_model=HealthResponse)
@router.head("/check")
async def health_check():
    """
    Perform a health check.
    
    Returns:
        HealthResponse: Health check response
    """
    logger.debug("Health check requested")
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        service_name=settings.APP_NAME
    )
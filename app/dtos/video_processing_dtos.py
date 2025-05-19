from app.dtos.error_success_code import ErrorAndSuccessCodes

from pydantic import BaseModel
from typing import Optional


class VideoProcessingResponse(BaseModel):
    """Video Processing response."""
    status : str
    task_id: Optional[str] = None
    internal_status_code : Optional[ErrorAndSuccessCodes] = None
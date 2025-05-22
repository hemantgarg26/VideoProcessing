from app.dtos.error_success_code import ErrorAndSuccessCodes

from pydantic import BaseModel
from typing import Optional, List


class VideoProcessingResponse(BaseModel):
    """Video Processing response."""
    status : str
    task_id: Optional[str] = None
    internal_status_code : Optional[ErrorAndSuccessCodes] = None

class TaskList(BaseModel):
    """Get Video Tasks"""
    status : str
    output: Optional[str] = None
    thumbnail : Optional[str] = None

class GetVideoTasksResponse(BaseModel): 
    status : str
    data : List[TaskList]

class GetTaskDetailsResponse(BaseModel):
    status : str
    detail : Optional[str] = None


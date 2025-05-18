from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import Annotated
from api.dtos.error_success_codes import ErrorAndSuccessCodes


class VideoProcessingResponse(BaseModel):
    """Video Processing response."""
    status : str
    task_id: str
    internal_status_code : ErrorAndSuccessCodes

class VideoProcessingRequest(BaseModel):
    """Video Processing Reques."""
    user_id : str
    video_file: Annotated[UploadFile, File(...)]
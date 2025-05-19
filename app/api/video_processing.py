from fastapi import APIRouter, UploadFile, Form, File
from pydantic import BaseModel
from app.core.config import settings
from app.utils.logger import get_logger
from app.dtos.video_processing_dtos import VideoProcessingResponse
from app.core.video_processing_service import process_video

logger = get_logger("video_processing")

router = APIRouter(tags=["VideoProcessing"])


@router.post("/upload", response_model=VideoProcessingResponse)
@router.head("/upload")
async def video_processing_route(user_id : str = Form(...), video_file : UploadFile = File(...)):
    """
    Uploads a video file for processing.
    Returns:
        VideoProcessingResponse: task_id to fetch the status
    """
    logger.info(f"Video Upload requested, User ID: {user_id}, File Name: {video_file.filename}")
    video_process_input = {
        'user_id': user_id,
        'video_file': video_file
    }
    result = await process_video(video_process_input)
    
    if result.get('task_id') is None:
        return VideoProcessingResponse(
            status="error",
            internal_status_code=result.get('status'),
        )
    else:
        return VideoProcessingResponse(
            status="ok",
            task_id=result.get('task_id'),
            internal_status_code=result.get('status'),
        )
from fastapi import APIRouter, status
from pydantic import BaseModel
from app.core.config import settings
from app.utils.logger import get_logger
from app.dtos.video_processing_dtos import VideoProcessingResponse, VideoProcessingRequest
from app.core.video_processing_service import process_video

logger = get_logger("video_processing")

router = APIRouter(tags=["VideoProcessing"])


@router.get("/upload", response_model=VideoProcessingResponse)
@router.head("/upload")
async def video_processing_route(input : VideoProcessingRequest):
    """
    Uploads a video file for processing.
    Returns:
        VideoProcessingResponse: task_id to fetch the status
    """
    logger.info("Video Upload requested")
    result = await process_video(input)
    
    if result.get('task_id') is None:
        return VideoProcessingResponse(
            status="error",
            internal_status_code=result,
        )
    else:
        return VideoProcessingResponse(
            status="ok",
            task_id=result.get('task_id'),
            internal_status_code=result.get('status'),
        )
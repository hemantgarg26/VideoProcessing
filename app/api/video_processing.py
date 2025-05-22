from app.core.config import settings
from app.utils.logger import get_logger
from app.dtos.video_processing_dtos import VideoProcessingResponse, GetVideoTasksResponse, TaskList, GetTaskDetailsResponse
from app.core.video_processing_service import process_video, get_tasks, get_task_details

from fastapi import APIRouter, UploadFile, Form, File, Query, Path
from typing import List, Optional
import psutil

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
    
@router.get("/tasks", response_model=GetVideoTasksResponse)
async def get_tasks_list(user_id : str = Query(...), task_id: Optional[str] = Query(None)):
    '''
        Fetches tasks from DB
        if task_id : then fetch only that task
        else fetch all tasks for that user
    '''
    logger.info(f"Tasks requested, User ID: {user_id}, Task ID: {task_id}")
    result : List[TaskList] = await get_tasks(user_id, task_id)
    return GetVideoTasksResponse(
        status="ok",
        data=result
    )

@router.get("/task", response_model = GetTaskDetailsResponse)
async def get_video_details(task_id: str = Query(...), type : str  = Query(...)):
    '''
        Fetches Thumbnail for the task
    '''
    logger.info(f"Tasks Details requested, Task ID: {task_id}, Type : {type}")
    result = await get_task_details(task_id, type)
    return GetTaskDetailsResponse(
        status = "ok",
        detail = result
    )

@router.get("/analytics/queue")
async def get_queue_details():
    '''
        Returns the local host command and port for running the flower dashboard
    '''
    return "Start Flower by running command in a different Terminal : celery -A app.core.worker.celery flower --port=5555\n and the got to http://localhost:5555/ \n\n"

@router.get("/analytics/system")
async def get_system_analytics():
    '''
        Returns System Analytics
    '''

    # CPU metrics
    return {
        "cpu_percent" : psutil.cpu_percent(interval=1),
        "cpu_count" : psutil.cpu_count(),
        "cpu_times" : psutil.cpu_times(),
        "memory" : psutil.virtual_memory(),
        "swap_memory" : psutil.swap_memory(),
        "disk_usage" : psutil.disk_usage('/'),
        "disk_io_counters" : psutil.disk_io_counters(),
        "net_io_counters" : psutil.net_io_counters()
    }
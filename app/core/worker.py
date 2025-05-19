from app.core.config import settings

from celery import Celery
from celery.result import AsyncResult

celery = Celery(
    'worker',
    broker=settings.BROKER_URL,
    backend=settings.BACKEND_URL
)

@celery.task
def process_video_task(task_id : str):
    '''
        1. Download video from S3
        2. Process Video via ffmpeg
        3. Upload this video and thumbnail to S3
        4. Store the S3 URLs of the processed video and thumbnail in the database
        5. Update the task status in the database
    '''
    return "Complete"

'''
    Fetch Status of task
'''
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result
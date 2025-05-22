from app.core.config import settings
from app.utils.logger import get_logger
from app.utils.db_connect import mongodb
from app.core.celery_core import process_video_inside_task_queue

from celery import Celery
from celery.result import AsyncResult
from celery.signals import worker_process_init
import asyncio

logger = get_logger("worker")

celery = Celery(
    'worker',
    broker=settings.BROKER_URL,
    backend=settings.BACKEND_URL
)

logger.info("Starting DB Connection in Celery Tasks")
'''
    Used To Connect Mongo in Celery Tasks
    Celery is Synchronous by default and therefore has to use asyncio
    In FastAPI the async-await uses asyncio under the hood, but is managed by uvicorn

    Will be called when Celery App is started
'''
@worker_process_init.connect
def init_worker(**kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(mongodb.connect())
logger.info("DB Connected in Celery Tasks")

@celery.task
def process_video_task(task_id : str):
    async def safe_wrapper():
        return await process_video_inside_task_queue(task_id)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already running (e.g., inside a thread, Jupyter), create a new one
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(safe_wrapper())
        else:
            return loop.run_until_complete(safe_wrapper())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(safe_wrapper())

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
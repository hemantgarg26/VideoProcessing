from app.utils.request_validations import validate_rate_limit, validate_file_type
from app.dtos.error_success_code import ErrorAndSuccessCodes
from app.dtos.collection_names import CollectionNames
from app.utils.db_query import MongoQueryApplicator
from app.constants.video_constants import VideoStatus
from app.utils.s3_utils import upload_video_to_s3
from app.core.worker import process_video_task
from app.utils.logger import get_logger
from app.dtos.video_processing_dtos import TaskList

from datetime import datetime
from bson import ObjectId
from typing import List

logger = get_logger("video_processing")

'''
    Implementation for Celery Task Queue
'''
class CeleryTaskQueue:
    def process_video(self, task_id):
        return process_video_task.delay(task_id)
    
async def process_video(input) -> dict:
    """
    Process the video file and return the task ID.
    
    Args:
        input ({user_id : str, video_file : UploadFile}): The video processing request containing user ID and video file.
    
    Processing Steps : 
    1. Validates if there is limit available at the global level to upload the file (Rate Limiting : Check 1)
    2. Validates if the user has the limits available to upload the file (Rate Limiting : Check 2)
    4. Validates File (Type, Size etc)
    4. Creates as record in the database to store the video file (Gets the task_id) 
    5. Upload File to S3
    6. Update the status in task record in the database, return the task_id
    7. Start Async processing for file
    
    Returns:
        str: The task ID for tracking the processing status.
    """
    mongo = None
    task_id = None

    try:
        # Rate Limit Validation
        rate_limit_check = await validate_rate_limit(input.get('user_id'))
        logger.info(f"Rate Limit Check : {rate_limit_check.value}")
        if rate_limit_check != ErrorAndSuccessCodes.SUCCESS:
            return {
                'status': rate_limit_check
            }
        
        # File Type Validation
        file_type_check = validate_file_type(input.get('video_file'))
        if file_type_check != ErrorAndSuccessCodes.SUCCESS:
            return {
                'status': file_type_check
            }
        
        # Mongo Record Creation
        mongo = MongoQueryApplicator(CollectionNames.VIDEOS.value)
        task_id = await mongo.insert_one({
            'user_id': input.get('user_id'),
            'status': VideoStatus.SAVED.value,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        })

        '''
            NOTE : When we have a client, the flow can start as async from here
            Since we are not having a client and only a backend system, we will upload the file in sync, and send the task_id for further processing in async
        '''
        # Upload File to S3
        s3_url = await upload_video_to_s3(input.get('video_file'))

        await mongo.update_one(
            {"_id" :ObjectId(task_id)},
            {
                's3_url' : s3_url,
                'status' : VideoStatus.PROCESSING.value,
                'updated_at' : datetime.now()
            }
        )

        '''
            Push to Celery for processing
            Returns a task_id
        '''
        CeleryTaskQueue().process_video(task_id)
        
        return {
            'task_id': task_id,
            'status' : ErrorAndSuccessCodes.SUCCESS
        }
    except Exception as e:
        logger.error(f"Error while processing Video : {e}")
        if mongo and task_id:
            await mongo.update_one(
                {"_id" :ObjectId(task_id)},
                {
                    'status' : VideoStatus.FAILED.value,
                }
        )
        return {
            'status' : ErrorAndSuccessCodes.PROCESSING_ERROR
        }
    

async def get_tasks(user_id, task_id) -> List[TaskList]: 
    try:
        query = {"user_id" : user_id}
        if task_id:
            query["_id"] = ObjectId(task_id)
        mongo = MongoQueryApplicator(CollectionNames.VIDEOS.value)
        tasks = await mongo.find(query)

        if not tasks or len(tasks) == 0:
            logger.info(f"No Tasks Found User Id : {user_id}")
            return []
        
        res : List[TaskList] = []
        for v in tasks:
            task : TaskList = {
                'status' : v.get('status'),
                'thumbnail' : v.get('thumbnail'),
                'output' : v.get('output_video'),
            }
            res.append(task)
        return res
    except Exception as e:
        logger.error(f"Error while fetching task : {e}, USER ID: {user_id}, TASK ID: {task_id}")
        return []
    
async def get_task_details(task_id : str, type : str) -> str: 
    try:
        query = {"_id" : ObjectId(task_id)}
        mongo = MongoQueryApplicator(CollectionNames.VIDEOS.value)
        task = await mongo.find_one(query)

        if not task:
            logger.info(f"No Tasks Found Task Id : {task_id}")
            return ""
        
        if type == "thumbnail":
            return task.get('thumbnail') or ""
        elif type == "progress":
            return task.get('status') or ""
        else:
            return ""
    except Exception as e:
        logger.error(f"Error while fetching task details : {e}, TASK ID: {task_id}")
        return ""
    
    
    

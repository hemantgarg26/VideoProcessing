from app.utils.request_validations import validate_rate_limit, validate_file_type
from app.dtos.error_success_code import ErrorAndSuccessCodes
from app.dtos.collection_names import CollectionNames
from app.utils.db_query import MongoQueryApplicator
from app.constants.video_constants import VideoStatus
from app.utils.s3_utils import upload_video_to_s3
from app.core.worker import process_video_task
from app.utils.logger import get_logger

from datetime import datetime
from bson import ObjectId

logger = get_logger("video_processing")

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

        '''
            Push to Celery for processing
        '''
        task = CeleryTaskQueue().process_video(task_id)
        
        mongo_res = await mongo.find_one({"_id" : ObjectId(task_id)})
        print(mongo_res, "Mongo Result")

        await mongo.update_one(
            {"_id" :ObjectId(task_id)},
            {
                's3_url' : s3_url,
                'status' : VideoStatus.PROCESSING.value,
                'task_queue_id' : task.id,
                'updated_at' : datetime.now()
            }
        )

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


'''
    Implementation for Celery Task Queue
'''
class CeleryTaskQueue:
    def process_video(self, task_id):
        return process_video_task.delay(task_id)
    
    
    

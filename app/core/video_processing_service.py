from app.dto.video_processing_dtos import VideoProcessingRequest
from app.utils.request_validations import validate_rate_limit, validate_file_type
from app.dtos.error_success_code import ErrorAndSuccessCodes
from app.dtos.collection_names import CollectionNames
from app.utils.db_query import MongoQueryApplicator
from app.constant.video_constants import VideoStatus
from app.utils.s3_utils import upload_video_to_s3
from app.tasks.celery_tasks import process_video_task

from datetime import datetime

async def process_video(input : VideoProcessingRequest):
    """
    Process the video file and return the task ID.
    
    Args:
        input (VideoProcessingRequest): The video processing request containing user ID and video file.
    
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
    
    # Rate Limit Validation
    rate_limit_check = validate_rate_limit(input.get('user_id'))
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
    mongo = MongoQueryApplicator(CollectionNames.VIDEOS)
    task_id = await mongo.insert_one({
        'user_id': input.get('user_id'),
        'status': VideoStatus.SAVED,
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
    task = CeleryTaskQueue(task_id)
    
    mongo.find_one_and_update(
        {"_id" :task_id},
        {
            "$set" : {
                's3_url' : s3_url,
                'status' : VideoStatus.PROCESSING,
                'task_queue_id' : task.id,
                'updated_at' : datetime.now()
            }
        }
    )

    return {
        'task_id': task_id,
        'status' : ErrorAndSuccessCodes.SUCCESS
    }


'''
    Implementation for Celery Task Queue
'''
class CeleryTaskQueue:
    def process_video(self, task_id):
        return process_video_task.delay(task_id)
    
    
    

from fastapi import File, UploadFile
from app.dtos.error_success_code import ErrorAndSuccessCodes
from app.dtos.collection_names import CollectionNames
from datetime import datetime
from app.utils.db_query import MongoQueryApplicator
from app.core.config import settings


async def validate_rate_limit(user_id : str) -> ErrorAndSuccessCodes:
    """
        Validate the rate limit for the incoming request.
        This function checks if the request exceeds the allowed rate limit.
        To save DB calls we are fetching all the records and filtering for that user
    """
    # Placeholder for actual rate limiting logic
    # For example, check if the request is within the allowed number of requests per minute
    # If it exceeds, raise an exception or return an error response
    start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    # Check the number of files created today, if it exceeds the limit, return error
    mongo = MongoQueryApplicator(CollectionNames.VIDEOS.value)
    
    # Build your query dict dynamically
    videos = await mongo.find({"created_at" : {"$gte" : start_of_day, "$lte" : end_of_date}})
    if videos and len(videos) >= settings.GLOBAL_VIDEO_RATE_LIMITING:
        return ErrorAndSuccessCodes.GLOBAL_RATE_LIMIT_EXHAUSTED
    
    user_videos = []
    for video in videos:
        if video.get('user_id') == user_id:  # Not using video['user_id'] to avoid KeyError
            user_videos.append(video)
    
    if len(user_videos) >= settings.USER_VIDEO_RATE_LIMITING:
        return ErrorAndSuccessCodes.USER_RATE_LIMIT_EXHAUSTED

    return ErrorAndSuccessCodes.SUCCESS
    

def validate_file_type(video_file:UploadFile = File(...)) -> ErrorAndSuccessCodes:
    """
    Validate the file type of the uploaded video.
    This function checks if the file type is allowed.
    """
    allowed_types = [
        "video/mp4",        # MP4
        "video/x-msvideo",  # AVI
        "video/quicktime",  # MOV
        "video/x-ms-wmv",   # WMV
        "video/x-flv"       # FLV
        ]
    if video_file.content_type not in allowed_types:
        return ErrorAndSuccessCodes.NOT_SUPPORTED_FILE_TYPE
    return ErrorAndSuccessCodes.SUCCESS
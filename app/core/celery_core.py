from app.dtos.collection_names import CollectionNames
from app.utils.db_query import MongoQueryApplicator
from app.constants.video_constants import VideoStatus
from app.utils.s3_utils import download_file, upload_file_to_s3_from_path
from app.utils.logger import get_logger
from app.utils.file_processing_utils import convert_to_mp4, extract_thumbnail

from datetime import datetime
from bson import ObjectId
import os
import shutil

logger = get_logger("celery_core")

async def process_video_inside_task_queue(task_id : str):
    '''
        1. Fetch Record from DB
        2. Download video from S3
        3. Process Video via ffmpeg
        4. Upload this video and thumbnail to S3
        5. Store the S3 URLs of the processed video and thumbnail in the database
        6. Update the task status in the database
    '''
    local_path = None
    try:
        logger.info(f"Starting Processing Video Task : {task_id}")

        # Fetch Record From DB
        mongo = MongoQueryApplicator(CollectionNames.VIDEOS.value)
        video_record = await mongo.find_one({"_id" : ObjectId(task_id)})
        logger.info(f"Video Record : {video_record}")
        if not video_record or not video_record.get("s3_url"):
            logger.error(f"Video Record Not Found in DB : {task_id}")
            return
        
        # Download File
        file_name = video_record.get("s3_url").split("/")[-1]
        local_path = f"{os.getcwd()}/{task_id}"
        output_file_name = f"output_{task_id}.mp4"
        thumbnail_file_name = f"thumbnail_{task_id}.jpeg"

        output_path = local_path + f"/{output_file_name}"
        thumbnail_output_path = local_path + f"/{thumbnail_file_name}"
        original_file_destination = local_path + f"/{file_name}"

        os.makedirs(local_path, exist_ok=True)
        logger.info(f"S3 URL : {video_record.get('s3_url')}") 
        download_file(video_record.get("s3_url"), original_file_destination)

        # Process Video
        convert_to_mp4(original_file_destination, output_path)
        converted_file_s3_url = ""
        if os.path.isfile(output_path):
            converted_file_s3_url = await upload_file_to_s3_from_path(output_path, output_file_name, "video/mp4")
            logger.info(f"File Conversion Success : S3 URL : {converted_file_s3_url}")

        # Gets Thumbnails
        extract_thumbnail(output_path, thumbnail_output_path)
        thumbnail_s3_url = ""
        if os.path.isfile(thumbnail_output_path):
            thumbnail_s3_url = await upload_file_to_s3_from_path(thumbnail_output_path, thumbnail_file_name, "image/jpeg")
            logger.info(f"Thumbnail Generation Success : S3 URL : {thumbnail_s3_url}")

        logger.info(f"Extracted URls : {thumbnail_s3_url}, {converted_file_s3_url}")
        await mongo.update_one(
            {"_id" :ObjectId(task_id)},
            {
                'status' : VideoStatus.PROCESSED.value,
                'updated_at' : datetime.now(),
                'output_video' : converted_file_s3_url,
                'thumbnail' : thumbnail_s3_url
            }
        )
        return "Complete"
    except Exception as e:
        logger.error(f"Error While Processing Video File : {e}")
        await mongo.update_one(
            {"_id" :ObjectId(task_id)},
            {
                'status' : VideoStatus.FAILED.value,
                'updated_at' : datetime.now()
            }
        )
    finally:
        if local_path and os.path.isdir(local_path):
            shutil.rmtree(local_path)
            logger.info(f"Successfully Deleted The Locally Created Files : {local_path}")
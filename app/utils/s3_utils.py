from fastapi import File, UploadFile
from app.dtos.error_success_code import ErrorAndSuccessCodes
from app.core.config import settings
from app.utils.logger import get_logger

import boto3
from botocore.exceptions import BotoCoreError, ClientError
logger = get_logger(__name__)

'''
    Uploading File to S3
'''
async def upload_video_to_s3(file : UploadFile = File(...)) -> str:
    s3_client = boto3.client(
        "s3",
        region_name = settings.S3_REGION
    )
    s3_key = f"videos/{file.filename}"

    '''
        Avoiding writing the video file to disk and directly uploading to S3
        This prevents the need for temporary storage and speeds up the process
        UploadFile.file supports directly streaming the file file to S3
    '''
    try:
        s3_client.upload_fileobj(
            file.file,
            settings.VIDEO_UPLOAD_S3_BUCKET,
            s3_key,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
        s3_url = f"https://{settings.VIDEO_UPLOAD_S3_BUCKET}.s3.{settings.S3_REGION}.amazonaws.com/{s3_key}"
        return s3_url

    except (BotoCoreError, ClientError) as e:
        raise Exception(f"S3 upload failed: {str(e)}")
    
'''
    Downloading File to a Local File in Python
'''
def download_file(s3_file_path: str, local_path: str):
    if not s3_file_path:
        logger.error(f"Missing S3 Path for File Download : {s3_file_path}")
        raise ValueError("S3 file path cannot be empty")

    s3_client = boto3.client(
        "s3",
        region_name=settings.S3_REGION
        # aws_access_key_id="your-access-key",
        # aws_secret_access_key="your-secret-key"
    )
    
    s3_key = s3_file_path.split(f"https://{settings.VIDEO_UPLOAD_S3_BUCKET}.s3.ap-south-1.amazonaws.com/")[-1]
    try:
        s3_client.download_file(settings.VIDEO_UPLOAD_S3_BUCKET, s3_key, local_path)
        logger.info(f"File downloaded to {local_path}")
    except Exception as e:
        logger.info(f"Download failed: {e}")

async def upload_file_to_s3_from_path(file_path: str, file_name: str, content_type : str) -> str:
    try:
        logger.info(f"Request Received to Upload File to S3 : {file_name}")
        s3_client = boto3.client(
            "s3",
            region_name = settings.S3_REGION
        )
        s3_key = f"videos/{file_name}"
        s3_client.upload_file(
            file_path,
            settings.VIDEO_UPLOAD_S3_BUCKET, 
            s3_key, 
            ExtraArgs={
                "ContentType": content_type
            }
        )
        s3_url = f"https://{settings.VIDEO_UPLOAD_S3_BUCKET}.s3.{settings.S3_REGION}.amazonaws.com/{s3_key}"
        return s3_url
    except Exception as e:
        logger.error(f"Upload to S3 failed: {e}")
        return ""
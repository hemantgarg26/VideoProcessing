from fastapi import File, UploadFile
from app.dtos.error_success_code import ErrorAndSuccessCodes
from app.core.config import settings

import boto3
from botocore.exceptions import BotoCoreError, ClientError

async def upload_video_to_s3(video_file : UploadFile = File(...)) -> str:
    s3_client = boto3.client(
        "s3",
        region_name = settings.S3_REGION
    )
    s3_key = f"videos/{video_file.filename}"

    '''
        Avoiding writing the video file to disk and directly uploading to S3
        This prevents the need for temporary storage and speeds up the process
        UploadFile.file supports directly streaming the file file to S3
    '''
    try:
        s3_client.upload_fileobj(
            video_file.file,
            settings.VIDEO_UPLOAD_S3_BUCKET,
            s3_key,
            ExtraArgs={
                "ContentType": video_file.content_type
            }
        )
        s3_url = f"https://{settings.VIDEO_UPLOAD_S3_BUCKET}.s3.{settings.S3_REGION}.amazonaws.com/{s3_key}"
        return s3_url

    except (BotoCoreError, ClientError) as e:
        raise Exception(f"S3 upload failed: {str(e)}")
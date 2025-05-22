from dotenv import load_dotenv, get_key
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """Application settings."""
    APP_NAME: str = "Video Processing"
    APP_VERSION: str = "0.1.0"
    MONGO_URI: str = get_key(".env", "MONGO_URI")
    MONGO_DB:str = get_key(".env", "MONGO_DB")
    GLOBAL_VIDEO_RATE_LIMITING: int = 100   # Per Day
    USER_VIDEO_RATE_LIMITING: int = 1 # Per Day

    # S3
    S3_REGION : str = get_key(".env", "S3_REGION")
    S3_ACCESS_KEY : str = get_key(".env", "S3_ACCESS_KEY")
    S3_SECRET_ACCESS_KEY : str = get_key(".env", "S3_SECRET_ACCESS_KEY")
    
    VIDEO_UPLOAD_S3_BUCKET : str = get_key(".env", "VIDEO_UPLOAD_S3_BUCKET")

    # Celery
    BROKER_URL : str = get_key(".env", "BROKER_URL")
    BACKEND_URL : str = get_key(".env", "BACKEND_URL") 

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a settings object
settings = Settings() 
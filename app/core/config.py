from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """Application settings."""
    APP_NAME: str = "Video Processing"
    APP_VERSION: str = "0.1.0"
    MONGO_URI: str
    MONGO_DB: str
    GLOBAL_VIDEO_RATE_LIMITING: int = 100   # Per Day
    USER_VIDEO_RATE_LIMITING: int = 1 # Per Day

    # S3
    S3_REGION : str
    S3_ACCESS_KEY : str
    S3_SECRET_ACCESS_KEY : str
    
    VIDEO_UPLOAD_S3_BUCKET : str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a settings object
settings = Settings() 
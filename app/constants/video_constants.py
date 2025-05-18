from enum import Enum
class VideoStatus(Enum):
    SAVED = "saved"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
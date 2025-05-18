from enum import Enum

class ErrorAndSuccessCodes(Enum):
    # 0xx: Success
    SUCCESS = 1

    # General Errors
    INVALID_INPUT = 2
    NOT_SUPPORTED_FILE_TYPE = 3
    FILE_UPLOAD_SIZE_EXCEEDED = 4
    GLOBAL_RATE_LIMIT_EXHAUSTED = 5
    USER_RATE_LIMIT_EXHAUSTED = 6

    # Processing Status
    FILE_UNDER_PROCESSING = 7
    FILE_PROCESSING_FAILED = 8
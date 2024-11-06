from enum import Enum

class ResponseSignal(Enum):

    SERVER_IS_DOWN = "Server is down"
    SERVER_IS_UP = "Server is up"

    ERROR_FILE_FORMAT_NOT_ALLOWED = "File format not supported"
    ERROR_FILE_MAX_SIZE_EXCEEDED = "File  max size exceeded"

    FILE_VALIDATION_SUCCESS = "File validation succeeded"
    FILE_VALIDATION_FAILED = "File validation failed"

    FILE_UPLOADED_SUCCESS = "File uploaded successfully"
    FILE_UPLOADED_FAILED = "File upload failed"
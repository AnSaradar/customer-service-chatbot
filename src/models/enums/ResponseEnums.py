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

    TEXT_EXTRACTATION_SUCCESS = "Text extraction succeeded"
    TEXT_EXTRACTATION_FAILED = "Text extraction failed"

    FILES_PROCESSING_SUCCESS = "Files processing succeeded"
    FILES_PROCESSING_FAILED = "Files processing failed"

    INVALID_CONFIGRATION_KEY = "Invalid configuration key"

    UPDATING_CONFIGURATION_SUCCESS = "Updating configuration succeeded"
    UPDATING_CONFIGURATION_FAILED = "Updating configuration failed"
    EMPTY_CONFIGUARTION_REQUEST = "Empty configuration request, Nothing changed"
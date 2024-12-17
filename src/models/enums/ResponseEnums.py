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

    PROJECT_NOT_FOUND = "Project not found"

    DATA_INDEXED_SUCCESS = "Data inserted to the VectorDB Successfully"
    DATA_INDEXED_FAILED = "Failed to insert data to the VectorDB"

    VECTORDB_COLLECTION_INFO_RETRIVED_SUCCESS = "VectorDB collection information was successfully retrieved"
    VECTORDB_COLLECTION_INFO_RETRIVED_FAILED = "Failed to retrieve VectorDB collection information"

    VECTORDB_COLLECTION_SEARCH_SUCCESS = "VectorDB collection search result was successfully retrieved"
    VECTORDB_COLLECTION_SEARCH_FAILED = "Failed to retrieve VectorDB collection search result"

    ANSWER_GENERATION_FAILED = "An error occurred while generating answer"
    ANSWER_GENERATION_SUCCESS = "Answer generated successfully"

    Project_ALREADY_EXISTS = "Project already exists"
    CREATE_PROJECT_FAILED = "Error while creating project"
    CREATE_PROJECT_SUCCESS = "Project created successfully"

    GETTING_CONFIGURATION_SUCCESS = "Configuration data retrieved successfully"
    GETTING_CONFIGURATION_FAILED = "Failed to retrieve configuration data"

    GETTING_PROJECT_FAILED = "Failed to retrieve project data"
    GETTING_PROJECT_SUCCESS = "Project retrieved successfully"
from .BaseController import BaseController
from fastapi import UploadFile
from models.enums import ResponseSignal

class DataController(BaseController):
    def __init__(self):
        super().__init__()
    
    def validate_uploaded_file(self, file: UploadFile):
        to_bytes_ratio = 1024 * 1024 
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.ERROR_FILE_FORMAT_NOT_ALLOWED.value
        
        if file.size > (self.app_settings.FILE_MAX_SIZE * to_bytes_ratio):
            return False, ResponseSignal.ERROR_FILE_MAX_SIZE_EXCEEDED.value
        
        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value
    

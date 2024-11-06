from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
import aiofiles
from models.enums import ResponseSignal
import logging

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}/")
async def upload_file(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):

    # Validate the uploaded file
    logger.info(f"Info from the Logger : Current file size :{file.size}")
    is_valid, response = DataController().validate_uploaded_file(file)

    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal":response})
    
    # Get The storing path for the uploaded file  
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path = os.path.join(project_dir_path,file.filename)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    
    except Exception as e:
        logger.error(f"Error while uploading file: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.FILE_UPLOADED_FAILED.value})
    

    return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value})
    

    




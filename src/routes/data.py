from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController, ProcessController
from models import ProjectModel , ChunkModel    
from models.db_schemes import DataChunk
from models.enums import ResponseSignal
from .requests_schemes import ProcessRequest
from bson import json_util
from helpers.config import get_settings, Settings
import aiofiles
import json
import os
import logging

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_file(request : Request, project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):

    project_model = ProjectModel(db_client = request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)


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
    

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
        "file_name": file.filename
    })



@data_router.post('/process/{project_id}/')
async def process_file(request : Request, project_id : str, process_request : ProcessRequest):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset


    process_controller = ProcessController(project_id=project_id)

    project_model = ProjectModel(db_client = request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id) # project : scheme

    chunk_model = ChunkModel(db_client = request.app.db_client)

    if do_reset == 1:
        _ = await chunk_model.delete_all_chunks_by_project_id(project_id=project.id)

    # # Get The storing path for the uploaded file  
    # project_dir_path = ProjectController().get_project_path(project_id=project_id)
    # logger.info(f"Info from the Logger : project_folder:{project_dir_path},{type(project_dir_path)}")
    # # Process all the files in the project folder
    # files_names = ProjectController().get_all_the_files_names_inside_folder(folder_path=project_dir_path)
    # all_files_contents = []
    # for file_name in files_names:
    #     file_content = process_controller.get_file_content(file_id=file_name)
    #     logger.info(f"Info from the Logger : file_content:{file_name},{type(file_content)}")
    #     chunks = process_controller.process_file_content(file_content=file_content,chunk_size=chunk_size,overlap_size=overlap_size)
    #     #logger.info(f"Info from the Logger : file_content:{chunks}")
    #     file_info = {'file_name': file_name, 'file_content': chunks}
    #     all_files_contents.append(file_info)


    file_content = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )
    
    if file_chunks is None or len(file_chunks) == 0 :

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "signal": ResponseSignal.FILES_PROCESSING_FAILED.value,
            })
    
    file_chunks_records = [
        DataChunk(
            chunk_text = chunk.page_content,
            chunk_metadata = chunk.metadata,
            chunk_order = i+1,
            chunk_project_id = project.id
        )

        for i , chunk in enumerate(file_chunks)
    ]
    
    
    num_records = await chunk_model.insert_many_chunks(chunks = file_chunks_records)


    return JSONResponse(status_code=status.HTTP_200_OK,content=
                        {"signal": ResponseSignal.FILES_PROCESSING_SUCCESS.value,
                        "Number of added chunks": json.loads(json_util.dumps(num_records))})

    




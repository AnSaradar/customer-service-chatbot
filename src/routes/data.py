from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request, Form
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController, ProcessController, NLPController
from models import ProjectModel , ChunkModel    
from models.db_schemes import DataChunkSchema
from models.enums import ResponseSignal
from .requests_schemes import ProcessRequest
from bson import json_util
from helpers.config import get_settings, Settings
import aiofiles
import json
import os
import logging

logger = logging.getLogger(__name__)

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload")
async def upload_file(request : Request, file: UploadFile, project_id: str = Form(...), app_settings: Settings = Depends(get_settings)):
    # TODO: Modify the code, so the "is_project_exist" method return the signal also 
    try:
        # Check if the Project exists
        project_model = ProjectModel(db_client = request.app.db_client)
        is_project_exist, company_schema = await project_model.is_project_exist(project_id = project_id)

        if is_project_exist == False or is_project_exist is None or company_schema is None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})

        # Validate the uploaded file
        logger.info(f"Info from the Logger : Current file size :{file.size}")
        is_valid, response = DataController().validate_uploaded_file(file)

        if not is_valid:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal":response})
        
        # Get The storing path for the uploaded file  
        project_dir_path = ProjectController().get_project_path(project_id=project_id)
        file_path = os.path.join(project_dir_path,file.filename)

        
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
        

        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
            "file_name": file.filename
        })
    
    except Exception as e:
        logger.error(f"Error while uploading file: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.FILE_UPLOADED_FAILED.value})



@data_router.post('/process')
async def process_file(request : Request, process_request : ProcessRequest):
    project_id = process_request.project_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    try:
        # Check if the Project exists
        project_model = ProjectModel(db_client = request.app.db_client)
        is_project_exist, project_schema = await project_model.is_project_exist(project_id = project_id)

        if is_project_exist == False or is_project_exist is None or project_schema is None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})
        


        process_controller = ProcessController(project_id=project_id)

        chunk_model = ChunkModel(db_client = request.app.db_client)

        if do_reset == 1:
            _ = await chunk_model.delete_all_chunks_by_project_id(project_id=project_schema.id)
    
        # Handle multiple files
        # Get The storing path for the uploaded file  
        project_dir_path = ProjectController().get_project_path(project_id=project_id)
        logger.info(f"project_folder:{project_dir_path}")
        # Process all the files in the project folder
        files_names = ProjectController().get_all_the_files_names_inside_folder(folder_path=project_dir_path)
        logger.info(f"All Files in project folder :{files_names}")
        
        all_files_chunks = []
        for file_name in files_names:
            file_content = process_controller.get_file_content(file_id=file_name)
            logger.info(f"Info from the Logger : file_content:{file_name},{type(file_content)}")
            chunks = process_controller.process_file_content(file_content=file_content,chunk_size=chunk_size,overlap_size=overlap_size)

            #logger.info(f"file_content:{chunks}")
            #logger.info(f"Chunks type:{type(chunks)}")
            #file_info = {'file_name': file_name, 'file_content': chunks}
            all_files_chunks.extend(chunks)


        # file_content = process_controller.get_file_content(file_id=file_id)
        # if file_content is None:
        #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
        #         "signal": ResponseSignal.FILES_PROCESSING_FAILED.value,
        #         })


        # file_chunks = process_controller.process_file_content(
        #     file_content=file_content,
        #     file_id=file_id,
        #     chunk_size=chunk_size,
        #     overlap_size=overlap_size
        # )
        
        if all_files_chunks is None or len(all_files_chunks) == 0 :

            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "signal": ResponseSignal.FILES_PROCESSING_FAILED.value,
                })
    
        file_chunks_records = [
            DataChunkSchema(
                chunk_text = chunk.page_content,
                chunk_metadata = chunk.metadata,
                chunk_order = i+1,
                chunk_project_id = project_schema.id
            )

            for i , chunk in enumerate(all_files_chunks)
        ]
        
        
        num_records = await chunk_model.insert_many_chunks(chunks = file_chunks_records)

        indexed_successfully, signal = await index_project(request = request, project_id = project_id, do_reset = do_reset)

        if indexed_successfully == False:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "signal": signal,
                })


        return JSONResponse(status_code=status.HTTP_200_OK,content=
                            {"signal": ResponseSignal.FILES_PROCESSING_SUCCESS.value,
                             "Number of processed files": len(files_names),
                            "Number of added chunks": json.loads(json_util.dumps(num_records))})
    
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "signal": ResponseSignal.FILES_PROCESSING_FAILED.value,
                })

    

async def index_project(request : Request, project_id : str, do_reset: int):

    try:

        project_model = ProjectModel(db_client = request.app.db_client)

        project_scheme = await project_model.get_project_or_create_one(project_id=project_id)

        if not project_scheme:
            return False, ResponseSignal.PROJECT_NOT_FOUND.value
            #return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})

        nlp_controller = NLPController(vectordb_client = request.app.vectordb_client,
                                    generation_client = request.app.generation_client,
                                    embedding_client = request.app.embedding_client,
                                    template_parser = request.app.template_parser,
                                    )
        
        chunk_model = ChunkModel(db_client = request.app.db_client) #Connect to Chunk Collection on mongo

    

        
        has_records = True
        page_no = 1
        inserted_items_count = 0
        idx = 0 # Records ID for VectorDB 

        while has_records:
            page_chunks = await chunk_model.get_all_chunks_by_project_id(project_id = project_scheme.id,page_no = page_no)
            logger.info(f"page_number:{page_no},page_chunks:{len(page_chunks)}")

            inserted_items_count += len(page_chunks)

            if len(page_chunks) > 0:
                page_no = page_no + 1
                #logger.info(f"Info from the Logger : New page_number:{page_no}")
            
            if not page_chunks or len(page_chunks) == 0:
                has_records = False
                break

            chunks_ids = list(range(idx, idx + len(page_chunks)))
            idx += len(page_chunks)

            is_inserted = nlp_controller.index_into_vector_db(
                project = project_scheme,
                chunks = page_chunks,
                chunks_ids = chunks_ids,
                do_reset = do_reset,
            )

            if not is_inserted:
                return False, ResponseSignal.DATA_INDEXED_FAILED.value
                #return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.DATA_INDEXED_FAILED.value})
            
        
        return True, ResponseSignal.DATA_INDEXED_SUCCESS.value
        # return JSONResponse(status_code=status.HTTP_200_OK,
        #                     content={"signal": ResponseSignal.DATA_INDEXED_SUCCESS.value,
        #                             "inserted_items_count": inserted_items_count})
    
    except Exception as e:
        logger.error(f"Error while indexing the project: {str(e)}")
        return False, ResponseSignal.DATA_INDEXED_FAILED.value
        #return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.DATA_INDEXED_FAILED.value})



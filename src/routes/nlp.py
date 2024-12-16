from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings, update_env_file_configuration
from controllers import NLPController, BaseController
from models import ProjectModel , ChunkModel, ConfigModel 
from models.enums import ResponseSignal
from .requests_schemes import IndexProjectRequest, IndexSearchRequest, InfoProjectRequest
import logging
from bson import json_util
import json

logger = logging.getLogger(__name__)

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

# @nlp_router.post("/index/push")
# async def index_project(request : Request, index_project_request : IndexProjectRequest):
#     project_id = index_project_request.project_id
#     do_reset = index_project_request.do_reset

#     try:

#         project_model = ProjectModel(db_client = request.app.db_client)

#         project_scheme = await project_model.get_project_or_create_one(project_id=project_id)

#         if not project_scheme:
#             return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})

#         nlp_controller = NLPController(vectordb_client = request.app.vectordb_client,
#                                     generation_client = request.app.generation_client,
#                                     embedding_client = request.app.embedding_client,
#                                     template_parser = request.app.template_parser,
#                                     )
        
#         chunk_model = ChunkModel(db_client = request.app.db_client) #Connect to Chunk Collection on mongo

    

        
#         has_records = True
#         page_no = 1
#         inserted_items_count = 0
#         idx = 0 # Records ID for VectorDB 

#         while has_records:
#             page_chunks = await chunk_model.get_all_chunks_by_project_id(project_id = project_scheme.id,page_no = page_no)
#             logger.info(f"Info from the Logger : page_number:{page_no},page_chunks:{len(page_chunks)}")

#             inserted_items_count += len(page_chunks)

#             if len(page_chunks) > 0:
#                 page_no = page_no + 1
#                 #logger.info(f"Info from the Logger : New page_number:{page_no}")
            
#             if not page_chunks or len(page_chunks) == 0:
#                 has_records = False
#                 break

#             chunks_ids = list(range(idx, idx + len(page_chunks)))
#             idx += len(page_chunks)

#             is_inserted = nlp_controller.index_into_vector_db(
#                 project = project_scheme,
#                 chunks = page_chunks,
#                 chunks_ids = chunks_ids,
#                 do_reset = index_project_request.do_reset,
#             )

#             if not is_inserted:
#                 return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.DATA_INDEXED_FAILED.value})
            
        
#         return JSONResponse(status_code=status.HTTP_200_OK,
#                             content={"signal": ResponseSignal.DATA_INDEXED_SUCCESS.value,
#                                     "inserted_items_count": inserted_items_count})
    
#     except Exception as e:
#         logger.error(f"Error while indexing the project: {str(e)}")
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.DATA_INDEXED_FAILED.value})



@nlp_router.get("/index/info")
async def get_project_index_info(request : Request, info_request: InfoProjectRequest):
    
    project_id = info_request.project_id

    try:
        # Check if the Project exists
        project_model = ProjectModel(db_client = request.app.db_client)
        is_project_exist, project_schema = await project_model.is_project_exist(project_id = project_id)

        if is_project_exist == False or is_project_exist is None or project_schema is None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})
        
        nlp_controller = NLPController(vectordb_client = request.app.vectordb_client,
                                    generation_client = request.app.generation_client,
                                    embedding_client = request.app.embedding_client,
                                    template_parser = request.app.template_parser,
                                    )
        
        collection_info = nlp_controller.get_vectordb_collection_info(
            project = project_schema,
        )

        if collection_info is None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.VECTORDB_COLLECTION_INFO_RETRIVED_FAILED.value})
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.VECTORDB_COLLECTION_INFO_RETRIVED_SUCCESS.value,
                                                                "collection_info": BaseController().get_json_serializable_object(info = collection_info)})

    except Exception as e:
        logger.error(f"Error while fetching vector database information:{e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                             content={"signal": ResponseSignal.VECTORDB_COLLECTION_INFO_RETRIVED_FAILED.value})


@nlp_router.post("/index/search")
async def index_search(request : Request, search_request : IndexSearchRequest):

    project_id = search_request.project_id

    project_model = ProjectModel(db_client = request.app.db_client)

    project_scheme = await project_model.get_project_or_create_one(project_id=project_id)

    if not project_scheme:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})
    
    nlp_controller = NLPController(vectordb_client = request.app.vectordb_client,
                                   generation_client = request.app.generation_client,
                                   embedding_client = request.app.embedding_client,
                                   template_parser = request.app.template_parser,
                                   )
    
    results = nlp_controller.search_in_vectordb_collection(
        project = project_scheme,
        text = search_request.text,
        limit = search_request.limit,
    )

    if not results or len(results) == 0:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.VECTORDB_COLLECTION_SEARCH_FAILED.value})
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.VECTORDB_COLLECTION_SEARCH_SUCCESS.value,
                                                             "results": BaseController().get_json_serializable_object(info = results)})



@nlp_router.post("/index/answer")
async def answer_user_query(request : Request,search_request : IndexSearchRequest):

    project_id = search_request.project_id
    
    try:

        # Check if the Project exists
        project_model = ProjectModel(db_client = request.app.db_client)
        is_project_exist, project_schema = await project_model.is_project_exist(project_id = project_id)

        if is_project_exist == False or is_project_exist is None or project_schema is None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})
        
        
        
        nlp_controller = NLPController(vectordb_client = request.app.vectordb_client,
                                    generation_client = request.app.generation_client,
                                    embedding_client = request.app.embedding_client,
                                    template_parser = request.app.template_parser,
                                    )
        
        config_model = ConfigModel(db_client= request.app.db_client)
        config_info = await config_model.load_config()
        
        answer, chat_history, full_prompt = nlp_controller.answer_rag_question(
            project = project_schema,
            question = search_request.text,
            config = config_info.dict(),
            limit = search_request.limit,
        )

        if not answer:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"signal": ResponseSignal.ANSWER_GENERATION_FAILED.value})
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.ANSWER_GENERATION_SUCCESS.value,
                                                                    "answer": BaseController().get_json_serializable_object(answer),
                                                                    "full_prompt": BaseController().get_json_serializable_object(full_prompt),
                                                                })

    
    except Exception as e:
        logger.error(f"Error while answering user query: {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.ANSWER_GENERATION_FAILED.value})








    


    
    

    






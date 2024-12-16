from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings, update_env_file_configuration
from controllers import DataController, ProjectController, ProcessController
from routes.requests_schemes import CreateProjectRequest
from models.enums import ResponseSignal
from .requests_schemes import ConfigUpdateRequest
from models import ProjectModel, ConfigModel
from models.db_schemes import ProjectSchema, ConfigSchema
import logging
from bson import json_util
import json


logger = logging.getLogger(__name__)

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["api_v1", "admin"],
)

# TODO: Endpoint to set the main project 

@admin_router.post("/project/create")
async def create_project(request: Request, create_project_request: CreateProjectRequest):
    project_id = create_project_request.project_id

    try:
        project_model = ProjectModel(db_client = request.app.db_client)
        is_project_exist, _ = await project_model.is_project_exist(project_id = project_id)

        if is_project_exist == True:
            return JSONResponse(
            status_code = status.HTTP_409_CONFLICT,
            content={
                "signal": ResponseSignal.Project_ALREADY_EXISTS.value,
            })
        
        project_schema = await project_model.create_project(ProjectSchema(project_id = project_id))
        
        if is_project_exist is None or project_schema is None:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal":ResponseSignal.CREATE_PROJECT_FAILED.value})
        
        logger.info(f"Project created successfully: {project_schema}")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.CREATE_PROJECT_SUCCESS.value})
    
    except Exception as e:
        logger.error(f"Error while creating project: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.CREATE_PROJECT_FAILED.value})


# TODO: Get all the files content 
# TODO: Get all the files of the project

# @admin_router.get("/project/get_all")
# async def get_all_projects(request: Request):
#     try:
#         project_model = ProjectModel(db_client = request.app.db_client)
        






@admin_router.post("/config/update")
async def update_config(request: Request, config_update_request: ConfigSchema, app_settings: Settings = Depends(get_settings)):

    logger.info(f"CONFIG Request:\n {config_update_request.dict()}")

    try:
        config_model = ConfigModel(db_client = request.app.db_client)
        #config_schema = ConfigSchema(**config_update_request.dict())
            
        _ =await config_model.update(new_config = config_update_request)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.UPDATING_CONFIGURATION_SUCCESS.value})
    
    except Exception as e:
        logger.error(f"Error while updating the config: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal":ResponseSignal.UPDATING_CONFIGURATION_FAILED.value})


@admin_router.get("/config/get")
async def get_admin_config(request: Request, app_settings: Settings = Depends(get_settings)):
    try:
        config_model = ConfigModel(db_client= request.app.db_client)
        config_data = await config_model.load_config()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.GETTING_CONFIGURATION_SUCCESS.value, "Admin Configuration": config_data.dict()})
    except Exception as e:
        logger.error(f"Error while getting the config: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.GETTING_CONFIGURATION_FAILED.value})
    


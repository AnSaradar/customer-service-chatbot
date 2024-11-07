from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings, update_env_file_configuration
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models.enums import ResponseSignal
from .requests_schemes import ConfigUpdateRequest
import logging
from bson import json_util
import json

logger = logging.getLogger('uvicorn.error')

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["api_v1", "admin"],
)

@admin_router.post("/config/update/")
async def update_config(config_update_request: ConfigUpdateRequest, app_settings: Settings = Depends(get_settings)):
    # #check if the reqeuest is empty
    # logger.info(f"Request: {config_update_request.dict()}")
    # logger.error(f"Empty Request: {not bool(config_update_request.dict())}")
    # if not bool(config_update_request.dict()):
    #     return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.EMPTY_CONFIGUARTION_REQUEST.value})
    try:
        # if hasattr(app_settings, request.key):
        #     # Update in-memory dictionary
        #     await update_env_file_configuration(updated_config)
        #     return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.UPDATING_CONFIGURATION_SUCCESS.value})
        # else:
        #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal":ResponseSignal.INVALID_CONFIGRATION_KEY.value})
        await update_env_file_configuration(config_update_request.dict()) 
        return JSONResponse(status_code=status.HTTP_200_OK, content={"signal": ResponseSignal.UPDATING_CONFIGURATION_SUCCESS.value})
    
    except Exception as e:
        logger.error(f"Error while updating the config: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal":ResponseSignal.UPDATING_CONFIGURATION_FAILED.value})



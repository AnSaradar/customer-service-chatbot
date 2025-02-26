from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import BaseController, AdminController, NLPController
from routes.requests_schemes import SuperAdminLoginRequest, SuperAdminLoginResponse
from models.enums import ResponseSignal
from .requests_schemes import ConfigUpdateRequest
from models import SuperAdminModel
from models.db_schemes import SuperAdminSchema
from fastapi.security import OAuth2PasswordBearer
import logging
from bson import json_util
import json
from jose import jwt
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["api_v1", "auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")



def create_access_token(data: dict, JWT_SECRET_KEY: str, JWT_ALGORITHM: str, ACCESS_TOKEN_EXPIRE_MINUTES: str):
    """
    Create a JWT access token with the given data.
    """

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt



@auth_router.post("/login", response_model=SuperAdminLoginResponse)
async def login(request: Request, super_admin_login_request: SuperAdminLoginRequest, app_settings: Settings = Depends(get_settings)):
    username = super_admin_login_request.username
    password = super_admin_login_request.password

    try:
        super_admin_model = SuperAdminModel(db_client = request.app.db_client)

        authenticated = await super_admin_model.authenticate(username, password)

        if not authenticated:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"signal": ResponseSignal.SUPER_ADMIN_WRONG_AUTH.value})
        

        access_token = create_access_token(data={"sub": username, "role":"super admin"},
                                           JWT_SECRET_KEY = app_settings.JWT_SECRET_KEY,
                                           JWT_ALGORITHM = app_settings.JWT_ALGORITHM,
                                           ACCESS_TOKEN_EXPIRE_MINUTES = app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "access_token": access_token,
                "token_type": "bearer"
            }
        )

    except Exception as e:
        logger.error(f"Error while logging in: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.SUPER_ADMIN_LOGIN_FAILED.value})


## TODO: Endpoint for change password








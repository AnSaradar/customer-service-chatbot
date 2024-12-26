from .BaseController import BaseController
from fastapi.security import OAuth2PasswordBearer
import logging
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

class AuthController(BaseController):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

    # Dependency function
    def validate_token(self,token: str = Depends(oauth2_scheme)):
        
        SECRET_KEY = self.app_settings.JWT_SECRET_KEY
        ALGORITHM = self.app_settings.JWT_ALGORITHM
        
        try:
            # Decode the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")  # Example claim
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            return payload  # Return payload if needed in the endpoint
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
    


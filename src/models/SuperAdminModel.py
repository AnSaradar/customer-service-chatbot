from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnums import DataBaseEnums
from .db_schemes import SuperAdminSchema
from passlib.context import CryptContext
from pydantic import ValidationError
from helpers.config import get_settings
import logging

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SuperAdminModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnums.COLLECTION_SUPER_ADMIN_NAME.value]
        self.logger = logging.getLogger(__name__)
        self.settings = get_settings()
    

    async def initialize_super_admin(self):
        """Initialize the super admin with default credentials if not already set."""
        default_username = self.settings.SUPER_ADMIN_USERNAME
        default_password = self.settings.SUPER_ADMIN_DEFAULT_PASSWORD
        
        # Check if super admin already exists
        # If it does, no need to create a new one
        # If it doesn't, create a new super admin with default credentials

        existing_admin = await self.collection.find_one({})
        if existing_admin:
            self.logger.info("Super admin already exists.")
            return
        
        self.logger.info("Creating default super admin.")
        default_admin = SuperAdminSchema(
            username=default_username,
            password=default_password,
        )
        await self.collection.insert_one(default_admin.dict(by_alias=True))
        self.logger.info("Default super admin created successfully.")
        return True
        

    async def authenticate(self, username: str, password: str):
        """Authenticate the super admin by validating username and password."""
        admin_data = await self.collection.find_one({"username": username})
        if not admin_data:
            self.logger.error("Authentication failed: Username not found.")
            return False
        
        # Validate password
        hashed_password = admin_data.get("password")
        if not pwd_context.verify(password, hashed_password):
            self.logger.error("Authentication failed: Invalid password.")
            return False
        
        self.logger.info("Authentication successful.")
        return True  # Return the admin data if authentication is successful

    async def update_password(self, username: str, new_password: str):
        """Update the super admin's password."""
        if not new_password:
            self.logger.error("Password update failed: Password cannot be empty.")
            raise ValueError("Password cannot be empty.")
        
        hashed_password = pwd_context.hash(new_password)
        result = await self.collection.update_one(
            {"username": username},
            {"$set": {"password": hashed_password}}
        )
        if result.matched_count == 0:
            self.logger.error("Password update failed: Username not found.")
            raise RuntimeError("Super admin not found.")
        
        self.logger.info("Password updated successfully.")

    async def get_super_admin(self):
        """Retrieve the super admin details."""
        admin_data = await self.collection.find_one({})
        if not admin_data:
            self.logger.error("Super admin not found in the database.")
            raise RuntimeError("Super admin not found in the database.")
        return SuperAdminSchema(**admin_data)

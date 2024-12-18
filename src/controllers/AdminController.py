from .BaseController import BaseController
from .NlpController import NLPController
from models.db_schemes import ConfigSchema
from models import ConfigModel, ProjectModel
from models.enums import DataBaseEnums
import logging
from pymongo.errors import PyMongoError
from motor.motor_asyncio import AsyncIOMotorClient

class AdminController(BaseController):
    def __init__(self, mongo_conn: object, db_client: object):
        super().__init__()
        self.db_client = db_client
        self.mongo_conn = mongo_conn
        self.logger = logging.getLogger(__name__)
    
    async def initilze_admin_config(self):

        self.logger.info("Initializing default configuration")
        collection = self.db_client[DataBaseEnums.COLLECTION_CONFIG_NAME.value]

        default_config = {
        "file_max_size": 10485760.0,
        "tempreature": 0.7,
        "contact_email": "contact@example.com",
        "contact_phone": "0812943874632948723"
        }

        if await collection.count_documents({}) == 0:
            try:
                validated_config = ConfigSchema(**default_config).dict()
                await collection.insert_one(validated_config)
                self.logger.info("Default configuration initialized.")
                return True
            except Exception as e:
                self.logger.error(f"Failed to initialize configuration: {e}")
                return False

        return True
    
    #TODO: SET THE MONGO REPLICA TO ENABLE THIS FUNCTION
    async def project_transactional_deletion(self, project_schema):
        async with await self.mongo_conn.start_session() as session:
            try:
                async with session.start_transaction():
                    project_collection = self.db_client[DataBaseEnums.COLLECTION_PROJECT_NAME.value]
                    chunk_collection = self.db_client[DataBaseEnums.COLLECTION_CHUNK_NAME.value]

                    
                    delete_chunks_result = await chunk_collection.delete_many(
                    {"chunk_project_id": project_schema.id}, session=session
                    )
                    self.logger.info(f"Deleted {delete_chunks_result.deleted_count} chunks.")

                    # Delete the project
                    delete_project_result = await project_collection.delete_one(
                        {"_id": project_schema.id}, session=session
                    )
                    if delete_project_result.deleted_count == 0:
                        raise Exception("Project not found or already deleted.")
                    
                    self.logger.info(f"Deleted project with ID: {project_schema.project_id}")

            
            except Exception as e:
                self.logger.error(f"Transaction failed: {e}")
                # Transaction will automatically abort if an exception occurs
                raise

            

                    






        


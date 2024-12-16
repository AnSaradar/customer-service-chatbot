from .BaseController import BaseController
from models.db_schemes import ConfigSchema
from models import ConfigModel
from models.enums import DataBaseEnums
import logging

class AdminController(BaseController):
    def __init__(self, db_client: object):
        super().__init__()
        self.db_client = db_client
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


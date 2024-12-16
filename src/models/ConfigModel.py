from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnums import DataBaseEnums
from .db_schemes import ConfigSchema
from pydantic import ValidationError
import logging

class ConfigModel(BaseDataModel):
    def __init__(self, db_client : object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnums.COLLECTION_CONFIG_NAME.value]
        self.logger = logging.getLogger(__name__)
        self.logger.info("The Model has been initialized")
    

    async def load_config(self):
        self.logger.info("Loading configuration")
        config_data = await self.collection.find_one({})  # Fetch the single record
        
        if not config_data:
            self.logger.error("Configuration not found in the database.")
            raise RuntimeError("Configuration not found in the database.")
        try:
            return ConfigSchema(**config_data)
        except ValidationError as e:
            self.logger.error(f"Invalid configuration data: {e}")
            raise

    def get(self, key: str):
        """Get a specific configuration value."""
        return getattr(self.config, key, None)

    async def update(self, new_config: ConfigSchema):

        self.logger.info("Updating configuration")
        self.logger.info(f"New Configuration Type: %s", type(new_config))

        """Update all configuration values using a ConfigSchema instance."""
        # Validate the new configuration
        try:
            validated_config = new_config.dict()
        except ValidationError as e:
            self.logger.error(f"Invalid configuration data: {e}")
            raise ValueError(f"Invalid configuration data: {e}")
        
        # Update the configuration in MongoDB
        _ = await self.collection.update_one({}, {"$set": validated_config}, upsert=True)
        self.logger.info("Configuration updated successfully.")
        
        # Reload the configuration into the Settings instance
        self.config = new_config

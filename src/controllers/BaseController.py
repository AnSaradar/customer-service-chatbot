from helpers.config import get_settings,Settings
import os
import json

class BaseController:

    def __init__(self):
        self.app_settings = get_settings()

        self.base_dir = os.path.dirname( os.path.dirname(__file__) )
        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files"
        ) 

        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )
    

    def get_vector_database_path(self, db_name):
        database_path = os.path.join(
            self.database_dir,
            db_name
        )
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        
        return database_path
    
    def get_json_serializable_object(self, info):
        return json.loads(
            json.dumps(info, default=lambda x: x.__dict__)
        )
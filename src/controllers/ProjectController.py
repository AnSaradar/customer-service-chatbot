from .BaseController import BaseController
import os
import logging



logger = logging.getLogger('uvicorn.error')

class ProjectController(BaseController):
    

    def __init__(self):
        super().__init__()
    
    
    def get_project_path(self , project_id:str):
        project_dir = os.path.join(self.files_dir , project_id)

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        return project_dir 
    

    def get_all_the_files_names_inside_folder(self,folder_path: str):

        try:
            if not os.path.exists(folder_path):
                logger.error(f"The folder '{folder_path}' does not exist.")
            
            file_names = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
            #logger.error(f"file_names:{file_names}")
            return file_names
        
        except FileNotFoundError:
            logger.error("The specified folder path does not exist.")
            return []
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return []   
       
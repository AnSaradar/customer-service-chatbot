from .BaseController import BaseController
import os
import logging
import shutil



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



def delete_all_files_in_folder(folder_path):
    try:
        # Iterate through each item in the folder
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            # Check if item is a file or directory and delete accordingly
            if os.path.isfile(item_path):
                os.remove(item_path)  # Remove the file
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove the directory and its contents
        logger.info("All files and directories inside the folder have been deleted.")
    except FileNotFoundError:
        logger.error("The specified folder path does not exist.")
    except Exception as e:
        logger.error(f"An error occurred: {e}") 
       
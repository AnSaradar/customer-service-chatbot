from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnums import DataBaseEnums
class ProjectModel(BaseDataModel):

    def __init__(self, db_client : object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnums.COLLECTION_PROJECT_NAME.value]
    

    async def create_project(self, project : Project):
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))   # to convert from pydantic object to dictinonary to insert inside the mongodb
        project._id = result.inserted_id  # set the returned mongodb id from the insert operation
        return project


    async def get_project_or_create_one(self, project_id : str):
        record = await self.collection.find_one({
            "project_id": project_id
        }) # record is dict

        if record is None: # Record not found, we should create it
            return await self.create_project(Project(project_id=project_id))

        return Project(**record) # Convert dict to pydantic model
    

    async def get_all_projects(self, page : int=1, page_size: int=10): 

        # We applied basic pagination
        total_documents_count = await self.collection.count_documents()

        total_pages = total_documents_count // page_size
        if total_documents_count % page_size > 0:
            total_pages += 1

        cursor = self.collection.find().skip((page - 1)*page_size).limit(page_size)

        projects = []
        async for project in cursor:
            projects.append(Project(**project))
        
        return projects, total_pages


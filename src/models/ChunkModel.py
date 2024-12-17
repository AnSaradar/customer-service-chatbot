from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunkSchema
from .enums.DataBaseEnums import DataBaseEnums
from bson.objectid import ObjectId
from pymongo import InsertOne
import logging

class ChunkModel(BaseDataModel):
    def __init__(self, db_client : object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnums.COLLECTION_CHUNK_NAME.value]
        self.logger = logging.getLogger(__name__)
    

    async def create_chunk(self, chunk : DataChunkSchema):
        try:
            result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
            chunk._id = result.inserted_id
            return chunk
        
        except Exception as e:
            self.logger.error(f"Error while creating chunk : {e}")
            return None
    
    async def get_chunk(self, chunk_id : str):
        try:
            result = await self.collection.find_one({
                "_id": ObjectId(chunk_id)
            })

            if result is None:
                return None
            
            return DataChunkSchema(**result)
        except Exception as e:
            self.logger.error(f"Error while getting chunk : {e}")
            return None
    

    async def insert_many_chunks(self, chunks : list, batch_size : int=100):
        try:
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]

                operations = [
                    InsertOne(chunk.dict(by_alias=True, exclude_unset=True))  # We define the operation here, to use it in the bulk write operation
                    for chunk in batch
                ]


                await self.collection.bulk_write(operations)

            
            return len(chunks)
        except Exception as e:
            self.logger.error(f"Error while insert many chunks : {e}")
            return None
    
    async def delete_all_chunks_by_project_id(self, project_id : ObjectId):
        try:
            result = await self.collection.delete_many({
                "chunk_project_id" : project_id,
            })

            return result.deleted_count
        except Exception as e:
            self.logger.error(f"Error While deleting project chunks {e}")
            return None
        
    async def get_all_chunks_by_project_id(self, project_id : ObjectId, page_no : int = 1, page_size : int = 50):
        try:
            
            records = await self.collection.find({
                "chunk_project_id" : project_id,
            }).skip(
                (page_no -1) * page_size
            ).limit(page_size).to_list(length=None) # length=None includes all the chunks / elements
            
            return [
                DataChunkSchema(**record)
                for record in records
            ]
        
        except Exception as e:
            self.logger.error(f"Error will retrieving the project data : {e}")
            return None
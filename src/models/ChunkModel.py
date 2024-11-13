from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnums import DataBaseEnums
from bson.objectid import ObjectId
from pymongo import InsertOne


class ChunkModel(BaseDataModel):
    def __init__(self, db_client : object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnums.COLLECTION_CHUNK_NAME.value]
    

    async def create_chunk(self, chunk : DataChunk):
        result = await self.collection.insert_one(chunk.dict())
        chunk._id = result.inserted_id
        return chunk
    
    async def get_chunk(self, chunk_id : str):
        result = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        if result is None:
            return None
        
        return DataChunk(**result)
    

    async def insert_many_chunks(self, chunks : list, batch_size : int=100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            await self.collection.insert_many(batch)

            operations = [
                InsertOne(chunk.dict())  # We define the operation here, to use it in the bulk write operation
                for chunk in batch
            ]


            await self.collection.bulk_write(operations)

        
        return len(chunks)

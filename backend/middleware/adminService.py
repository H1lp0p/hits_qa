from motor.motor_asyncio import AsyncIOMotorClient

class AdminService:

    def __init__(self, client: AsyncIOMotorClient, datatabase_name: str, collection_name: str):
        self.client = client
        self.collection = self.client[datatabase_name][collection_name]

    
    async def clear_db(self):
        res = await self.collection.delete_many({})

        print(f"admin> deleted {res.deleted_count} items from tasks collection")

        return res.deleted_count
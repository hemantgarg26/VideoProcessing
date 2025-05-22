from app.core.config import settings

from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db = None

    async def connect(self):
        if not self.client:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            self.db = self.client[settings.MONGO_DB]

    async def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

mongodb = MongoDB()
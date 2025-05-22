# services/query_applicator.py
from typing import Any, Dict, List, Optional
from app.utils.db_connect import mongodb

class MongoQueryApplicator:
    def __init__(self, collection_name: str):
        self.collection = mongodb.db[collection_name]

    async def find(self, filters: Optional[Dict[str, Any]] = None, limit: int = 10) -> List[Dict]:
        filters = filters or {}
        cursor = self.collection.find(filters).limit(limit)
        return await cursor.to_list(length=limit)

    async def find_one(self, filters: Dict[str, Any]) -> Optional[Dict]:
        return await self.collection.find_one(filters)

    async def insert_one(self, document: Dict[str, Any]) -> str:
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def update_one(self, filters: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        result = await self.collection.update_one(filters, {'$set': update_data})
        return result.modified_count

    async def delete_one(self, filters: Dict[str, Any]) -> int:
        result = await self.collection.delete_one(filters)
        return result.deleted_count
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        filters = filters or {}
        return await self.collection.count_documents(filters)
from typing import List, Optional, Any
from pymongo.collection import Collection
from bson import ObjectId
from route_optimizer.database.connection import get_database

class AnalyticsRepository:
    def __init__(self):
        self.collection: Collection = get_database()["analytics"]

    def _map_doc(self, doc: dict) -> dict:
        if not doc:
            return doc
        doc["id"] = str(doc.pop("_id"))
        return doc

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        return self.get_by_id(result.inserted_id)

    def get_by_id(self, analytics_id: Any) -> Optional[dict]:
        try:
            doc = self.collection.find_one({"_id": ObjectId(analytics_id)})
            return self._map_doc(doc)
        except Exception:
            return None

    def get_latest(self) -> Optional[dict]:
        doc = self.collection.find_one(sort=[("_id", -1)])
        return self._map_doc(doc)

    def get_all(self) -> List[dict]:
        docs = self.collection.find().sort("_id", -1)
        return [self._map_doc(doc) for doc in docs]

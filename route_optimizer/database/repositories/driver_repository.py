from typing import List, Optional, Any
import logging
from pymongo.collection import Collection
from bson import ObjectId
from route_optimizer.database.connection import get_database

class DriverRepository:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.collection: Collection = get_database()["drivers"]

    def _map_doc(self, doc: dict) -> dict:
        if not doc:
            return doc
        doc["id"] = str(doc.pop("_id"))
        return doc

    def create(self, data: dict) -> dict:
        self.logger.info(f"Creating driver in MongoDB collection: {self.collection.name}")
        result = self.collection.insert_one(data)
        if not result.inserted_id:
            raise Exception("Failed to insert driver into MongoDB")
        self.logger.info(f"Driver created successfully with ObjectId: {result.inserted_id}")
        return self.get_by_id(result.inserted_id)

    def get_by_id(self, driver_id: Any) -> Optional[dict]:
        try:
            doc = self.collection.find_one({"_id": ObjectId(driver_id)})
            return self._map_doc(doc)
        except Exception:
            return None

    def get_all(self) -> List[dict]:
        docs = self.collection.find()
        return [self._map_doc(doc) for doc in docs]

    def update(self, driver_id: Any, data: dict) -> Optional[dict]:
        try:
            self.collection.update_one(
                {"_id": ObjectId(driver_id)},
                {"$set": data}
            )
            return self.get_by_id(driver_id)
        except Exception:
            return None

    def delete(self, driver_id: Any) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(driver_id)})
            return result.deleted_count > 0
        except Exception:
            return False

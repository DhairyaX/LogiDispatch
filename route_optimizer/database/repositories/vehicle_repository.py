from typing import List, Optional, Any
from pymongo.collection import Collection
from bson import ObjectId
from route_optimizer.database.connection import get_database

class VehicleRepository:
    def __init__(self):
        self.collection: Collection = get_database()["vehicles"]

    def _map_doc(self, doc: dict) -> dict:
        if not doc:
            return doc
        doc["id"] = str(doc.pop("_id"))
        return doc

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        return self.get_by_id(result.inserted_id)

    def get_by_id(self, vehicle_id: Any) -> Optional[dict]:
        try:
            doc = self.collection.find_one({"_id": ObjectId(vehicle_id)})
            return self._map_doc(doc)
        except Exception:
            return None

    def get_all(self) -> List[dict]:
        docs = self.collection.find()
        return [self._map_doc(doc) for doc in docs]

    def update(self, vehicle_id: Any, data: dict) -> Optional[dict]:
        try:
            self.collection.update_one(
                {"_id": ObjectId(vehicle_id)},
                {"$set": data}
            )
            return self.get_by_id(vehicle_id)
        except Exception:
            return None

    def delete(self, vehicle_id: Any) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(vehicle_id)})
            return result.deleted_count > 0
        except Exception:
            return False

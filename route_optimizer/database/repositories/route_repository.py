from typing import List, Optional, Any
from pymongo.collection import Collection
from bson import ObjectId
from route_optimizer.database.connection import get_database

class RouteRepository:
    def __init__(self):
        self.collection: Collection = get_database()["routes"]

    def _map_doc(self, doc: dict) -> dict:
        if not doc:
            return doc
        doc["id"] = str(doc.pop("_id"))
        return doc

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        return self.get_by_id(result.inserted_id)

    def get_by_id(self, route_id: Any) -> Optional[dict]:
        try:
            doc = self.collection.find_one({"_id": ObjectId(route_id)})
            return self._map_doc(doc)
        except Exception:
            return None

    def get_latest(self) -> Optional[dict]:
        doc = self.collection.find_one(sort=[("_id", -1)])
        return self._map_doc(doc)

    def get_all(self) -> List[dict]:
        docs = self.collection.find().sort("_id", -1)
        return [self._map_doc(doc) for doc in docs]

    def get_active(self) -> List[dict]:
        docs = self.collection.find({"status": "Active"}).sort("_id", -1)
        return [self._map_doc(doc) for doc in docs]

    def archive_all_active(self) -> None:
        try:
            self.collection.update_many(
                {"status": "Active"},
                {"$set": {"status": "Archived"}}
            )
        except Exception:
            pass

    def update(self, route_id: Any, data: dict) -> Optional[dict]:
        try:
            self.collection.update_one(
                {"_id": ObjectId(route_id)},
                {"$set": data}
            )
            return self.get_by_id(route_id)
        except Exception:
            return None

    def delete(self, route_id: Any) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(route_id)})
            return result.deleted_count > 0
        except Exception:
            return False

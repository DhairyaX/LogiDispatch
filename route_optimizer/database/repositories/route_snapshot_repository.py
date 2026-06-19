from typing import Optional, Any
from pymongo.collection import Collection
from route_optimizer.database.connection import get_database

class RouteSnapshotRepository:
    def __init__(self):
        self.collection: Collection = get_database()["route_snapshots"]

    def _map_doc(self, doc: dict) -> dict:
        if not doc:
            return doc
        doc["id"] = str(doc.pop("_id"))
        return doc

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        return self.get_latest()

    def get_latest(self) -> Optional[dict]:
        doc = self.collection.find_one(sort=[("_id", -1)])
        return self._map_doc(doc)

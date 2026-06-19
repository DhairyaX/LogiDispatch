from typing import List, Optional
from datetime import datetime, timezone
from route_optimizer.api.schemas.delivery import DeliveryCreate, DeliveryResponse
from route_optimizer.database.repositories.delivery_repository import DeliveryRepository

class DeliveryService:
    def __init__(self):
        self.repository = DeliveryRepository()

    def get_all(self) -> List[DeliveryResponse]:
        docs = self.repository.get_all()
        return [DeliveryResponse(**d) for d in docs]

    def get_by_id(self, delivery_id: str) -> Optional[DeliveryResponse]:
        doc = self.repository.get_by_id(delivery_id)
        if doc:
            return DeliveryResponse(**doc)
        return None

    def create(self, delivery: DeliveryCreate) -> DeliveryResponse:
        data = delivery.model_dump()
        data["createdAt"] = datetime.now(timezone.utc).isoformat()
        data["status"] = "Pending"
        doc = self.repository.create(data)
        return DeliveryResponse(**doc)

    def update(self, delivery_id: str, delivery: DeliveryCreate) -> Optional[DeliveryResponse]:
        # Preserve original createdAt and status
        existing = self.repository.get_by_id(delivery_id)
        if not existing:
            return None
            
        data = delivery.model_dump()
        data["createdAt"] = existing.get("createdAt", datetime.now(timezone.utc).isoformat())
        data["status"] = existing.get("status", "Pending")
        
        doc = self.repository.update(delivery_id, data)
        if doc:
            return DeliveryResponse(**doc)
        return None

    def delete(self, delivery_id: str) -> bool:
        return self.repository.delete(delivery_id)

from typing import List, Optional
from route_optimizer.api.schemas.vehicle import VehicleCreate, VehicleResponse
from route_optimizer.database.repositories.vehicle_repository import VehicleRepository

class VehicleService:
    def __init__(self):
        self.repository = VehicleRepository()

    def get_all(self) -> List[VehicleResponse]:
        docs = self.repository.get_all()
        return [VehicleResponse(**d) for d in docs]

    def get_by_id(self, vehicle_id: str) -> Optional[VehicleResponse]:
        doc = self.repository.get_by_id(vehicle_id)
        if doc:
            return VehicleResponse(**doc)
        return None

    def create(self, vehicle: VehicleCreate) -> VehicleResponse:
        doc = self.repository.create(vehicle.model_dump())
        return VehicleResponse(**doc)

    def update(self, vehicle_id: str, vehicle: VehicleCreate) -> Optional[VehicleResponse]:
        doc = self.repository.update(vehicle_id, vehicle.model_dump())
        if doc:
            return VehicleResponse(**doc)
        return None

    def delete(self, vehicle_id: str) -> bool:
        return self.repository.delete(vehicle_id)

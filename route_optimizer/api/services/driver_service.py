from typing import List, Optional
from route_optimizer.api.schemas.driver import DriverCreate, DriverResponse
from route_optimizer.database.repositories.driver_repository import DriverRepository

class DriverService:
    def __init__(self):
        self.repository = DriverRepository()

    def get_all(self) -> List[DriverResponse]:
        docs = self.repository.get_all()
        return [DriverResponse(**d) for d in docs]

    def get_by_id(self, driver_id: str) -> Optional[DriverResponse]:
        doc = self.repository.get_by_id(driver_id)
        if doc:
            return DriverResponse(**doc)
        return None

    def create(self, driver: DriverCreate) -> DriverResponse:
        doc = self.repository.create(driver.model_dump())
        return DriverResponse(**doc)

    def update(self, driver_id: str, driver: DriverCreate) -> Optional[DriverResponse]:
        doc = self.repository.update(driver_id, driver.model_dump())
        if doc:
            return DriverResponse(**doc)
        return None

    def delete(self, driver_id: str) -> bool:
        return self.repository.delete(driver_id)

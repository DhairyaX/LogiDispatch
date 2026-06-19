from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from route_optimizer.api.schemas.driver import DriverCreate, DriverResponse
from route_optimizer.api.services.driver_service import DriverService
from route_optimizer.api.dependencies.services import get_driver_service

router = APIRouter(prefix="/api/v1/drivers", tags=["Drivers"])

@router.get("/", response_model=List[DriverResponse])
def get_all_drivers(service: DriverService = Depends(get_driver_service)):
    return service.get_all()

@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(driver_id: str, service: DriverService = Depends(get_driver_service)):
    driver = service.get_by_id(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(driver: DriverCreate, service: DriverService = Depends(get_driver_service)):
    return service.create(driver)

@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(driver_id: str, driver: DriverCreate, service: DriverService = Depends(get_driver_service)):
    updated = service.update(driver_id, driver)
    if not updated:
        raise HTTPException(status_code=404, detail="Driver not found")
    return updated

@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(driver_id: str, service: DriverService = Depends(get_driver_service)):
    if not service.delete(driver_id):
        raise HTTPException(status_code=404, detail="Driver not found")
    return None

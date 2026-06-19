from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from route_optimizer.api.schemas.vehicle import VehicleCreate, VehicleResponse
from route_optimizer.api.services.vehicle_service import VehicleService
from route_optimizer.api.dependencies.services import get_vehicle_service

router = APIRouter(prefix="/api/v1/vehicles", tags=["Vehicles"])

@router.get("/", response_model=List[VehicleResponse])
def get_all_vehicles(service: VehicleService = Depends(get_vehicle_service)):
    return service.get_all()

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: str, service: VehicleService = Depends(get_vehicle_service)):
    vehicle = service.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, service: VehicleService = Depends(get_vehicle_service)):
    return service.create(vehicle)

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: str, vehicle: VehicleCreate, service: VehicleService = Depends(get_vehicle_service)):
    updated = service.update(vehicle_id, vehicle)
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return updated

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: str, service: VehicleService = Depends(get_vehicle_service)):
    if not service.delete(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return None

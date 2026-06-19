from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from route_optimizer.api.schemas.delivery import DeliveryCreate, DeliveryResponse
from route_optimizer.api.services.delivery_service import DeliveryService
from route_optimizer.api.dependencies.services import get_delivery_service

router = APIRouter(prefix="/api/v1/deliveries", tags=["Deliveries"])

@router.get("/", response_model=List[DeliveryResponse])
def get_all_deliveries(service: DeliveryService = Depends(get_delivery_service)):
    return service.get_all()

@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: str, service: DeliveryService = Depends(get_delivery_service)):
    delivery = service.get_by_id(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery

@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(delivery: DeliveryCreate, service: DeliveryService = Depends(get_delivery_service)):
    return service.create(delivery)

@router.put("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(delivery_id: str, delivery: DeliveryCreate, service: DeliveryService = Depends(get_delivery_service)):
    updated = service.update(delivery_id, delivery)
    if not updated:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return updated

@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery(delivery_id: str, service: DeliveryService = Depends(get_delivery_service)):
    if not service.delete(delivery_id):
        raise HTTPException(status_code=404, detail="Delivery not found")
    return None

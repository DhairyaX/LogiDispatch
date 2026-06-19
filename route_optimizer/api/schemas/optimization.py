from pydantic import BaseModel, Field
from typing import List, Optional

class OptimizationRequest(BaseModel):
    vehicleCount: int = Field(default=5, ge=1)
    optimizationMode: str = Field(default="distance")
    balancingMode: str = Field(default="balanced")

class RouteLocation(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float

class VehicleRouteSchema(BaseModel):
    vehicle_id: str
    vehicle_name: str
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    locations: List[RouteLocation]
    distance: float
    duration: float

class OptimizationResponse(BaseModel):
    id: Optional[str] = None
    vehiclesUsed: int
    fleetUtilization: float
    totalDistance: float
    totalDuration: float
    routes: List[VehicleRouteSchema]
    metrics: Optional[dict] = None

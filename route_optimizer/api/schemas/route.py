from pydantic import BaseModel
from typing import List, Optional, Literal

class RouteLocationSchema(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float

class RouteBase(BaseModel):
    driverId: str
    driverName: str
    vehicleId: str
    vehicleName: str
    deliveryIds: List[str]
    stopCount: int
    totalDistanceKm: float
    totalDurationMinutes: float
    routeSequence: List[RouteLocationSchema]
    status: Literal['Active', 'Completed', 'Archived']

class RouteCreate(RouteBase):
    pass

class RouteResponse(RouteBase):
    id: str
    createdAt: str

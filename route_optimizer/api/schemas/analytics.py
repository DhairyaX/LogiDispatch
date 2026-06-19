from pydantic import BaseModel
from typing import Optional

class AnalyticsResponse(BaseModel):
    id: Optional[str] = None
    fleetUtilization: float
    workloadStandardDeviation: float
    distanceStandardDeviation: float
    durationStandardDeviation: float
    averageStopsPerVehicle: float
    averageDistancePerVehicle: float
    averageDurationPerVehicle: float
    maxDistance: float
    minDistance: float
    maxDuration: float
    minDuration: float

class VehicleMetrics(BaseModel):
    vehicle_id: str
    vehicle_name: str
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    num_stops: int
    distance: float
    duration: float

from pydantic import BaseModel
from typing import Literal

class VehicleBase(BaseModel):
    name: str
    vehicleNumber: str
    status: Literal['Available', 'In Route', 'Maintenance', 'Unavailable']

class VehicleCreate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    id: str

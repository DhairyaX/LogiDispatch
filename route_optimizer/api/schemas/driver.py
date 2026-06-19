from pydantic import BaseModel
from typing import Literal

class DriverBase(BaseModel):
    name: str
    phone: str
    status: Literal['Available', 'Busy', 'On Leave', 'Offline']

class DriverCreate(DriverBase):
    pass

class DriverResponse(DriverBase):
    id: str

from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class DeliveryBase(BaseModel):
    customerName: str
    phoneNumber: str
    address: str
    latitude: float
    longitude: float
    priority: Literal['Low', 'Medium', 'High']
    packageWeight: float

class DeliveryCreate(DeliveryBase):
    pass

class DeliveryResponse(DeliveryBase):
    id: str
    status: Literal['Pending', 'Assigned', 'In Transit', 'Delivered']
    createdAt: str

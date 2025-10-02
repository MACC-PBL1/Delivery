#añadir delivery schemas de validacion y respuesta
from datetime import datetime
from pydantic import BaseModel

class DeliveryBase(BaseModel):
    order_id: int
    address: str

class DeliveryCreate(DeliveryBase):
    pass

class Delivery(DeliveryBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

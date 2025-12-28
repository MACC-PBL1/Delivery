from chassis.sql import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

class Delivery(BaseModel):
    __tablename__ = "delivery"

    STATUS_PENDING = "pending"
    STATUS_PACKAGED = "packaged"
    STATUS_DELIVERING = "delivering"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    client_id: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    street: Mapped[str] = mapped_column(String, nullable=False)
    zip: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=STATUS_PENDING)


from chassis.sql import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

class Delivery(BaseModel):
    __tablename__ = "delivery"

    STATUS_PENDING = "Pending"
    STATUS_PACKAGED = "Packaged"
    STATUS_DELIVERING = "Delivering"
    STATUS_DELIVERED = "Delivered"
    STATUS_CANCELLED = "Cancelled"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    client_id: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    street: Mapped[str] = mapped_column(String(50), nullable=False)
    zip: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=STATUS_PENDING)


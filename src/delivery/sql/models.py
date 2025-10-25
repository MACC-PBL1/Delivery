# -*- coding: utf-8 -*-
"""Database models definitions. Table representations as class."""
from chassis.sql import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

class Delivery(BaseModel):
    """Representación de la tabla 'delivery' en la base de datos."""
    __tablename__ = "delivery"

    STATUS_PENDING = "pending"
    STATUS_PACKAGED = "packaged"
    STATUS_DELIVERING = "delivering"
    STATUS_DELIVERED = "delivered"

    # ID del pedido asociado
    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)

    #identificar al cliente
    client_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Dirección de entrega (obligatoria)
    address: Mapped[str] = mapped_column(String(255), nullable=True)

    # Estado actual de la entrega (por defecto, 'pending')
    status: Mapped[str] = mapped_column(String(50), default=STATUS_PENDING)




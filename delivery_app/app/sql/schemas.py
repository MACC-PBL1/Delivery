# -*- coding: utf-8 -*-
"""Classes for Request/Response schema definitions."""
# pylint: disable=too-few-public-methods
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Respuesta genérica de éxito o error."""
    detail: str = Field(example="Entrega creada correctamente")


# ---------------------------------------------------------------------
#  Esquemas base y de validación para la entidad Delivery
# ---------------------------------------------------------------------

class DeliveryBase(BaseModel):
    """Campos comunes de una entrega (Delivery)."""
    order_id: int = Field(..., example=101)
    client_id: int = Field(..., example=1)  # AGREGADO: client_id obligatorio
    address: str = Field("", example="Calle Mayor 123, Madrid")  # Default vacío


class DeliveryCreate(DeliveryBase):
    """Schema para crear una nueva entrega (entrada POST)."""
    pass


class DeliveryUpdate(BaseModel):
    """Schema para actualizar datos de una entrega (entrada PUT/PATCH)."""
    address: Optional[str] = Field(None, example="Avenida del Sol 45, Madrid")
    status: Optional[str] = Field(None, example="delivered")


class DeliveryOut(DeliveryBase):
    """Respuesta al consultar una entrega (salida GET)."""
    id: int = Field(..., example=1)
    status: str = Field(..., example="pending")
    creation_date: datetime = Field(..., example="2025-10-09T12:00:00Z")
    update_date: datetime = Field(..., example="2025-10-09T12:30:00Z")

    class Config:
        from_attributes = True  # equivale a orm_mode=True para Pydantic v2
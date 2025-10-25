# -*- coding: utf-8 -*-
"""Classes for Request/Response schema definitions."""
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Respuesta genérica de éxito o error."""
    detail: str = Field(example="Entrega creada correctamente")
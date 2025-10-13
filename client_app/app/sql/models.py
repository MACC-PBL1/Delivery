# -*- coding: utf-8 -*-
"""Database models definitions. Table representations as class."""
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from .database import Base


class BaseModel(Base):
    """Clase base reutilizable para los modelos de base de datos."""
    # Indicamos que esta clase es abstracta (no crea una tabla por sí sola)
    __abstract__ = True

    # Fecha y hora en que se crea el registro (automáticamente)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())

    # Fecha y hora en que se actualiza el registro (automáticamente en cada cambio)
    update_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        """Devuelve una representación legible del objeto (útil para depuración)."""
        fields = ""
        for column in self.__table__.columns:
            if fields == "":
                fields = f"{column.name}='{getattr(self, column.name)}'"
            else:
                fields = f"{fields}, {column.name}='{getattr(self, column.name)}'"
        return f"<{self.__class__.__name__}({fields})>"

    @staticmethod
    def list_as_dict(items):
        """Convierte una lista de objetos en una lista de diccionarios."""
        return [i.as_dict() for i in items]

    def as_dict(self):
        """Convierte un solo objeto en un diccionario."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Delivery(BaseModel):
    """Representación de la tabla 'delivery' en la base de datos."""
    __tablename__ = "delivery"

    # ID único para cada entrega (clave primaria)
    id = Column(Integer, primary_key=True, index=True)

    # ID del pedido asociado (por ejemplo, un número de pedido)
    order_id = Column(Integer, nullable=False)

    # Dirección de entrega (obligatoria)
    address = Column(String(255), nullable=False)

    # Estado actual de la entrega (por defecto, 'pending')
    status = Column(String(50), default="pending")
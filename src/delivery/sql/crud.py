# -*- coding: utf-8 -*-
"""
CRUD functions for Delivery Service.
Functions that interact with the database using SQLAlchemy AsyncSession.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.sql import models, schemas

# ----------------------------------------
#  Crear una nueva entrega
# ----------------------------------------
async def create_delivery(db: AsyncSession, delivery: schemas.DeliveryCreate):
    """
    Crea un nuevo delivery en la base de datos.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        delivery (schemas.DeliveryCreate): Pydantic schema con order_id, client_id y opcional address.

    Returns:
        models.Delivery: Objeto Delivery recién creado con ID generado.
    """
    new_delivery = models.Delivery(
        order_id=delivery.order_id,
        client_id=delivery.client_id,  # CORREGIDO: ahora client_id es obligatorio
        address=delivery.address,
        status="pending"  # Estado inicial por defecto
    )
    db.add(new_delivery)  # Añadir a la sesión
    await db.commit()     # Guardar cambios en DB
    await db.refresh(new_delivery)  # Refrescar para obtener ID y datos actualizados
    return new_delivery

# ----------------------------------------
#  Obtener una entrega por ID
# ----------------------------------------
async def get_delivery(db: AsyncSession, delivery_id: int):
    """
    Obtiene un delivery específico por su ID.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        delivery_id (int): ID del delivery a buscar.

    Returns:
        models.Delivery | None: El delivery encontrado o None si no existe.
    """
    result = await db.execute(
        select(models.Delivery).where(models.Delivery.id == delivery_id)
    )
    return result.scalars().first()

# ----------------------------------------
#  Obtener lista de deliveries con paginación
# ----------------------------------------
async def get_deliveries(db: AsyncSession, skip: int = 0, limit: int = 10):
    """
    Obtiene una lista de deliveries, con soporte de paginación.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        skip (int): Número de registros a saltar.
        limit (int): Número máximo de registros a devolver.

    Returns:
        List[models.Delivery]: Lista de deliveries.
    """
    result = await db.execute(select(models.Delivery).offset(skip).limit(limit))
    return result.scalars().all()

# ----------------------------------------
#  Actualizar delivery completo (status, address u otros campos)
# ----------------------------------------
async def update_delivery(db: AsyncSession, delivery_id: int, updates: dict):
    """
    Actualiza uno o varios campos de un delivery existente.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        delivery_id (int): ID del delivery a actualizar.
        updates (dict): Diccionario con campos a actualizar (ej: status, address).

    Returns:
        models.Delivery | None: El delivery actualizado o None si no existe.
    """
    result = await db.execute(
        select(models.Delivery).where(models.Delivery.id == delivery_id)
    )
    delivery = result.scalars().first()
    if not delivery:
        return None

    # Actualizar los campos indicados en el diccionario
    for key, value in updates.items():
        setattr(delivery, key, value)

    await db.commit()    # Guardar cambios en DB
    await db.refresh(delivery)
    return delivery

# ----------------------------------------
#  Eliminar un delivery
# ----------------------------------------
async def delete_delivery(db: AsyncSession, delivery_id: int):
    """
    Elimina un delivery por su ID.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        delivery_id (int): ID del delivery a eliminar.

    Returns:
        models.Delivery | None: El delivery eliminado o None si no existe.
    """
    result = await db.execute(
        select(models.Delivery).where(models.Delivery.id == delivery_id)
    )
    delivery = result.scalars().first()
    if not delivery:
        return None

    await db.delete(delivery)
    await db.commit()
    return delivery
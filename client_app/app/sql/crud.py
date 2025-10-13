#añadir funciones CRUD, funciones que interactuan con la base de datos.
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.sql import models, schemas

# Crear una nueva entrega en la base de datos
async def create_delivery(db: AsyncSession, delivery: schemas.DeliveryCreate):
    # Crear un nuevo objeto Delivery con los datos recibidos
    new_delivery = models.Delivery(
        order_id=delivery.order_id,
        address=delivery.address,
        status="pending"  # Estado inicial por defecto
    )
    # Añadir la nueva entrega a la sesión
    db.add(new_delivery)
    # Confirmar los cambios en la base de datos
    await db.commit()
    # Refrescar el objeto para obtener los datos actualizados (como el ID generado)
    await db.refresh(new_delivery)
    # Devolver la entrega creada
    return new_delivery

# Obtener una entrega por su ID
async def get_delivery(db: AsyncSession, delivery_id: int):
    # Buscar la entrega con el ID indicado
    result = await db.execute(select(models.Delivery).where(models.Delivery.id == delivery_id))
    # Devolver la primera coincidencia (o None si no existe)
    return result.scalars().first()

# Actualizar el estado de una entrega existente
async def update_delivery_status(db: AsyncSession, delivery_id: int, status: str):
    # Buscar la entrega correspondiente en la base de datos
    result = await db.execute(select(models.Delivery).where(models.Delivery.id == delivery_id))
    delivery = result.scalars().first()

    # Si no se encuentra la entrega, devolver None
    if not delivery:
        return None

    # Actualizar el estado de la entrega
    delivery.status = status
    # Guardar los cambios
    await db.commit()
    # Refrescar el objeto para obtener los datos actualizados
    await db.refresh(delivery)
    # Devolver la entrega actualizada
    return delivery
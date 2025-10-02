#añadir funciones CRUD, funciones que interactuan con la base de datos.
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.sql import models, schemas

async def create_delivery(db: AsyncSession, delivery: schemas.DeliveryCreate):
    new_delivery = models.Delivery(
        order_id=delivery.order_id,
        address=delivery.address,
        status="pending"
    )
    db.add(new_delivery)
    await db.commit()
    await db.refresh(new_delivery)
    return new_delivery

async def get_delivery(db: AsyncSession, delivery_id: int):
    result = await db.execute(select(models.Delivery).where(models.Delivery.id == delivery_id))
    return result.scalars().first()

async def update_delivery_status(db: AsyncSession, delivery_id: int, status: str):
    result = await db.execute(select(models.Delivery).where(models.Delivery.id == delivery_id))
    delivery = result.scalars().first()
    if not delivery:
        return None
    delivery.status = status
    await db.commit()
    await db.refresh(delivery)
    return delivery

from .models import Delivery
from chassis.sql import get_element_by_id
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

async def get_delivery(
    db: AsyncSession,
    order_id: int,
) -> Optional[Delivery]:
    return await get_element_by_id(
        db=db,
        model=Delivery,
        element_id=order_id,
    )

def create_delivery(
    db: AsyncSession,
    order_id: int, 
    client_id: int,
) -> None:
    db.add(
        Delivery(
            order_id=order_id,
            client_id=client_id,
        )
    )
    
async def update_address(
    db: AsyncSession,
    order_id: int,
    address: str,
) -> Optional[Delivery]:
    db_delivery = await get_delivery(db, order_id)
    if db_delivery is not None:
        db_delivery.address = address
        await db.commit()
        await db.refresh(db_delivery)
    return db_delivery

async def update_status(
    db: AsyncSession,
    order_id: int,
    status: str,
) -> Optional[Delivery]:
    db_delivery = await get_delivery(db, order_id)
    if db_delivery is not None:
        db_delivery.status = status
        await db.commit()
        await db.refresh(db_delivery)
    return db_delivery
from .models import Delivery
from chassis.sql import (
    get_element_by_id,
    update_elements_statement_result,
)
from sqlalchemy import update
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

async def create_delivery(
    db: AsyncSession,
    order_id: int, 
    client_id: int,
    city: str,
    street: str,
    zip: str,
) -> None:
    db.add(
        Delivery(
            order_id=order_id,
            client_id=client_id,
            city=city,
            street=street,
            zip=zip,
            status=Delivery.STATUS_PENDING,
        )
    )
    await db.commit()

async def update_status(
    db: AsyncSession,
    order_id: int,
    status: str,
) -> None:
    await update_elements_statement_result(
        db=db,
        stmt=(
            update(Delivery)
                .where(Delivery.order_id == order_id)
                .values(status=status)
        )
    )
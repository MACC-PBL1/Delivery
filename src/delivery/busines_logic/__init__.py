from ..global_vars import RABBITMQ_CONFIG
from ..sql import (
    Delivery,
    update_status
)
from chassis.messaging import RabbitMQPublisher
from random import randint
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

logger = logging.getLogger(__name__)

async def delivery_process(
    db: AsyncSession,
    order_id: int,
) -> None:
    """
    Simulates a delivery process that runs in the background.
    """
    # Wait some time
    await asyncio.sleep(randint(5, 10))
    await update_status(db, order_id, Delivery.STATUS_DELIVERING)
    logger.info(f"[LOG:DELIVERY_PROCESS] - Order {order_id}: Delivering")
    
    # Wait again
    await asyncio.sleep(randint(5, 10))
    await update_status(db, order_id, Delivery.STATUS_DELIVERED)
    logger.info(f"[LOG:DELIVERY_PROCESS] - Order {order_id}: Delivered")

    with RabbitMQPublisher(
        queue="order.status.update",
        rabbitmq_config=RABBITMQ_CONFIG,
    ) as publisher:
        publisher.publish({
            "order_id": order_id,
            "status": Delivery.STATUS_DELIVERED,
        })
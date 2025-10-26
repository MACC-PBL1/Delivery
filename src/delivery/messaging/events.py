from .global_vars import (
    LISTENING_QUEUES,
    PUBLIC_KEY,
)
from ..sql.crud import (
    create_delivery,
    update_status
)
from chassis.messaging import (
    MessageType,
    register_queue_handler
)
from chassis.sql import SessionLocal
import logging

logger = logging.getLogger(__name__)

@register_queue_handler(LISTENING_QUEUES["create"])
async def event_create_delivery(message: MessageType) -> None:
    assert (order_id := message.get("order_id")) is not None, "'order_id' field should be present."
    assert (client_id := message.get("client_id")) is not None, "'client_id' field should be present."
    order_id = int(order_id)
    client_id = int(client_id)
    async with SessionLocal() as db:
        create_delivery(db, order_id, client_id)

@register_queue_handler(LISTENING_QUEUES["update_status"])
async def event_update_delivery_status(message: MessageType) -> None:
    assert (order_id := message.get("order_id")) is not None, "'order_id' field should be present."
    assert (status := message.get("status")) is not None, "'status' field should be present."
    order_id = int(order_id)
    async with SessionLocal() as db:
        await update_status(db, order_id, status)

@register_queue_handler(
    queue=LISTENING_QUEUES["public_key"],
    exchange="public_key",
    exchange_type="fanout"
)
def public_key(message: MessageType) -> None:
    global PUBLIC_KEY
    assert (public_key := message.get("public_key")) is not None, "'public_key' field should be present."
    PUBLIC_KEY = str(public_key)
    logging.info(f"Public key updated: {PUBLIC_KEY}")
from delivery.busines_logic import check_postal_code
from .global_vars import (
    LISTENING_QUEUES,
    PUBLIC_KEY,
)
from chassis.messaging import RabbitMQPublisher
from ..messaging import (
    PUBLISHING_QUEUES,
    RABBITMQ_CONFIG
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
from chassis.consul import ConsulClient 
import requests

logger = logging.getLogger(__name__)

@register_queue_handler(LISTENING_QUEUES["create"])
async def event_create_delivery(message: MessageType) -> None:
    logger.info(f"EVENT: Creation delivery --> Message: {message}")
    assert (order_id := message.get("order_id")) is not None, "'order_id' field should be present."
    assert (client_id := message.get("client_id")) is not None, "'client_id' field should be present."
    order_id = int(order_id)
    client_id = int(client_id)
    async with SessionLocal() as db:
        create_delivery(db, order_id, client_id)

@register_queue_handler(LISTENING_QUEUES["update_status"])
async def event_update_delivery_status(message: MessageType) -> None:
    logger.info(f"EVENT: Update delivery status --> Message: {message}")
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
    logger.info(f"EVENT: Public key updated: {message}")
    global PUBLIC_KEY

    assert "public_key" in message, "'public_key' field should be present."
    assert message["public_key"] == "AVAILABLE", (
        f"'public_key' value is '{message['public_key']}', expected 'AVAILABLE'"
    )

    consul = ConsulClient(logger)
    auth_base_url = consul.get_service_url("auth")
    if not auth_base_url:
        logger.error("The auth service couldn't be found")
        return

    target_url = f"{auth_base_url}/auth/key"

    response = requests.get(target_url, timeout=5)

    if response.status_code == 200:
        data = response.json()
        new_key = data.get("public_key")

        assert new_key is not None, (
            "Auth response did not contain expected 'public_key' field."
        )

        PUBLIC_KEY["key"] = str(new_key)
        logger.info("Public key updated")

    else:
        logger.warning(f"Auth answered with an error: {response.status_code}")


    
@register_queue_handler(
    queue=LISTENING_QUEUES["cmd"],
    exchange="cmd",
    exchange_type="topic"
)
def cmd(message: MessageType) -> None:
    logger.info(f"EVENT: cmd --> Message: {message}")
    assert (response_destination := message.get("response_destination")) is not None, "'response_destination' field should be present."
    assert (postal_code := message.get("postal_code")) is not None, "'postal_code' field should be present."
    with RabbitMQPublisher(
        queue=response_destination,
        rabbitmq_config=RABBITMQ_CONFIG,
    ) as publisher:
        publisher.publish({
            "status": check_postal_code(postal_code),
        })
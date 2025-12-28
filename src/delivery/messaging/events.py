from ..sql import Delivery

from ..global_vars import (
    LISTENING_QUEUES,
    PUBLIC_KEY,
    PUBLISHING_QUEUES,
    RABBITMQ_CONFIG,
)

from ..busines_logic import delivery_process
from ..sql.crud import (
    create_delivery,
    update_status,
    get_delivery_by_order,
)
from chassis.consul import ConsulClient 

from chassis.messaging import (
    MessageType, 
    RabbitMQPublisher,
    register_queue_handler,
)
from chassis.sql import SessionLocal
import logging
import requests

logger = logging.getLogger(__name__)

@register_queue_handler(LISTENING_QUEUES["create"])
async def event_create_delivery(message: MessageType) -> None:
    assert (order_id := message.get("order_id")) is not None, "'order_id' field should be present."
    assert (client_id := message.get("client_id")) is not None, "'client_id' field should be present."
    assert (city := message.get("city")) is not None, "'city' field should be present"
    assert (street := message.get("street")) is not None, "'street' field should be present"
    assert (zip := message.get("zip")) is not None, "'zip' field should be present"

    order_id = int(order_id)
    client_id = int(client_id)
    city = str(city)
    street = str(street)
    zip = str(zip)

    async with SessionLocal() as db:
        create_delivery(
            db=db, 
            order_id=order_id, 
            client_id=client_id,
            city=city,
            street=street,
            zip=zip,
        )

    logger.info(
        "[EVENT:DELIVERY:CREATED] - Delivery created: "
        f"order_id={order_id}, client_id={client_id}, city={city}, street={street}, zip={zip}"
    )

@register_queue_handler(LISTENING_QUEUES["update_status"])
async def event_update_delivery_status(message: MessageType) -> None:
    assert (order_id := message.get("order_id")) is not None, "'order_id' field should be present."
    assert (status := message.get("status")) is not None, "'status' field should be present."
    
    order_id = int(order_id)
    status = str(status)


    async with SessionLocal() as db:
        await update_status(db, order_id, status)

    # Beti izango da 'packaged', baino bueno oraingoz horrela
    if status == "packaged":
        async with SessionLocal() as db:
            await delivery_process(db, order_id)

    logger.info(
        "[EVENT:DELIVERY:STATUS_UPDATED] - Delivery status updated: "
        f"order_id={order_id}, status={status}"
    )


@register_queue_handler(LISTENING_QUEUES["delivery_cancel"])
async def delivery_cancel(message: MessageType) -> None:
    """
    Cancels a delivery if it has not been completed yet.
    """

    assert (order_id := message.get("order_id")) is not None, "'order_id' field required"
    order_id = int(order_id)

    logger.info(
        "[CMD:DELIVERY:CANCEL] - order_id=%s",
        order_id,
    )

    async with SessionLocal() as db:
        delivery = await get_delivery_by_order(db, order_id)

        if delivery is None:
            event_type = "delivery.not_found"

        elif delivery.status == Delivery.STATUS_DELIVERED:
            event_type = "delivery.cancel_rejected"

        elif delivery.status == Delivery.STATUS_CANCELLED:
            event_type = "delivery.cancelled"

        else:
            await update_status(db, order_id, Delivery.STATUS_CANCELLED)
            event_type = "delivery.cancelled"

        await db.commit()

    with RabbitMQPublisher(
        queue="",
        rabbitmq_config=RABBITMQ_CONFIG,
        exchange="evt",
        exchange_type="topic",
        routing_key=event_type,
    ) as publisher:
        publisher.publish({
            "order_id": order_id,
        })

    logger.info(
        "[EVENT:%s] - order_id=%s",
        event_type.upper(),
        order_id,
    )


@register_queue_handler(
    queue=LISTENING_QUEUES["public_key"],
    exchange="public_key",
    exchange_type="fanout"
)
def public_key(message: MessageType) -> None:
    global PUBLIC_KEY
    assert (auth_base_url := ConsulClient(logger).get_service_url("auth")) is not None, (
        "The 'auth' service should be accesible"
    )
    assert "public_key" in message, "'public_key' field should be present."
    assert message["public_key"] == "AVAILABLE", (
        f"'public_key' value is '{message['public_key']}', expected 'AVAILABLE'"
    )
    response = requests.get(f"{auth_base_url}/auth/key", timeout=5)
    assert response.status_code == 200, (
        f"Public key request returned '{response.status_code}', should return '200'"
    )
    data: dict = response.json()
    new_key = data.get("public_key")
    assert new_key is not None, (
        "Auth response did not contain expected 'public_key' field."
    )
    PUBLIC_KEY["key"] = str(new_key)
    logger.info(
        "[EVENT:PUBLIC_KEY:UPDATED] - Public key updated: "
        f"key={PUBLIC_KEY["key"]}"
    )
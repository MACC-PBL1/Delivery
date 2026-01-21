from ..global_vars import (
    LISTENING_QUEUES,
    PUBLIC_KEY,
    RABBITMQ_CONFIG,
)
from ..busines_logic import delivery_process
from ..sql.crud import (
    create_delivery,
    Delivery,
    get_delivery,
    update_status
)
from chassis.consul import CONSUL_CLIENT 
from chassis.messaging import (
    MessageType,
    RabbitMQPublisher,
    register_queue_handler
)
from chassis.sql import SessionLocal
import logging
import requests

logger = logging.getLogger(__name__)

@register_queue_handler(LISTENING_QUEUES["delivery_create"])
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
        await create_delivery(
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

@register_queue_handler(LISTENING_QUEUES["delivery_start"])
async def event_update_delivery_status(message: MessageType) -> None:
    assert (order_id := message.get("order_id")) is not None, "'order_id' field should be present."
    
    order_id = int(order_id)

    async with SessionLocal() as db:
        await update_status(db, order_id, Delivery.STATUS_PACKAGED)
        await delivery_process(db, order_id)

@register_queue_handler(
    queue=LISTENING_QUEUES["saga_reserve"],
    exchange="cmd",
    exchange_type="topic",
    routing_key="delivery.cancel"
)
async def delivery_cancel(message: MessageType) -> None:
    assert (order_id := message.get("order_id")) is not None, "'order_id' should exist"
    assert (response_exchange := message.get("response_exchange")) is not None, "'response_exchange' should exist"
    assert (response_exchange_type := message.get("response_exchange_type")) is not None, "'response_exchange_type' should exist"
    assert (response_routing_key := message.get("response_routing_key")) is not None, "'response_routing_key' should exist"

    order_id = int(order_id)
    response_exchange = str(response_exchange)
    response_exchange_type = str(response_exchange_type)
    response_routing_key = str(response_routing_key)
    response = {}

    logger.info(
        "[CMD:DELIVERY_CANCEL:RECEIVED] - Received cancel command: "
        f"order_id={order_id}"
    )

    async with SessionLocal() as db:
        assert (delivery := await get_delivery(db, order_id)) is not None, "Delivery should exist"
        if delivery.status in [Delivery.STATUS_PENDING, Delivery.STATUS_PACKAGED]:
            response["status"] = "OK"
            await update_status(db, order_id, Delivery.STATUS_CANCELLED)
            logger.info(
                "[CMD:DELIVERY_CANCEL:SUCCESS] - Delivery cancelled: "
                f"order_id={order_id}"
            )
        else:
            response["status"] = "FAIL"
            logger.info(
                "[CMD:DELIVERY_CANCEL:FAILED] - Delivery cancellation failed: "
                f"order_id={order_id}"
            )

    with RabbitMQPublisher(
        queue="",
        rabbitmq_config=RABBITMQ_CONFIG,
        exchange=response_exchange,
        exchange_type=response_exchange_type,
        routing_key=response_routing_key,
        auto_delete_queue=True,
    ) as publisher:
        publisher.publish(response)
        
@register_queue_handler(
    queue=LISTENING_QUEUES["public_key"],
    exchange="public_key",
    exchange_type="fanout"
)
def public_key(message: MessageType) -> None:
    global PUBLIC_KEY
    assert (auth_base_url := CONSUL_CLIENT.discover_service("auth")) is not None, (
        "The 'auth' service should be accesible"
    )
    assert "public_key" in message, "'public_key' field should be present."
    assert message["public_key"] == "AVAILABLE", (
        f"'public_key' value is '{message['public_key']}', expected 'AVAILABLE'"
    )
    address, port = auth_base_url
    response = requests.get(f"{address}:{port}/auth/key", timeout=5)
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
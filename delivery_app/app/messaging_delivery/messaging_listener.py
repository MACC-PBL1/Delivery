# -*- coding: utf-8 -*-
"""RabbitMQ listeners and publishers for Delivery Service."""
import aio_pika
import asyncio
import json
import logging
import os
from app.sql import crud, database, schemas

# Configuramos un logger específico para este módulo
logger = logging.getLogger(__name__)

# URL de conexión a RabbitMQ
RABBITMQ_URL = "amqp://user:password@rabbitmq:5672/"

# Variable global para mantener la conexión y el canal
_connection = None
_channel = None


# -------------------------------------------------------
# Función para obtener conexión y canal (singleton)
# -------------------------------------------------------
async def get_rabbitmq_channel():
    """Obtiene el canal de RabbitMQ, creándolo si no existe"""
    global _connection, _channel
    
    if _channel is None or _channel.is_closed:
        if _connection is None or _connection.is_closed:
            _connection = await aio_pika.connect_robust(RABBITMQ_URL)
        _channel = await _connection.channel()
        await _channel.set_qos(prefetch_count=1)
    
    return _channel


# -------------------------------------------------------
# Funciones para PUBLICAR mensajes
# -------------------------------------------------------
async def publish_to_order_update_status(order_id: int, status: str):
    """
    Publica un mensaje a la cola 'order.update_status'
    
    Args:
        order_id: ID del pedido
        status: Estado a actualizar (ej: 'delivered', 'in_transit')
    """
    try:
        channel = await get_rabbitmq_channel()
        
        message = {
            "order_id": order_id,
            "status": status
        }
        
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key="order.update_status"
        )
        
        logger.info(f"Published to order.update_status: {message}")
    except Exception as e:
        logger.error(f"Error publishing to order.update_status: {e}")


async def publish_client_refresh_public_key(data: dict = None):
    """
    Publica un mensaje a la cola 'client.refresh_public_key'
    
    Args:
        data: Datos adicionales a enviar (opcional)
    """
    try:
        channel = await get_rabbitmq_channel()
        
        message = data or {"action": "refresh_keys"}
        
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key="client.refresh_public_key"
        )
        
        logger.info(f"Published to client.refresh_public_key: {message}")
    except Exception as e:
        logger.error(f"Error publishing to client.refresh_public_key: {e}")


# -------------------------------------------------------
# Funciones para ESCUCHAR mensajes (consumers)
# -------------------------------------------------------
async def handle_delivery_create(message: aio_pika.IncomingMessage):
    """Maneja mensajes de creación de delivery"""
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            logger.info(f"Received delivery.create: {payload}")
            
            async with database.async_session() as session:
                delivery_data = schemas.DeliveryCreate(
                    order_id=payload["order_id"],
                    client_id=payload.get("client_id", 0),
                    address=""
                )
                await crud.create_delivery(session, delivery_data)
                logger.info(f"Delivery creado para order_id={payload['order_id']}")
        except Exception as e:
            logger.error(f"Error processing delivery.create: {e}")


async def handle_delivery_update_status(message: aio_pika.IncomingMessage):
    """Maneja mensajes de actualización de status"""
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            logger.info(f"Received delivery.update_status: {payload}")
            
            async with database.async_session() as session:
                # Buscar el delivery por order_id
                from sqlalchemy.future import select
                from app.sql.models import Delivery
                
                result = await session.execute(
                    select(Delivery).where(Delivery.order_id == payload["order_id"])
                )
                delivery = result.scalars().first()
                
                if delivery:
                    # Actualizar el status
                    await crud.update_delivery(
                        session, 
                        delivery.id, 
                        {"status": payload["status"]}
                    )
                    logger.info(f"Delivery status actualizado para order_id={payload['order_id']}")
                    
                    # Si el status es 'delivered', notificar a Order
                    if payload["status"] == "delivered":
                        await publish_to_order_update_status(
                            payload["order_id"], 
                            "completed"
                        )
                else:
                    logger.warning(f"Delivery not found for order_id={payload['order_id']}")
                    
        except Exception as e:
            logger.error(f"Error processing delivery.update_status: {e}")


# -------------------------------------------------------
# Función para iniciar los listeners de RabbitMQ
# -------------------------------------------------------
async def start_listeners():
    """Inicia los listeners de RabbitMQ"""
    global _connection, _channel
    
    # Conectar a RabbitMQ con reintentos
    for attempt in range(10):
        try:
            _connection = await aio_pika.connect_robust(RABBITMQ_URL)
            break
        except Exception as e:
            logger.warning(f"RabbitMQ no disponible ({e}), reintentando en 3s...")
            await asyncio.sleep(3)
    else:
        raise RuntimeError("No se pudo conectar a RabbitMQ después de varios intentos")

    # Crear canal
    _channel = await _connection.channel()
    await _channel.set_qos(prefetch_count=1)

    # Declarar y consumir de las colas
    queue_create = await _channel.declare_queue("delivery.create", durable=True)
    await queue_create.consume(handle_delivery_create)

    queue_update = await _channel.declare_queue("delivery.update_status", durable=True)
    await queue_update.consume(handle_delivery_update_status)

    logger.info("RabbitMQ listeners started for Delivery Service")
    
    return _connection
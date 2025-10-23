# -*- coding: utf-8 -*-
"""FastAPI router definitions for Delivery Service."""

# ----------------------------------------
# Imports
# ----------------------------------------
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql import crud, schemas
from app.dependencies import get_db
from pydantic import BaseModel

# ----------------------------------------
# Configurar logger
# ----------------------------------------
logger = logging.getLogger(__name__)

# ----------------------------------------
# Crear router principal
# ----------------------------------------
router = APIRouter()

# ------------------------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------------------------
@router.get(
    "/",
    summary="Health check endpoint",
    response_model=schemas.Message,
)
async def health_check():
    logger.debug("GET '/' endpoint called.")
    return {"detail": "OK"}

# ------------------------------------------------------------------------------------
# Deliveries endpoints
# ------------------------------------------------------------------------------------
@router.post(
    "/deliveries",
    response_model=schemas.DeliveryOut,
    summary="Create new delivery",
    status_code=status.HTTP_201_CREATED,
    tags=["Delivery"]
)
async def create_delivery(
    delivery: schemas.DeliveryCreate,
    db: AsyncSession = Depends(get_db)
):
    logger.debug("POST '/deliveries' endpoint called.")
    return await crud.create_delivery(db, delivery)

@router.get(
    "/deliveries",
    response_model=List[schemas.DeliveryOut],
    summary="Retrieve delivery list",
    tags=["Delivery", "List"]
)
async def get_delivery_list(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    logger.debug("GET '/deliveries' endpoint called.")
    return await crud.get_deliveries(db, skip=skip, limit=limit)

@router.get(
    "/deliveries/{delivery_id}",
    response_model=schemas.DeliveryOut,
    summary="Retrieve single delivery by id",
    tags=["Delivery"]
)
async def get_single_delivery(
    delivery_id: int,
    db: AsyncSession = Depends(get_db)
):
    logger.debug("GET '/deliveries/%i' endpoint called.", delivery_id)
    delivery = await crud.get_delivery(db, delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery {delivery_id} not found"
        )
    return delivery

@router.put(
    "/deliveries/{delivery_id}",
    response_model=schemas.DeliveryOut,
    summary="Update delivery by id",
    tags=["Delivery"]
)
async def update_delivery(
    delivery_id: int,
    delivery_update: schemas.DeliveryUpdate,
    db: AsyncSession = Depends(get_db)
):
    logger.debug("PUT '/deliveries/%i' endpoint called.", delivery_id)
    
    # Convertir el schema Pydantic a dict, eliminando None
    updates = delivery_update.model_dump(exclude_unset=True)
    
    delivery = await crud.update_delivery(db, delivery_id, updates)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery {delivery_id} not found"
        )
    return delivery

@router.delete(
    "/deliveries/{delivery_id}",
    summary="Delete delivery",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Message,
            "description": "Delivery successfully deleted."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message,
            "description": "Delivery not found"
        }
    },
    tags=["Delivery"]
)
async def delete_delivery(
    delivery_id: int,
    db: AsyncSession = Depends(get_db)
):
    logger.debug("DELETE '/deliveries/%i' endpoint called.", delivery_id)
    delivery = await crud.delete_delivery(db, delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery {delivery_id} not found"
        )
    return {"detail": f"Delivery {delivery_id} deleted"}

# ------------------------------------------------------------------------------------
# Endpoint para actualizar address y status
# ------------------------------------------------------------------------------------
class AddressPayload(BaseModel):
    address: str
    jwt: str

@router.post(
    "/address/{delivery_id}",
    response_model=schemas.DeliveryOut,
    summary="Update delivery address",
    tags=["Delivery"]
)
async def update_delivery_address(
    delivery_id: int,
    payload: AddressPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza el address de un delivery y cambia el status a 'delivering'.
    """
    # Validar JWT aquí si es necesario
    updates = {"address": payload.address, "status": "delivering"}
    delivery = await crud.update_delivery(db, delivery_id, updates)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery {delivery_id} not found"
        )
    return delivery


# ------------------------------------------------------------------------------------
# Endpoints de prueba para RabbitMQ
# ------------------------------------------------------------------------------------
@router.post(
    "/test/publish-to-order",
    summary="Test publishing to order.update_status queue",
    tags=["Testing", "RabbitMQ"]
)
async def test_publish_to_order(order_id: int, status: str = "delivered"):
    """
    Endpoint de prueba para publicar un mensaje a la cola 'order.update_status'
    """
    from app.messaging_delivery import messaging_listener
    
    await messaging_listener.publish_to_order_update_status(order_id, status)
    
    return {
        "detail": f"Message published to order.update_status",
        "order_id": order_id,
        "status": status
    }


@router.post(
    "/test/publish-refresh-key",
    summary="Test publishing to client.refresh_public_key queue",
    tags=["Testing", "RabbitMQ"]
)
async def test_publish_refresh_key():
    """
    Endpoint de prueba para publicar un mensaje a la cola 'client.refresh_public_key'
    """
    from app.messaging_delivery import messaging_listener
    
    await messaging_listener.publish_client_refresh_public_key()
    
    return {
        "detail": "Message published to client.refresh_public_key"
    }

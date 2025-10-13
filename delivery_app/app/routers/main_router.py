# -*- coding: utf-8 -*-
"""FastAPI router definitions for Delivery Service."""
import logging
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.sql import crud, schemas
from app.dependencies import get_db

# Configurar logger
logger = logging.getLogger(__name__)

# Crear router principal
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
    """Endpoint para verificar que el Delivery Service está activo."""
    logger.debug("GET '/' endpoint called.")
    return {"detail": "OK"}


# ------------------------------------------------------------------------------------
# Deliveries
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
    """Crea una nueva entrega (delivery)."""
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
    """Obtiene una lista de todas las entregas (con paginación)."""
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
    """Obtiene una entrega específica por su ID."""
    logger.debug("GET '/deliveries/%i' endpoint called.", delivery_id)
    delivery = await crud.get_delivery(db, delivery_id)
    if not delivery:
        return {"detail": f"Delivery {delivery_id} not found"}
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
    """Actualiza una entrega existente (dirección o estado)."""
    logger.debug("PUT '/deliveries/%i' endpoint called.", delivery_id)
    delivery = await crud.update_delivery(db, delivery_id, delivery_update)
    if not delivery:
        return {"detail": f"Delivery {delivery_id} not found"}
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
    """Elimina una entrega por su ID."""
    logger.debug("DELETE '/deliveries/%i' endpoint called.", delivery_id)
    delivery = await crud.delete_delivery(db, delivery_id)
    if not delivery:
        return {"detail": f"Delivery {delivery_id} not found"}
    return {"detail": f"Delivery {delivery_id} deleted"}
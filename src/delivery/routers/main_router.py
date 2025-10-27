from ..busines_logic import delivery_process
from ..messaging import PUBLIC_KEY
from ..sql import (
    Message,
    update_address
)
from chassis.security import create_jwt_verifier
from chassis.sql import get_db
from fastapi import (
    APIRouter, 
    Depends, 
)
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

# ----------------------------------------
# Configurar logger
# ----------------------------------------
logger = logging.getLogger(__name__)

# ----------------------------------------
# Crear router principal
# ----------------------------------------
Router = APIRouter(
    prefix="/deliveries",
    tags=["Delivery"],
)

# ------------------------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------------------------
@Router.get(
    "/",
    summary="Health check endpoint",
    response_model=Message,
)
async def health_check():
    logger.debug("GET '/' endpoint called.")
    return {"detail": "OK"}

@Router.get(
    "/health/auth",
    summary="Health check endpoint (JWT protected)",
)
async def health_check_auth(
    token_data: dict = Depends(create_jwt_verifier(lambda: PUBLIC_KEY["key"], logger))
):
    logger.debug("GET '/payment/auth' endpoint called.")
    user_id = token_data.get("sub")
    user_email = token_data.get("email")
    user_role = token_data.get("role")

    logger.info(f" Valid JWT: user_id={user_id}, email={user_email}, role={user_role}")

    return {
        "detail": f"Order service is running. Authenticated as {user_email} (id={user_id}, role={user_role})"
    }


# ------------------------------------------------------------------------------------
# Address
# ------------------------------------------------------------------------------------
@Router.post(
    "/address",
    summary="Add address for delivery",
)
async def address(
    order_id: int,
    address: str,
    token_data: dict = Depends(create_jwt_verifier(lambda: PUBLIC_KEY["key"], logger)),
    db: AsyncSession = Depends(get_db),
) -> None:
    logger.debug(
        "POST '/deposit' endpoint called:\n",
        "\tParams:\n",
        f"\t\t- 'order_id': {order_id}",
        f"\t\t- 'address': {address}"
    )
    # Guardar address
    await update_address(db, order_id, address)
    asyncio.create_task(delivery_process(db, order_id))
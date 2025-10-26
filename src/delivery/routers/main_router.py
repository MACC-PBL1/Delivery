from ..busines_logic import delivery_process
from ..messaging import PUBLIC_KEY
from ..sql import (
    Message,
    update_address
)
from chassis.sql import get_db
from chassis.routers import raise_and_log_error
from fastapi import (
    APIRouter, 
    Depends, 
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import asyncio
import jwt
import logging

# ----------------------------------------
# Configurar logger
# ----------------------------------------
logger = logging.getLogger(__name__)

# ----------------------------------------
# Crear router principal
# ----------------------------------------
router = APIRouter()
Bearer = HTTPBearer()

def create_jwt_verifier(public_key: Optional[str], algorithm: str = "RS256"):
    """
    Factory function to create a JWT verifier with a specific public key.
    """
    def verify_token(credentials: HTTPAuthorizationCredentials = Depends(Bearer)):
        try:
            assert PUBLIC_KEY is not None, "'PUBLIC_KEY' is None"
            payload = jwt.decode(
                credentials.credentials,
                public_key,
                algorithms=[algorithm]
            )
            return payload
        except jwt.InvalidTokenError:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, "Invalid token")
        except Exception as e:
            raise_and_log_error(logger, status.HTTP_500_INTERNAL_SERVER_ERROR, f"Internal error: {e}")
    
    return verify_token

# Create the verifier with your public key
verify_token = create_jwt_verifier(PUBLIC_KEY)

# ------------------------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------------------------
@router.get(
    "/",
    summary="Health check endpoint",
    response_model=Message,
)
async def health_check():
    logger.debug("GET '/' endpoint called.")
    return {"detail": "OK"}

# ------------------------------------------------------------------------------------
# Address
# ------------------------------------------------------------------------------------
@router.post(
    "/address",
    summary="Add address for delivery",
)
async def address(
    order_id: int,
    address: str,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> None:
    # Guardar address
    await update_address(db, order_id, address)
    asyncio.create_task(delivery_process(db, order_id))
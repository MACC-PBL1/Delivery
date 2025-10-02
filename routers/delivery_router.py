#Define las URL y metodos que los usuarios o sistemas externos puedan llamar.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.sql import schemas, crud
from app.dependencies import get_db

router = APIRouter(
    prefix="/delivery",
    tags=["Delivery"]
)

@router.post("/", response_model=schemas.Delivery)
async def provide_delivery_info(delivery: schemas.DeliveryCreate, db: AsyncSession = Depends(get_db)):
    """
    4. Provide delivery info
    """
    new_delivery = await crud.create_delivery(db, delivery)
    return new_delivery


@router.get("/{delivery_id}", response_model=schemas.Delivery)
async def get_delivery(delivery_id: int, db: AsyncSession = Depends(get_db)):
    delivery = await crud.get_delivery(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.patch("/{delivery_id}/status", response_model=schemas.Delivery)
async def update_delivery_status(delivery_id: int, status: str, db: AsyncSession = Depends(get_db)):
    """
    3.5 Update delivery status
    """
    updated = await crud.update_delivery_status(db, delivery_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Delivery not found or not updated")
    return updated
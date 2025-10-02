from fastapi import FastAPI
from app.routers import main_router, delivery_router

app = FastAPI()

app.include_router(main_router.router)
app.include_router(delivery_router.router)

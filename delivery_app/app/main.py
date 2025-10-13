# -*- coding: utf-8 -*-
"""Archivo principal para arrancar el microservicio Delivery con FastAPI."""

import logging
import os
from fastapi import FastAPI
from app.sql import models, database
from app.routers import main_router

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear instancia de FastAPI
app = FastAPI(
    title="Delivery Service",
    description="Microservicio para gestionar entregas (CRUD Delivery).",
    version=os.getenv("APP_VERSION", "1.0.0"),
)

# Incluir el router de Delivery con prefijo /delivery
app.include_router(main_router.router, prefix="/delivery", tags=["Delivery"])

# ------------------------------------------------------------------------------------
# Lifespan events
# ------------------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup():
    """Evento que se ejecuta al iniciar la app: crea tablas si no existen."""
    logger.info("Iniciando Delivery Service...")
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    logger.info("Tablas de la base de datos creadas.")

@app.on_event("shutdown")
async def on_shutdown():
    """Evento que se ejecuta al apagar la app: libera recursos."""
    logger.info("Cerrando Delivery Service...")
    await database.engine.dispose()

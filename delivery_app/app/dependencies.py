# -*- coding: utf-8 -*-
"""Application dependency injector."""

import logging
from app.sql.database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

MY_MACHINE = None

# Database #########################################################################################
async def get_db() -> AsyncSession: # type: ignore
    """
    Genera sesiones de DB y las cierra al terminar.
    Resiliente a fallos: si hay error, hace rollback y lo registra.
    """
    try:
        async with SessionLocal() as db:  # context manager async
            try:
                yield db
                await db.commit()
            except SQLAlchemyError as e:
                await db.rollback()
                logger.error("DB operation failed: %s", e)
                raise
    except SQLAlchemyError as e:
        # Esto captura fallos de conexión inicial a la DB
        logger.warning("No se pudo conectar a la base de datos: %s", e)
        # Aquí no propagamos el error para que el servicio siga vivo
        # pero cualquier endpoint que use la DB fallará
        # Si quieres, puedes devolver un objeto 'mock' o None
        class DummySession:
            async def execute(self, *args, **kwargs):
                raise SQLAlchemyError("DB no disponible")
        yield DummySession()


# asyncio.create_task(get_machine())
# asyncio.run(init_machine())

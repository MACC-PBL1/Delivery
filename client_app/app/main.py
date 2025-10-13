# -*- coding: utf-8 -*-
"""Configuración de la sesión y motor de base de datos (SQLAlchemy Async)."""
import os
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# URL de la base de datos (por defecto, una base SQLite llamada delivery.db)
SQLALCHEMY_DATABASE_URL = os.getenv(
    'SQLALCHEMY_DATABASE_URL',
    "sqlite+aiosqlite:///./delivery.db" 
)

# Crear el motor asíncrono para conectarse a la base de datos
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Cambia a True para ver las consultas SQL en consola
)

# Crear la sesión asíncrona
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    future=True
)

# Clase base de la que heredarán todos los modelos
Base = declarative_base()


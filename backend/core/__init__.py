# core/__init__.py

"""
Módulo core: Configuración central y base de datos.
una explicacion mas grande es:aqui se encuentran las configuraciones globales de la aplicación
es modulo core también maneja la conexión a la base de datos y la creación de tablas.
y las variables y funciones principales para interactuar con la base de datos.
"""

from .config import settings
from .data_base import engine, create_db_and_tables, get_session

__all__ = [
    "settings",
    "engine",
    "create_db_and_tables",
    "get_session"
]

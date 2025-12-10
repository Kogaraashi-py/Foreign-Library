 # api/__init__.py

"""
Módulo api: Endpoints HTTP organizados por recurso.
"""

from .genres import router as genres_router
from .novels import router as novels_router
from .chapters import router as chapters_router
from .scraping import router as scraping_router

__all__ = [
    "genres_router",
    "novels_router",
    "chapters_router",
    "scraping_router"
]

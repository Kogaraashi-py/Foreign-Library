# main.py

"""
Punto de entrada de la aplicación FastAPI.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# IMPORTS DESDE CORE
# ═══════════════════════════════════════════════════════════════
from core.config import settings
from core.data_base import create_db_and_tables
# ═══════════════════════════════════════════════════════════════
# IMPORTS DE ROUTERS
# ═══════════════════════════════════════════════════════════════

from api import genres_router, novels_router, chapters_router,scraping_router


# ═══════════════════════════════════════════════════════════════
# LIFESPAN: Startup y Shutdown
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    
    Startup:
    - Crea todas las tablas en la BD
    
    Shutdown:
    - Limpieza (por ahora vacío)
    """
    # STARTUP
    print("🚀 Iniciando aplicación...")
    print("📊 Creando tablas en base de datos...")
    create_db_and_tables()
    print("✅ Base de datos lista")
    
    yield  # Aquí la app corre
    
    # SHUTDOWN
    print("👋 Cerrando aplicación...")


# ═══════════════════════════════════════════════════════════════
# CREAR APLICACIÓN
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="API de Novelas",
    description="API para gestionar novelas, capítulos y géneros literarios",
    version="1.0.0",
    root_path=settings.API_V1_PREFIX,  # Todas las rutas con /api/v1
    lifespan=lifespan
)


# ═══════════════════════════════════════════════════════════════
# INCLUIR ROUTERS
# ═══════════════════════════════════════════════════════════════

app.include_router(genres_router)
# Agrega todos los endpoints de api/genres.py
# - GET /api/v1/genres/
# - POST /api/v1/genres/
# - etc.

app.include_router(novels_router)
# Agrega todos los endpoints de api/novels.py
# - GET /api/v1/novels/
# - GET /api/v1/novels/{id}
# - etc.

app.include_router(chapters_router)
# Agrega todos los endpoints de api/chapters.py
# - GET /api/v1/novels/{id}/chapters
# - GET /api/v1/chapters/{id}
# - etc.

app.include_router(scraping_router)


# ═══════════════════════════════════════════════════════════════
# ENDPOINT RAÍZ (Health Check)
# ═══════════════════════════════════════════════════════════════

@app.get("/", tags=["health"])
def health_check():
    """
    Endpoint de verificación.
    
    Útil para:
    - Verificar que la API está viva
    - Health checks de servicios de deployment
    - Testing básico
    """
    return {
        "status": "ok",
        "message": "API de Novelas funcionando correctamente",
        "version": "1.0.0",
        "docs": "/docs"  # Enlace a documentación Swagger
    }


# ═══════════════════════════════════════════════════════════════
# ENDPOINT DE INFORMACIÓN
# ═══════════════════════════════════════════════════════════════

@app.get("/info", tags=["health"])
def api_info():
    """
    Información general de la API.
    """
    return {
        "name": "API de Novelas",
        "version": "1.0.0",
        "endpoints": {
            "genres": "/genres",
            "novels": "/novels",
            "chapters": "/chapters"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


# ═══════════════════════════════════════════════════════════════
# MONTAR ARCHIVOS ESTÁTICOS
# ═══════════════════════════════════════════════════════════════

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ═══════════════════════════════════════════════════════════════
# ENDPOINT MANUAL PARA IMÁGENES (fallback)
# ═══════════════════════════════════════════════════════════════

from fastapi.responses import FileResponse

@app.get("/images/{filename}")
async def get_image(filename: str):
    """
    Endpoint manual para servir imágenes.
    Fallback si StaticFiles no funciona.
    """
    file_path = Path("static/novels") / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Image not found")

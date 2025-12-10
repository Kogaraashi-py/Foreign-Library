 # ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field, HttpUrl
# HttpUrl: Validador específico para URLs

from datetime import datetime
from typing import List
# List: Para listas tipadas

from models.novel import NovelStatus
# Importar el Enum para reutilizarlo

#importar esquemas relacionados 
from schemas import GenreResponse,NovelNameResponse



# ═══════════════════════════════════════════════════════════════
# SCHEMA BASE
# ═══════════════════════════════════════════════════════════════

class NovelBase(BaseModel):
    """
    Campos comunes que se usan en create/update/response.
    
    ¿Qué va aquí?
    - Campos que el usuario puede modificar
    - Campos que se devuelven siempre
    - NO van: id, created_at, cover_path (se generan automáticamente)
    """
    
    name: str = Field(min_length=1, max_length=200)
    # Nombre principal de la novela
    # min_length=1: No puede estar vacío
    # max_length=200: Coincide con BD
    
    author: str = Field(min_length=1, max_length=200)
    # Autor de la novela
    # ¿Por qué obligatorio?
    # - Toda novela tiene autor
    # - Si es anónimo, se pone "Unknown"
    
    rating: float | None = Field(default=None, ge=0, le=10)
    # float | None: Puede ser número o None (nulo)
    # default=None: Si no se envía, es None
    # ge=0: Greater or Equal (mayor o igual a 0)
    # le=10: Less or Equal (menor o igual a 10)
    # ¿Por qué opcional?
    # - Novelas nuevas no tienen rating
    # - Se calcula después con reviews
    
    status: NovelStatus = Field(default=NovelStatus.ongoing)
    # NovelStatus: Tipo Enum (solo acepta valores definidos)
    # default=ongoing: Por defecto es "ongoing"
    # ¿Por qué?
    # - La mayoría de novelas inician como "ongoing"
    # - Puedes cambiar después a "completed", etc.


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA CREAR
# ═══════════════════════════════════════════════════════════════

class NovelCreate(NovelBase):
    """
    Schema para CREAR una novela.
    
    ¿Cuándo se usa?
    POST /novels/
    Body: {
        "name": "Lord of the Mysteries",
        "author": "Cuttlefish",
        "description": "...",
        "status": "ongoing"
    }
    
    ¿Qué NO incluye?
    - id: Se autogenera
    - cover_path: Se sube después con POST /novels/5/cover
    - created_at: Se genera automáticamente
    - genres: Se asocian después con POST /novels/5/genres
    - alternative_names: Se agregan después
    """
    
    description: str = Field(max_length=5000)
    # max_length=5000: Coincide con BD
    # ¿Por qué obligatorio aquí?
    # - Toda novela debe tener descripción al crearse
    # - Si después la hacemos opcional, usamos NovelUpdate
    
    source_url: str | None = Field(default=None, max_length=500)
    # URL de donde se extrajo (para scraping)
    # Opcional: Si la creas manualmente, no tiene source_url


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA ACTUALIZAR
# ═══════════════════════════════════════════════════════════════

class NovelUpdate(BaseModel):
    """
    Schema para ACTUALIZAR una novela.
    
    ¿Cuándo se usa?
    PUT /novels/5
    Body: {"rating": 9.5, "status": "completed"}
    
    ¿Por qué todos los campos son opcionales?
    - Actualización PARCIAL (PATCH behavior)
    - Solo envías lo que quieres cambiar
    - Si envías {}, no cambia nada
    """
    
    name: str | None = Field(default=None, min_length=1, max_length=200)
    # Opcional: Solo si quieres cambiar el nombre
    
    author: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    rating: float | None = Field(default=None, ge=0, le=10)
    status: NovelStatus | None = None
    source_url: str | None = Field(default=None, max_length=500)
    
    # ¿Qué NO se puede actualizar?
    # - id: Nunca cambia
    # - created_at: Es histórico
    # - cover_path: Se actualiza con endpoint específico


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA RESPUESTA SIMPLE
# ═══════════════════════════════════════════════════════════════

class NovelResponse(NovelBase):
    """
    Schema para DEVOLVER una novela (sin relaciones).

    ¿Cuándo se usa?
    - GET /novels/ → List[NovelResponse] (listado simple)
    - POST /novels/ → NovelResponse (después de crear)

    ¿Por qué SIN relaciones?
    - Más rápido (no hace JOIN en BD)
    - Para listados donde no necesitas todo
    """

    id: int
    # ID de la novela

    description: str
    # Puede ser None si no se guardó

    cover_path: str | None
    # Ruta de la imagen (/static/novels/5.jpg)
    # None si no tiene portada

    cover_url: str | None
    # URL COMPLETA de la imagen (http://localhost:8000/static/novels/5.webp)
    # None si no tiene portada

    source_url: str | None
    # URL original (si viene de scraping)

    created_at: datetime
    # ¿Por qué 'created_at' y no 'create_at'?
    # - Aquí corregimos el typo del modelo
    # - En el endpoint hacemos: created_at = novel_db.create_at

    updated_at: datetime
    # Última actualización

    class Config:
        from_attributes = True
        # Permite: NovelResponse.from_orm(novel_db)


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA RESPUESTA COMPLETA (con relaciones)
# ═══════════════════════════════════════════════════════════════

class NovelDetailResponse(NovelResponse):
    """
    Schema para DEVOLVER una novela CON sus relaciones.
    
    ¿Cuándo se usa?
    GET /novels/5 → NovelDetailResponse (detalle completo)
    
    ¿Por qué separado de NovelResponse?
    - Listados usan NovelResponse (más rápido)
    - Detalle usa NovelDetailResponse (más completo)
    """
    
    genres: List[GenreResponse] = []
    # Lista de géneros de la novela
    # List[GenreResponse]: Cada género incluye id y name
    # default=[]: Si no tiene géneros, lista vacía
    # 
    # Ejemplo:
    # {
    #   "id": 5,
    #   "name": "Lord of Mysteries",
    #   "genres": [
    #     {"id": 1, "name": "fantasy"},
    #     {"id": 2, "name": "mystery"}
    #   ]
    # }
    
    alternative_names: List[NovelNameResponse] = []
    # Lista de nombres alternativos
    # default=[]: Si no tiene, lista vacía
    # 
    # Ejemplo:
    # "alternative_names": [
    #   {"id": 1, "novel_id": 5, "name": "诡秘之主"},
    #   {"id": 2, "novel_id": 5, "name": "Mystery Lord"}
    # ]
    
    chapters_count: int = 0
    # Cantidad de capítulos
    # ¿Por qué no List[Chapter]?
    # - Sería muy pesado (1000+ capítulos)
    # - Solo devolvemos el conteo
    # - Los capítulos se piden con GET /novels/5/chapters


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA ASOCIAR GÉNEROS
# ═══════════════════════════════════════════════════════════════

class NovelGenresUpdate(BaseModel):
    """
    Schema para ASOCIAR géneros a una novela.
    
    ¿Cuándo se usa?
    POST /novels/5/genres
    Body: {"genre_ids": [1, 2, 3]}
    
    ¿Por qué?
    - Necesitas un endpoint para agregar/quitar géneros
    - No se hace en NovelCreate para simplicidad
    """
    
    genre_ids: List[int] = Field(min_length=1)  # ✅ CorrectoLista de IDs de géneros
    # min_length=1: Al menos un género
    # 
    # Proceso:
    # 1. Validas que todos los IDs existen en BD
    # 2. Creas registros en NovelGender
    # 3. Devuelves la novela actualizada



# Schema NUEVO para homepage
class NovelCardResponse(BaseModel):
    """Para mostrar tarjetas en homepage"""
    id: int
    name: str
    author: str
    cover_path: str | None
    rating: float | None
    genres: List[str]  # ← Solo nombres, no objetos completos
    chapters_count: int
    class Config:
       from_attributes = True 
    # NO incluye: description completa (solo excerpt)
    # NO incluye: alternative_names
    # NO incluye: dates

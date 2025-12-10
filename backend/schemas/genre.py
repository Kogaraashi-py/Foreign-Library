 # ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field
# BaseModel: Clase base de Pydantic para validación
# Field: Define metadatos y validaciones de campos

from datetime import datetime
# Para tipar campos de fecha

# ═══════════════════════════════════════════════════════════════
# SCHEMA BASE
# ═══════════════════════════════════════════════════════════════

class GenreBase(BaseModel):
    """
    Schema base con campos comunes de género.
    
    ¿Por qué existe?
    - Evita repetir 'name' en múltiples clases
    - Herencia: GenreCreate y GenreResponse heredan de aquí
    """
    
    name: str = Field(min_length=1, max_length=100)
    # str: Tipo de dato (texto)
    # Field(min_length=1): No puede estar vacío
    # Field(max_length=100): Máximo 100 caracteres (igual que en modelo)
    # 
    # ¿Por qué estas validaciones?
    # - min_length=1: Evita géneros vacíos ""
    # - max_length=100: Coincide con la restricción de BD


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA CREAR
# ═══════════════════════════════════════════════════════════════

class GenreCreate(GenreBase):
    """
    Schema para CREAR un género.
    
    ¿Cuándo se usa?
    POST /genres/
    Body: {"name": "fantasy"}
    
    ¿Por qué solo hereda de GenreBase?
    - Solo necesita el campo 'name'
    - El 'id' se autogenera en BD
    - No hay otros campos que enviar
    """
    pass  # Solo hereda 'name' de GenreBase


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA RESPUESTA
# ═══════════════════════════════════════════════════════════════

class GenreResponse(GenreBase):
    """
    Schema para DEVOLVER un género al cliente.
    
    ¿Cuándo se usa?
    - GET /genres/ → devuelve List[GenreResponse]
    - GET /genres/5 → devuelve GenreResponse
    - POST /genres/ → después de crear, devuelve GenreResponse
    
    ¿Por qué agrega 'id'?
    - El cliente necesita saber el ID para futuras operaciones
    - Ejemplo: Si crea "fantasy", la respuesta incluye {"id": 1, "name": "fantasy"}
    """
    
    id: int
    # int: Tipo entero
    # Sin Field: No necesita validaciones (viene de BD, siempre es válido)
    # No tiene default: Es obligatorio (siempre existe en BD)
    
    class Config:
        from_attributes = True
        # ¿Qué hace esto?
        # - Permite convertir objetos SQLModel a Pydantic
        # - Sin esto, Pydantic solo acepta diccionarios
        # 
        # Ejemplo:
        # genre_db = Genre(id=1, name="fantasy")  ← Objeto SQLModel
        # response = GenreResponse.from_orm(genre_db)  ← Convierte a schema
        #
        # FastAPI hace esto automáticamente cuando usas response_model

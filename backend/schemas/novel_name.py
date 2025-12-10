 # ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════
# SCHEMA BASE
# ═══════════════════════════════════════════════════════════════

class NovelNameBase(BaseModel):
    """
    Schema base para nombres alternativos.
    
    ¿Por qué 'name' es el único campo común?
    - 'novel_id' solo se envía al crear
    - 'id' solo se devuelve en respuestas
    """
    
    name: str = Field(min_length=1, max_length=200)
    # Validación igual que en modelo (max_length=200)


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA CREAR
# ═══════════════════════════════════════════════════════════════

class NovelNameCreate(NovelNameBase):
    """
    Schema para CREAR un nombre alternativo.
    
    ¿Cuándo se usa?
    POST /novels/5/alternative-names
    Body: {"name": "诡秘之主"}
    
    ¿Por qué NO incluye 'novel_id'?
    - Porque viene en la URL: /novels/{novel_id}/alternative-names
    - El endpoint lo extrae del path parameter
    - Evita inconsistencias (URL dice novel_id=5, body dice novel_id=3)
    """
    pass  # Solo necesita 'name'


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA RESPUESTA
# ═══════════════════════════════════════════════════════════════

class NovelNameResponse(NovelNameBase):
    """
    Schema para DEVOLVER un nombre alternativo.
    
    ¿Cuándo se usa?
    GET /novels/5/alternative-names → List[NovelNameResponse]
    """
    
    id: int
    # ID del nombre alternativo (no de la novela)
    
    novel_id: int
    # ¿Por qué incluir novel_id en la respuesta?
    # - Para saber a qué novela pertenece
    # - Útil si el cliente maneja múltiples novelas
    
    class Config:
        from_attributes = True

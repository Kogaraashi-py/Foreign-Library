 # ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# SCHEMA BASE
# ═══════════════════════════════════════════════════════════════

class ChapterBase(BaseModel):
    """Campos comunes de capítulo."""
    
    title: str = Field(min_length=1, max_length=300)
    # Título del capítulo (ej: "Chapter 1: The Beginning")
    
    order_number: int = Field(ge=1)
    # Número de orden (1, 2, 3...)
    # ge=1: Mínimo 1 (no hay capítulo 0)


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA CREAR
# ═══════════════════════════════════════════════════════════════

class ChapterCreate(ChapterBase):
    """
    Schema para CREAR un capítulo.
    
    POST /novels/5/chapters
    Body: {
        "title": "Chapter 1",
        "content": "Once upon a time...",
        "order_number": 1
    }
    
    ¿Por qué NO incluye novel_id?
    - Viene en la URL: /novels/{novel_id}/chapters
    """
    
    content: str
    # Contenido completo del capítulo
    # Sin max_length: Puede ser muy largo (50k+ palabras)
    
    source_url: str | None = Field(default=None, max_length=500)
    # URL original (si viene de scraping)


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA RESPUESTA (sin contenido)
# ═══════════════════════════════════════════════════════════════

class ChapterSummary(ChapterBase):
    """
    Schema para LISTAR capítulos (sin contenido).
    
    GET /novels/5/chapters → List[ChapterSummary]
    
    ¿Por qué sin contenido?
    - Listados de 1000+ capítulos
    - Solo necesitas título y número
    - El contenido se pide individualmente
    """
    
    id: int
    novel_id: int
    created_at: datetime
    
    # NO incluye 'content' (se pide con GET /chapters/123)
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA RESPUESTA (con contenido)
# ═══════════════════════════════════════════════════════════════

class ChapterDetailResponse(ChapterBase):
    """
    Schema para LEER un capítulo completo.
    
    GET /chapters/123 → ChapterDetailResponse
    """
    
    id: int
    novel_id: int
    content: str  # ← Incluye contenido completo
    source_url: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True

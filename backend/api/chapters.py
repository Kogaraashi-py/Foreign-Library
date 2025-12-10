 # ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException, Path
# APIRouter: Para agrupar endpoints de capítulos
# HTTPException: Para errores HTTP (404, 400, etc.)
# Path: Para documentar path parameters (opcional, mejora docs)

from typing import List
# List: Para tipar listas

from sqlmodel import select
# select: Construir queries SQL

from datetime import datetime
# Para timestamps

from api.deps import session_dep
# Dependencia de sesión de BD

from models.novel import Novel
from models.chapter import Chapter
# Modelo de BD de capítulos
# Para verificar que la novela existe

from schemas import (
    ChapterCreate,
    ChapterSummary,
    ChapterDetailResponse
)
# Schemas de validación


# ═══════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════

router = APIRouter(tags=["chapters"])
# ¿Por qué SIN prefix?
# - Tenemos dos tipos de rutas:
#   1. /novels/{novel_id}/chapters (relacionada con novela)
#   2. /chapters/{chapter_id} (independiente)
# - Es más flexible definir cada ruta completa


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 1: Listar capítulos de una novela (sin contenido)
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/novels/{novel_id}/chapters",
    response_model=List[ChapterSummary],
    summary="Listar capítulos de una novela"
)
def list_novel_chapters(
    session: session_dep,
    novel_id: int = Path(..., description="ID de la novela", gt=0),
    # Path(...): Documentar parámetro en Swagger
    # gt=0: Greater than 0 (mayor que 0)
    
    skip: int = 0,
    limit: int = 100
):
    """
    Lista todos los capítulos de una novela específica.
    
    **NO incluye el contenido completo** (solo metadatos).
    Para leer el contenido, usar GET /chapters/{chapter_id}
    
    - **novel_id**: ID de la novela
    - **skip**: Capítulos a saltar (paginación)
    - **limit**: Máximo de capítulos a devolver
    
    Ejemplo: GET /novels/5/chapters?skip=0&limit=50
    """
    
    # ───────────────────────────────────────────────────────────
    # PASO 1: Verificar que la novela existe
    # ───────────────────────────────────────────────────────────
    novel = session.get(Novel, novel_id)
    
    if not novel:
        raise HTTPException(
            status_code=404,
            detail=f"Novela con ID {novel_id} no encontrada"
        )
    # ¿Por qué verificar?
    # - Si pides capítulos de novela 999 que no existe, debe dar 404
    # - No devolver lista vacía (confuso para el cliente)
    
    # ───────────────────────────────────────────────────────────
    # PASO 2: Buscar capítulos ordenados por número
    # ───────────────────────────────────────────────────────────
    statement = (
        select(Chapter)
        .where(Chapter.novel_id == novel_id)
        .order_by(Chapter.order_number)  # Orden: 1, 2, 3... # pyright: ignore[reportArgumentType]
        .offset(skip)
        .limit(limit)
    )
    # ¿Por qué order_by?
    # - Los capítulos deben mostrarse en orden correcto
    # - Chapter.order_number = 1 (primer capítulo)
    
    chapters = session.exec(statement).all()
    
    # ───────────────────────────────────────────────────────────
    # PASO 3: Devolver lista (FastAPI convierte a ChapterSummary)
    # ───────────────────────────────────────────────────────────
    return chapters
    # ChapterSummary NO incluye 'content' → respuesta ligera
    # Útil para mostrar lista de 1000+ capítulos


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 2: Leer UN capítulo completo (con contenido)
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/chapters/{chapter_id}",
    response_model=ChapterDetailResponse,
    summary="Leer un capítulo"
)
def get_chapter(
    session: session_dep,
    chapter_id: int = Path(..., description="ID del capítulo", gt=0),
):
    """
    Obtiene el contenido completo de un capítulo.
    
    **Incluye el texto completo** para lectura.
    
    - **chapter_id**: ID del capítulo a leer
    
    Ejemplo: GET /chapters/123
    """
    
    # ───────────────────────────────────────────────────────────
    # PASO 1: Buscar capítulo
    # ───────────────────────────────────────────────────────────
    chapter = session.get(Chapter, chapter_id)
    
    if not chapter:
        raise HTTPException(
            status_code=404,
            detail=f"Capítulo con ID {chapter_id} no encontrado"
        )
    
    # ───────────────────────────────────────────────────────────
    # PASO 2: Devolver capítulo completo
    # ───────────────────────────────────────────────────────────
    return chapter
    # ChapterDetailResponse INCLUYE 'content' → respuesta pesada
    # Solo se usa cuando el usuario quiere LEER el capítulo


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 3: Crear capítulo manualmente
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/novels/{novel_id}/chapters",
    response_model=ChapterDetailResponse,
    status_code=201,
    summary="Crear capítulo"
)
def create_chapter(
    session: session_dep,
    chapter_data: ChapterCreate ,
    novel_id: int = Path(..., description="ID de la novela", gt=0),
):
    """
    Crea un nuevo capítulo para una novela.
    
    Body ejemplo:
```json
    {
      "title": "Chapter 1: The Beginning",
      "content": "Once upon a time...",
      "order_number": 1,
      "source_url": "https://..."
    }
```
    
    - **novel_id**: ID de la novela a la que pertenece
    - **chapter_data**: Datos del capítulo
    """
    
    # ───────────────────────────────────────────────────────────
    # PASO 1: Verificar que la novela existe
    # ───────────────────────────────────────────────────────────
    novel = session.get(Novel, novel_id)
    
    if not novel:
        raise HTTPException(
            status_code=404,
            detail=f"Novela con ID {novel_id} no encontrada"
        )
    
    # ───────────────────────────────────────────────────────────
    # PASO 2: Verificar que no exista capítulo con ese número
    # ───────────────────────────────────────────────────────────
    existing = session.exec(
        select(Chapter)
        .where(Chapter.novel_id == novel_id)
        .where(Chapter.order_number == chapter_data.order_number)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un capítulo {chapter_data.order_number} para esta novela"
        )
    # ¿Por qué verificar?
    # - No puede haber dos "Capítulo 5" en la misma novela
    # - order_number debe ser único por novela
    
    # ───────────────────────────────────────────────────────────
    # PASO 3: Crear capítulo
    # ───────────────────────────────────────────────────────────
    chapter = Chapter(
        novel_id=novel_id,
        title=chapter_data.title,
        content=chapter_data.content,
        order_number=chapter_data.order_number,
        source_url=chapter_data.source_url,
        created_at=datetime.now()
    )
    
    # ───────────────────────────────────────────────────────────
    # PASO 4: Guardar en BD
    # ───────────────────────────────────────────────────────────
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    # refresh: Obtener ID autogenerado
    
    return chapter


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 4: Actualizar capítulo
# ═══════════════════════════════════════════════════════════════

@router.put(
    "/chapters/{chapter_id}",
    response_model=ChapterDetailResponse,
    summary="Actualizar capítulo"
)
def update_chapter(
    chapter_data: ChapterCreate,  # Reutilizamos ChapterCreate
    session: session_dep,
    chapter_id: int = Path(..., description="ID del capítulo", gt=0),
):
    """
    Actualiza el contenido de un capítulo existente.
    
    Body ejemplo:
```json
    {
      "title": "Chapter 1: The Real Beginning",
      "content": "Updated content...",
      "order_number": 1
    }
```
    """
    
    # ───────────────────────────────────────────────────────────
    # PASO 1: Buscar capítulo
    # ───────────────────────────────────────────────────────────
    chapter = session.get(Chapter, chapter_id)
    
    if not chapter:
        raise HTTPException(
            status_code=404,
            detail=f"Capítulo con ID {chapter_id} no encontrado"
        )
    
    # ───────────────────────────────────────────────────────────
    # PASO 2: Verificar conflicto de order_number
    # ───────────────────────────────────────────────────────────
    # Si se cambia el order_number, verificar que no esté ocupado
    if chapter_data.order_number != chapter.order_number:
        existing = session.exec(
            select(Chapter)
            .where(Chapter.novel_id == chapter.novel_id)
            .where(Chapter.order_number == chapter_data.order_number)
            .where(Chapter.id != chapter_id)  # Excluir el mismo capítulo
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un capítulo {chapter_data.order_number} para esta novela"
            )
    
    # ───────────────────────────────────────────────────────────
    # PASO 3: Actualizar campos
    # ───────────────────────────────────────────────────────────
    chapter.title = chapter_data.title
    chapter.content = chapter_data.content
    chapter.order_number = chapter_data.order_number
    
    if chapter_data.source_url:
        chapter.source_url = chapter_data.source_url
    
    # ───────────────────────────────────────────────────────────
    # PASO 4: Guardar cambios
    # ───────────────────────────────────────────────────────────
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    
    return chapter


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 5: Eliminar capítulo
# ═══════════════════════════════════════════════════════════════

@router.delete(
    "/chapters/{chapter_id}",
    summary="Eliminar capítulo"
)
def delete_chapter(
    session: session_dep,
    chapter_id: int = Path(..., description="ID del capítulo", gt=0),
):
    """
    Elimina un capítulo.
    
    **CUIDADO**: Esta acción es irreversible.
    """
    
    # ───────────────────────────────────────────────────────────
    # PASO 1: Buscar capítulo
    # ───────────────────────────────────────────────────────────
    chapter = session.get(Chapter, chapter_id)
    
    if not chapter:
        raise HTTPException(
            status_code=404,
            detail=f"Capítulo con ID {chapter_id} no encontrado"
        )
    
    # ───────────────────────────────────────────────────────────
    # PASO 2: Eliminar
    # ───────────────────────────────────────────────────────────
    session.delete(chapter)
    session.commit()
    
    # ───────────────────────────────────────────────────────────
    # PASO 3: Respuesta de confirmación
    # ───────────────────────────────────────────────────────────
    return {
        "ok": True,
        "message": f"Capítulo '{chapter.title}' eliminado exitosamente"
    }


# ═══════════════════════════════════════════════════════════════
# ENDPOINT BONUS: Obtener capítulo siguiente/anterior
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/chapters/{chapter_id}/next",
    response_model=ChapterSummary | None,
    summary="Obtener capítulo siguiente"
)
def get_next_chapter(
    session: session_dep,
    chapter_id: int = Path(..., description="ID del capítulo actual", gt=0),
):
    """
    Obtiene el capítulo siguiente al actual.
    
    Útil para botón "Siguiente capítulo" en el lector.
    
    Retorna `null` si es el último capítulo.
    """
    
    # Buscar capítulo actual
    current = session.get(Chapter, chapter_id)
    
    if not current:
        raise HTTPException(status_code=404, detail="Capítulo no encontrado")
    
    # Buscar siguiente capítulo
    next_chapter = session.exec(
        select(Chapter)
        .where(Chapter.novel_id == current.novel_id)
        .where(Chapter.order_number > current.order_number)
        .order_by(Chapter.order_number)                       # pyright: ignore[reportArgumentType] 
        .limit(1)
    ).first()
    
    return next_chapter  # Puede ser None


@router.get(
    "/chapters/{chapter_id}/previous",
    response_model=ChapterSummary | None,
    summary="Obtener capítulo anterior"
)
def get_previous_chapter(
    session: session_dep,
    chapter_id: int = Path(..., description="ID del capítulo actual", gt=0),
):
    """
    Obtiene el capítulo anterior al actual.
    
    Útil para botón "Capítulo anterior" en el lector.
    
    Retorna `null` si es el primer capítulo.
    """
    
    # Buscar capítulo actual
    current = session.get(Chapter, chapter_id)
    
    if not current:
        raise HTTPException(status_code=404, detail="Capítulo no encontrado")
    
    # Buscar capítulo anterior
    previous_chapter = session.exec(
        select(Chapter)
        .where(Chapter.novel_id == current.novel_id)
        .where(Chapter.order_number < current.order_number)
         .order_by(Chapter.order_number.desc())  # Descendente   #pyright: ignore[reportAttributeAccessIssue]
        .limit(1)
    ).first()
    
    return previous_chapter  # Puede ser None














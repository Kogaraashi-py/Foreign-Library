
# ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
# APIRouter: Para agrupar endpoints relacionados
# HTTPException: Para devolver errores HTTP (404, 400, etc.)
# Request: Para obtener información de la petición

from pathlib import Path
# Path: Para manipular rutas de archivos

from typing import List
# List: Para tipar listas (List[GenreResponse])

from sqlmodel import select
# select: Para construir queries SQL
# Ejemplo: select(Genre).where(Gender.id == 5)

from api.deps import session_dep
# session_dep: Dependencia que inyecta la sesión de BD
# Recuerda: session_dep = Annotated[Session, Depends(get_session)]
from schemas import (
    NovelCreate,
    NovelUpdate,
    NovelResponse,
    NovelDetailResponse,
    NovelGenresUpdate,
    GenreResponse,
    NovelNameResponse
)

from models.novel import Novel, NovelStatus, NovelName  # ← De models.novel
from models.genre import Genre, NovelGenre              # ← De models.genre (CORREGIR)
from models.chapter import Chapter


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def build_cover_url(request: Request, cover_path: str | None) -> str | None:
    """
    Convierte una ruta relativa de portada en URL completa.

    Args:
        request: Objeto Request de FastAPI
        cover_path: Ruta relativa como "/static/novels/5.webp"

    Returns:
        URL completa como "http://localhost:8000/images/5.webp"
        None si cover_path es None
    """
    if not cover_path:
        return None

    # Extraer solo el nombre del archivo de la ruta
    # "/static/novels/5.webp" -> "5.webp"
    filename = Path(cover_path).name

    # Construir URL manualmente para evitar problemas con url_for
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/images/{filename}"  



router = APIRouter(prefix="/novels", tags=["novels"])


@router.get("/", response_model = list[NovelResponse])
def get_all_novels(
    request: Request,  # Para generar URLs completas
    session: session_dep,
    skip: int = 0,
    limit: int = 20,
    status : NovelStatus | None = None,
    min_rate: float | None = None
  ):
    statemen = select(Novel)

    if status:
          statemen = statemen.where(Novel.status == status)

    if min_rate is not None:
        statemen = statemen.where(Novel.rating >= min_rate) # pyright: ignore[reportOptionalOperand]

    statemen = statemen.order_by(Novel.rating.desc())  # pyright: ignore[reportAttributeAccessIssue,reportOptionalMemberAccess]

    #paginacion
    statemen = statemen.offset(skip).limit(limit)

    novels = session.exec(statemen).all()

    # Convertir a dict y agregar cover_url
    result = []
    for novel in novels:
        novel_dict = {
            "id": novel.id,
            "name": novel.name,
            "author": novel.author,
            "description": novel.description or "",
            "rating": novel.rating,
            "status": novel.status,
            "cover_path": novel.cover_path,
            "cover_url": build_cover_url(request, novel.cover_path),
            "source_url": novel.source_url,
            "created_at": novel.created_at,
            "updated_at": novel.updated_at
        }
        result.append(novel_dict)

    return result




@router.get("/{novel_id}", response_model=NovelDetailResponse)
def get_novel(novel_id: int, session: session_dep):
    """Obtiene detalle completo de una novela."""
    
    # 1. Buscar novela
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novela no encontrada")
    
    # 2. Safety check
    if novel.id is None:
        raise HTTPException(status_code=500, detail="Error: novel sin ID")
    
    # 3. Cargar géneros
    genres = session.exec(
        select(Genre).join(NovelGenre).where(NovelGenre.novel_id == novel.id)
    ).all()
    
    # 4. Cargar nombres alternativos
    alternative_names = session.exec(
        select(NovelName).where(NovelName.novel_id == novel.id)
    ).all()
    
    # 5. Contar capítulos
    from models.chapter import Chapter
    from sqlalchemy import func
    
    chapters_count = session.exec(
        select(func.count()).select_from(Chapter).where(Chapter.novel_id == novel.id)
    ).one()
    
    # 6. Construir respuesta - AHORA SIN ERRORES
    return NovelDetailResponse(
        id=novel.id,
        name=novel.name,
        author=novel.author,
        description=novel.description or "",  # ✅ Ahora el schema acepta str | None
        rating=novel.rating,
        status=novel.status,
        cover_path=novel.cover_path,
        source_url=novel.source_url,
        created_at=novel.created_at,
        updated_at=novel.updated_at,
        genres=[GenreResponse.model_validate(g) for g in genres],
        alternative_names=[NovelNameResponse.model_validate(n) for n in alternative_names],
        chapters_count=chapters_count
    )



@router.post("/", response_model=NovelResponse, status_code=201)
def create_novel(
    request: Request,  # Para generar URLs completas
    novel_data: NovelCreate,
    session: session_dep,
):
    """
    Crea una nueva novela (sin géneros ni nombres alternativos aún).
    Esos se agregan después con endpoints específicos.
    """
    
    # Verificar que no exista una novela con ese nombre
    existing = session.exec(
        select(Novel).where(Novel.name == novel_data.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una novela con el nombre '{novel_data.name}'"
        )
    
    # Crear instancia del modelo Novel (BD)
    novel = Novel(
        name=novel_data.name,
        author=novel_data.author,
        description=novel_data.description,
        rating=novel_data.rating,
        status=novel_data.status,
        source_url=novel_data.source_url,
        cover_path=None,  # Se sube después con POST /novels/{id}/cover
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Guardar en BD
    session.add(novel)
    session.commit()
    session.refresh(novel)

    # Devolver con cover_url
    return {
        "id": novel.id,
        "name": novel.name,
        "author": novel.author,
        "description": novel.description or "",
        "rating": novel.rating,
        "status": novel.status,
        "cover_path": novel.cover_path,
        "cover_url": build_cover_url(request, novel.cover_path),
        "source_url": novel.source_url,
        "created_at": novel.created_at,
        "updated_at": novel.updated_at
    }









@router.put("/{novel_id}", response_model=NovelResponse)
def update_novel(
    request: Request,  # Para generar URLs completas
    novel_id: int,
    novel_data: NovelUpdate,
    session: session_dep
):
    """
    Actualiza los campos de una novela.
    Solo se actualizan los campos que se envíen (actualización parcial).
    """
    
    # Buscar novela
    novel = session.get(Novel, novel_id)
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novela no encontrada")
    
    # Actualizar solo los campos que vengan en el request
    update_data = novel_data.model_dump(exclude_unset=True)
    # model_dump(exclude_unset=True): solo devuelve campos que se enviaron
    
    for key, value in update_data.items():
        setattr(novel, key, value)
    
    # Actualizar timestamp
    novel.updated_at = datetime.now()
    
    # Guardar cambios
    session.add(novel)
    session.commit()
    session.refresh(novel)

    # Devolver con cover_url
    return {
        "id": novel.id,
        "name": novel.name,
        "author": novel.author,
        "description": novel.description or "",
        "rating": novel.rating,
        "status": novel.status,
        "cover_path": novel.cover_path,
        "cover_url": build_cover_url(request, novel.cover_path),
        "source_url": novel.source_url,
        "created_at": novel.created_at,
        "updated_at": novel.updated_at
    }


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 5: Eliminar novela
# ═══════════════════════════════════════════════════════════════

@router.delete("/{novel_id}")
def delete_novel(
    novel_id: int,
    session: session_dep
):
    """
    Elimina una novela y todas sus relaciones.
    CUIDADO: Esto elimina también capítulos, nombres alternativos, etc.
    """
    
    novel = session.get(Novel, novel_id)
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novela no encontrada")
    
    # Eliminar relaciones manualmente (si no tienes CASCADE en BD)
    # Eliminar nombres alternativos
    session.exec(select(NovelName).where(NovelName.novel_id == novel_id)).all()
    for name in session.exec(select(NovelName).where(NovelName.novel_id == novel_id)):
        session.delete(name)
    
    # Eliminar asociaciones de géneros
    for assoc in session.exec(select(NovelGenre).where(NovelGenre.novel_id == novel_id)):
        session.delete(assoc)
    
    # Eliminar capítulos
    from models.chapter import Chapter
    for chapter in session.exec(select(Chapter).where(Chapter.novel_id == novel_id)):
        session.delete(chapter)
    
    # Eliminar la novela
    session.delete(novel)
    session.commit()
    
    return {"ok": True, "message": f"Novela '{novel.name}' eliminada"}


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 6: Buscar novelas
# ═══════════════════════════════════════════════════════════════

@router.get("/search/", response_model=List[NovelResponse])
def search_novels(
    request: Request,  # Para generar URLs completas
    session: session_dep,
    q: str | None = None,  # Query de búsqueda
    genre_id: int | None = None,
    status: NovelStatus | None = None,
    min_rating: float | None = None,
    skip: int = 0,
    limit: int = 20
):
    """
    Busca novelas por nombre o filtros.
    
    - **q**: Buscar en el nombre (búsqueda parcial)
    - **genre_id**: Filtrar por género
    - **status**: Filtrar por estado
    - **min_rating**: Rating mínimo
    
    Ejemplo: GET /novels/search/?q=lord&genre_id=1&status=completed
    """
    
    statement = select(Novel)
    
    # Búsqueda por nombre (case-insensitive, parcial)
    if q:
        statement = statement.where(Novel.name.ilike(f"%{q}%")) # pyright: ignore[reportAttributeAccessIssue]
        # ilike: case-insensitive LIKE
        # %lord% busca "lord", "Lord of", "Overlord", etc.
    
    # Filtrar por género (requiere JOIN)
    if genre_id:
        statement = (
            statement
            .join(NovelGenre)
            .where(NovelGenre.genre_id == genre_id)


        )
    
    # Otros filtros
    if status:
        statement = statement.where(Novel.status == status)
    
    if min_rating is not None:
        statement = statement.where(Novel.rating >= min_rating)  # pyright: ignore[reportOptionalOperand]  
    
    # Ordenar por relevancia (por ahora, por rating)
    statement = statement.order_by(Novel.rating.desc())  # pyright: ignore[reportAttributeAccessIssue,reportOptionalMemberAccess]   
    
    # Paginación
    statement = statement.offset(skip).limit(limit)
    
    novels = session.exec(statement).all()

    # Convertir a dict y agregar cover_url
    result = []
    for novel in novels:
        novel_dict = {
            "id": novel.id,
            "name": novel.name,
            "author": novel.author,
            "description": novel.description or "",
            "rating": novel.rating,
            "status": novel.status,
            "cover_path": novel.cover_path,
            "cover_url": build_cover_url(request, novel.cover_path),
            "source_url": novel.source_url,
            "created_at": novel.created_at,
            "updated_at": novel.updated_at
        }
        result.append(novel_dict)

    return result


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 7: Asociar géneros a una novela
# ═══════════════════════════════════════════════════════════════

@router.post("/{novel_id}/genres", response_model=NovelDetailResponse)
def add_genres_to_novel(
    novel_id: int,
    genres_data: NovelGenresUpdate,
    session: session_dep
):
    """
    Asocia géneros a una novela.
    Reemplaza los géneros existentes con los nuevos.
    
    Body: {"genre_ids": [1, 2, 3]}
    """
    
    # Verificar que la novela existe
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novela no encontrada")
    
    # Verificar que todos los géneros existen
    for genre_id in genres_data.genre_ids:
        genre = session.get(Genre, genre_id)
        if not genre:
            raise HTTPException(
                status_code=400,
                detail=f"Género con ID {genre_id} no existe"
            )
    
    # Eliminar asociaciones existentes
    existing_associations = session.exec(
        select(NovelGenre).where(NovelGenre.novel_id == novel_id)
    ).all()
    
    for assoc in existing_associations:
        session.delete(assoc)
    
    # Crear nuevas asociaciones
    for genre_id in genres_data.genre_ids:
        association = NovelGenre(novel_id=novel_id, genre_id=genre_id)
        session.add(association)
    
    session.commit()
    
    # Devolver novela actualizada con géneros
    return get_novel(novel_id, session)


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 8: Obtener mejores novelas
# ═══════════════════════════════════════════════════════════════

@router.get("/best/", response_model=List[NovelResponse])
def get_best_novels(
    request: Request,  # Para generar URLs completas
    session: session_dep,
    limit: int = 10
):
    """
    Obtiene las novelas mejor puntuadas.
    Útil para sección "Top Novels" en homepage.
    """

    statement = (
        select(Novel)
        .where(Novel.rating.isnot(None))  # Solo novelas con rating  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        .order_by(Novel.rating.desc())                   # pyright: ignore[reportAttributeAccessIssue,reportOptionalMemberAccess]
        .limit(limit)
    )

    novels = session.exec(statement).all()

    # Convertir a dict y agregar cover_url
    result = []
    for novel in novels:
        novel_dict = {
            "id": novel.id,
            "name": novel.name,
            "author": novel.author,
            "description": novel.description or "",
            "rating": novel.rating,
            "status": novel.status,
            "cover_path": novel.cover_path,
            "cover_url": build_cover_url(request, novel.cover_path),
            "source_url": novel.source_url,
            "created_at": novel.created_at,
            "updated_at": novel.updated_at
        }
        result.append(novel_dict)

    return result

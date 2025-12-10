 # ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException
# APIRouter: Para agrupar endpoints relacionados
# HTTPException: Para devolver errores HTTP (404, 400, etc.)

from typing import List
# List: Para tipar listas (List[GenreResponse])

from sqlmodel import select
# select: Para construir queries SQL
# Ejemplo: select(Gender).where(Gender.id == 5)

from api.deps import session_dep
# SessionDep: Dependencia que inyecta la sesión de BD
# Recuerda: SessionDep = Annotated[Session, Depends(get_session)]

from models.genre import Genre
# Gender: Modelo de la tabla (para queries)

from schemas import GenreCreate, GenreResponse
# GenreCreate: Schema para validar datos al crear
# GenreResponse: Schema para devolver datos al cliente


router = APIRouter(prefix="/genres", tags=["genres"])



# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

#este endpoint lista todos los generos disponibles
@router.get("/", response_model=List[GenreResponse])
def list_genres(
    session: session_dep,
    skip: int = 0,
    limit: int = 100
):
    """
    Lista todos los géneros disponibles.
    
    - **skip**: Número de géneros a saltar (paginación)
    - **limit**: Máximo número de géneros a devolver
    """
    statement =  select(Genre).offset(skip).limit(limit)
    genres = session.exec(statement).all()
    return genres



#este endpoint obtiene un genero por su id
@router.get("/{genre_id}", response_model=GenreResponse)
def get_genre(
    genre_id: int,
    session: session_dep
):
    """Obtiene un género por su ID."""
    
    genre = session.get(Genre, genre_id)

    if not genre:
      raise HTTPException(status_code=404, detail="Género no encontrado")


    return genre

#para hacer un pliege de codigo en nvim es con el atajo de z+f señalando la parte y si la queremos abrir es con z+o 
#y si la queremos cerarrar es con z+c y para abrir todos es z+R y para cerrar todos es z+M


#este endpoint crea un nuevo genero
@router.post("/", response_model=GenreResponse, status_code=201)
def create_genre(
    genre_data: GenreCreate,
    session: session_dep
):
    """
    
    **`@router.post("/")`**
    - Maneja peticiones POST
    - Ruta: `POST /genres/`
    
    **`status_code=201`**
    - Por defecto FastAPI devuelve 200
    - Para creaciones, el estándar HTTP es 201 (Created)
    
    **`genre_data: GenreCreate`**
    - Body de la petición
    - FastAPI automáticamente:
    - Lee el JSON del body
    - Valida con `GenreCreate` schema
    - Si no es válido, devuelve error 422
    - Pasa el objeto validado a la función
    
    **Ejemplo de petición:**
    ```
    POST /genres/
    Content-Type: application/json
    
    {
      "name": "cultivation"
    }
    Crea un nuevo género.
    """

    
    # Verificar que no exista un género con ese nombre
    existing = session.exec(
        select(Genre).where(Genre.name == genre_data.name.lower())
    ).first()

    if existing:
         raise HTTPException(
             status_code=400,
             detail = f"ya existe un genero con ese nombre: {existing.name}")
    # Crear el género
    genre = Genre(name=genre_data.name.lower())
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre





#este endpoint actualiza un genero por su id
@router.put("/{genre_id}", response_model=GenreResponse )
def update_genre(
         genre_id : int,
         genre_data : GenreCreate,
         session: session_dep,
):
    genre = session.get(Genre,genre_id)

    if not genre:
        raise HTTPException(status_code=404, detail="genero no encontrado")


    genre.name = genre_data.name.lower()

    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre



@router.delete("/{genre_id}")
def delete_genre(
         genre_id : int,
         session: session_dep
):
    genre = session.get(Genre,genre_id)
     
    if not genre:
         raise HTTPException(status_code=404, detail="genero no encontrado")
    session.delete(genre)
    session.commit()
    
    return {"OK": True, "message":"el Genero ha sido eliminado "}











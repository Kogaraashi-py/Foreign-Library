from .config import settings
from sqlmodel import Session,  create_engine ,SQLModel
from typing import Annotated,Generator



engine = create_engine(settings.url_conection,echo=True)

def create_db_and_tables():
    import importlib

    importlib.import_module("models.genre")   # define NovelGenre
    importlib.import_module("models.novel")   # usa NovelGenre
    importlib.import_module("models.chapter") # independiente
    """Crea las tablas en la base de datos  definida en los modelos SQLModel."""
    SQLModel.metadata.create_all(engine)



def get_session():
    """Proporciona una sesión de base de datos para todo(por ahora)"""
    with Session(engine) as session:
        yield session
 

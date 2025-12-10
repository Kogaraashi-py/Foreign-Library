from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from datetime import datetime
from enum import Enum

"""definición de las tablas relacionadas con novelas, incluyendo nombres alternativos y géneros"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .chapter import Chapter
    from .genre import Genre



from .novel_genre import NovelGenre


class NovelName(SQLModel, table=True):
    """Modelo para nombres alternativos de novelas."""
    __tablename__: str = "novel_names"

    id: int | None = Field(default=None, primary_key=True)
    novel_id: int = Field(foreign_key="novels.id")
    name: str = Field(max_length=200)
    """definición de la relación muchos a uno con novela"""
    novel: "Novel" = Relationship(back_populates="names")


class NovelStatus(str, Enum):
    """Estado de la novela."""
    ongoing = "ongoing"
    completed = "completed"
    hiatus = "hiatus"
    dropped = "dropped"





class Novel(SQLModel, table=True):
    """
    Tabla de novelas en la base de datos.
    Este modelo representa la estructura real de la tabla.
    """
    __tablename__: str = "novels"  # Nombre explícito de tabla
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=200)

    rating: float | None = Field(default=None, ge=0, le=10)
    description: str = Field(max_length=5000)

    cover_path: str | None = Field(default=None, max_length=500)
    source_url: str | None = Field(default=None, max_length=500) 

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    status: NovelStatus = Field(default=NovelStatus.ongoing)
    author: str = Field(max_length=200)


     # Nombres alternativos (1:N)
    """definición de la relación uno a muchos con nombres alternativos"""
    names: "NovelName" = Relationship(back_populates="novel")

    # Géneros (N:M)
    """definición de la relación muchos a muchos con géneros"""
    genres: "Genre" = Relationship(
        back_populates="novels",
        link_model=NovelGenre
    ) 
    """definición de la relación uno a muchos con capítulos"""
    chapters: "Chapter" = Relationship(back_populates="novel")









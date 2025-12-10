from __future__ import annotations
from sqlmodel import SQLModel, Field

class NovelGenre(SQLModel, table=True):
    __tablename__ = "novel_genres"

    novel_id: int = Field(foreign_key="novels.id", primary_key=True)
    genre_id: int = Field(foreign_key="genres.id", primary_key=True)


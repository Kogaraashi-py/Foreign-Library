# pyright: reportAssignmentType=none
# pyright: reportIncompatibleVariableOverride=none

from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .novel import Novel

from .novel_genre import NovelGenre



class Genre(SQLModel, table=True):
    """Tabla de géneros en la base de datos."""
    __tablename__: str = "genres"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)

    novels: "Novel" = Relationship(
        back_populates="genres",
        link_model=NovelGenre
    )


# schemas/__init__.py

"""
Módulo schemas: Schemas de validación Pydantic.
"""

# Genre schemas
from .genre import GenreBase, GenreCreate, GenreResponse

# Novel Name schemas
from .novel_name import NovelNameBase, NovelNameCreate, NovelNameResponse

# Novel schemas
from .novel import (
    NovelBase,
    NovelCreate,
    NovelUpdate,
    NovelResponse,
    NovelDetailResponse,
    NovelGenresUpdate,
    NovelCardResponse
)

# Chapter schemas
from .chapter import (
    ChapterBase,
    ChapterCreate,
    ChapterSummary,
    ChapterDetailResponse
)

__all__ = [
    # Genres
    "GenreBase",
    "GenreCreate",
    "GenreResponse",
    
    # Novel Names
    "NovelNameBase",
    "NovelNameCreate",
    "NovelNameResponse",
    
    # Novels
    "NovelBase",
    "NovelCreate",
    "NovelUpdate",
    "NovelResponse",
    "NovelDetailResponse",
    "NovelGenresUpdate",
    "NovelCardResponse",
    
    # Chapters
    "ChapterBase",
    "ChapterCreate",
    "ChapterSummary",
    "ChapterDetailResponse",
]

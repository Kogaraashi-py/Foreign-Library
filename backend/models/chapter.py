 # models/chapter.py
from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from sqlalchemy import Column, Text
"""soporte para restricciones únicas,en este caso para evitar capítulos duplicados por novela y número de orden"""
from sqlmodel import UniqueConstraint


"""definición de la tabla de capítulos de novelas"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .novel import Novel


class Chapter(SQLModel, table=True):
    """Tabla de capítulos"""
    __tablename__: str = "chapters"
    __table_args__ = (
        UniqueConstraint("novel_id", "order_number"),
    )
    
    id: int | None = Field(default=None, primary_key=True)
    novel_id: int = Field(foreign_key="novels.id", index=True)
    title: str = Field(max_length=300)
    content: str = Field(sa_column=Column(Text))  # Texto completo del capítulo
    order_number: int  # Número de capítulo (1, 2, 3...)
    source_url: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.now)
     
     # RELACIÓN inversa
    """definición de la relación muchos a uno con novela"""
    novel: "Novel" = Relationship(back_populates="chapters")

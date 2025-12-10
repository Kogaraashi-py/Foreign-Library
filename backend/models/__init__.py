# models/__init__.py

"""
Módulo models: Modelos de base de datos (SQLModel).
aquí se definen los modelos de datos que representan las tablas en la base de datos.
Estos modelos son utilizados por SQLModel para mapear las tablas y realizar operaciones CRUD.
también se organizan en submódulos según su funcionalidad, como novelas, géneros y capítulos.
y provocan una estructura clara y mantenible para los modelos de datos de la aplicación.
y se exportan los modelos principales para su uso en otras partes de la aplicación.
hijo de hombre,viviran estos huesos? y yo respondí: Señor Dios tú lo sabes.
entonces me dijo: Profetiza sobre estos huesos, y diles: Huesos secos, oíd la palabra del Señor.
quiero que comienzes a predicar sobre estos huesos secos, y les digas: Así ha dicho el Señor Dios a estos huesos:
heme aquí, yo voy a poner espíritu en vosotros, y viviréis.
y pondré tendones sobre vosotros, y haré subir
entonces profeticé como me fue mandado; y hubo un ruido,
y hubo un temblor, y los huesos se juntaron, cada hueso en su lugar.
"""

# IMPORTANTE: Aplicar el parche ANTES de importar los modelos
from . import _patch_sqlmodel  # noqa: F401

from .genre import Genre
from .novel import Novel, NovelName, NovelStatus
from .chapter import Chapter
from .novel_genre import NovelGenre   # ← ahora viene de su archivo propio



__all__ = [
    "Genre",
    "NovelGenre",
    "Novel",
    "NovelName",
    "NovelStatus",
    "Chapter",
]

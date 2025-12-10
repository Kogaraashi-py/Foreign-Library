 # ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field, HttpUrl
from typing import List
from models.novel import NovelStatus

# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA CAPÍTULO DESDE SCRAPING
# ═══════════════════════════════════════════════════════════════

class ScrapedChapter(BaseModel):
    """
    Representa UN capítulo extraído por scraping.
    
    ¿Por qué existe?
    - Es parte del JSON completo que envía el scraper
    - No es el mismo que ChapterCreate (ese es para crear uno a la vez)
    """
    
    title: str = Field(min_length=1, max_length=300)
    # Título del capítulo
    
    content: str
    # Contenido completo
    # Sin límite de tamaño (puede ser muy largo)
    
    order_number: int = Field(ge=1)
    # Número de orden en la serie
    # ge=1: Mínimo 1
    
    source_url: str | None = None
    # URL original del capítulo (opcional)
    # ¿Por qué opcional?
    # - A veces el scraper no guarda URLs individuales de capítulos


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA NOVELA COMPLETA DESDE SCRAPING
# ═══════════════════════════════════════════════════════════════

class NovelImportData(BaseModel):
    """
    Schema para IMPORTAR una novela completa desde scraping.
    
    ¿Cuándo se usa?
    POST /admin/import-novel
    Body: { ...todos los datos... }
    
    ¿Por qué es diferente a NovelCreate?
    - NovelCreate: Crear manualmente desde frontend
    - NovelImportData: Importar automáticamente desde scraper
    - Este incluye relaciones, imagen, capítulos, etc.
    """
    
    # ═══════════════════════════════════════════════════════════
    # DATOS BÁSICOS DE LA NOVELA
    # ═══════════════════════════════════════════════════════════
    
    name: str = Field(min_length=1, max_length=200)
    # Nombre principal de la novela
    
    author: str = Field(min_length=1, max_length=200)
    # Autor
    
    description: str = Field(max_length=5000)
    # Descripción/sinopsis
    
    rating: float | None = Field(default=None, ge=0, le=10)
    # Rating (puede venir del sitio web o ser None)
    
    status: NovelStatus = Field(default=NovelStatus.ongoing)
    # Estado: ongoing, completed, hiatus, dropped
    
    source_url: str
    # URL de donde se extrajo
    # ¿Por qué obligatorio?
    # - Siempre viene de un sitio web
    # - Es importante para rastrear la fuente
    
    # ═══════════════════════════════════════════════════════════
    # IMAGEN DE PORTADA
    # ═══════════════════════════════════════════════════════════
    
    image_path: str | None = None
    # Ruta LOCAL donde el scraper guardó la imagen
    # Ejemplo: "/tmp/scraped_images/lotm.jpg"
    #
    # ¿Qué hará el backend con esto?
    # 1. Leer el archivo de esa ruta
    # 2. Crear la novela en BD → obtener ID
    # 3. Mover/copiar a: static/novels/{id}.webp
    # 4. Actualizar novel.cover_path = "/static/novels/{id}.webp"
    #
    # ¿Por qué opcional?
    # - A veces el sitio no tiene imagen
    # - O falló la descarga
    
    # ═══════════════════════════════════════════════════════════
    # NOMBRES ALTERNATIVOS
    # ═══════════════════════════════════════════════════════════
    
    alternative_names: List[str] = []
    # Lista de nombres alternativos
    # Ejemplo: ["诡秘之主", "Mystery Lord", "LoM"]
    #
    # ¿Qué hará el backend?
    # for name in alternative_names:
    #     NovelName.create(novel_id=novel.id, name=name)
    #
    # default=[]: Si no hay nombres alternativos, lista vacía
    
    # ═══════════════════════════════════════════════════════════
    # GÉNEROS
    # ═══════════════════════════════════════════════════════════
    
    genres: List[str] = []
    # Lista de nombres de géneros
    # Ejemplo: ["fantasy", "mystery", "adventure"]
    #
    # ¿Por qué strings y no IDs?
    # - El scraper no conoce los IDs de tu BD
    # - El backend debe:
    #   1. Buscar cada género por nombre
    #   2. Si no existe, crearlo
    #   3. Asociarlo a la novela
    #
    # Pseudocódigo:
    # for genre_name in genres:
    #     genre = session.query(Gender).filter_by(name=genre_name).first()
    #     if not genre:
    #         genre = Gender(name=genre_name)
    #         session.add(genre)
    #     novel.genders.append(genre)
    
    # ═══════════════════════════════════════════════════════════
    # CAPÍTULOS
    # ═══════════════════════════════════════════════════════════
    
    chapters: List[ScrapedChapter] = []
    # Lista de capítulos completos
    # Ejemplo: [
    #   {"title": "Chapter 1", "content": "...", "order_number": 1},
    #   {"title": "Chapter 2", "content": "...", "order_number": 2}
    # ]
    #
    # ¿Qué hará el backend?
    # for chapter_data in chapters:
    #     Chapter.create(
    #         novel_id=novel.id,
    #         title=chapter_data.title,
    #         content=chapter_data.content,
    #         order_number=chapter_data.order_number
    #     )
    #
    # ¿Por qué opcional (default=[])?
    # - A veces quieres importar la novela sin capítulos
    # - Los capítulos se pueden agregar después


# ═══════════════════════════════════════════════════════════════
# SCHEMA PARA RESPUESTA DE IMPORT
# ═══════════════════════════════════════════════════════════════

class NovelImportResponse(BaseModel):
    """
    Respuesta después de importar una novela.
    
    ¿Qué devuelve?
    - Confirmación de éxito
    - ID de la novela creada
    - Estadísticas de lo que se creó
    """
    
    success: bool
    # True si todo salió bien
    
    novel_id: int
    # ID de la novela creada
    
    message: str
    # Mensaje descriptivo
    # Ejemplo: "Novela 'Lord of Mysteries' importada exitosamente"
    
    stats: dict
    # Estadísticas de lo que se creó
    # Ejemplo:
    # {
    #   "alternative_names_created": 3,
    #   "genres_created": 2,
    #   "genres_associated": 4,
    #   "chapters_created": 150,
    #   "cover_uploaded": True
    # }

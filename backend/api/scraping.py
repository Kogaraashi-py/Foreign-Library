# api/scraping.py

# ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════
from PIL import Image
import io
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from datetime import datetime
from pathlib import Path
import shutil

from api.deps import session_dep

# Modelos
from models.novel import Novel, NovelName
from models.genre import Genre, NovelGenre
from models.chapter import Chapter

# Schemas
from schemas.scraping import (
    NovelImportData,
    NovelImportResponse,
    ScrapedChapter
)

from core.config import settings


# ═══════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════

router = APIRouter(prefix="/admin", tags=["admin", "scraping"])
# prefix="/admin": Todas las rutas empiezan con /admin
# tags: Agrupa en documentación de Swagger


# ═══════════════════════════════════════════════════════════════
# ENDPOINT: Importar novela completa desde scraping
# ═══════════════════════════════════════════════════════════════

@router.post("/import-novel", response_model=NovelImportResponse, status_code=201)
def import_novel_from_scraper(
    data: NovelImportData,
    session: session_dep
):
    """
    Importa una novela completa con todos sus datos desde un scraper.
    
    **Este endpoint hace TODO en una sola operación:**
    - Crea la novela en la BD
    - Descarga y guarda la imagen de portada
    - Crea nombres alternativos
    - Asocia géneros (crea si no existen)
    - Crea todos los capítulos
    
    **Uso típico:**
    Un script externo hace scraping de un sitio web, organiza los datos
    en formato JSON y los envía a este endpoint.
    
    **Body ejemplo:**
```json
    {
      "name": "Lord of the Mysteries",
      "author": "Cuttlefish That Loves Diving",
      "description": "In the waves of steam...",
      "rating": 9.5,
      "status": "completed",
      "source_url": "https://novelfull.com/lord-of-the-mysteries.html",
      "image_path": "/tmp/scraped/lotm.jpg",
      "alternative_names": ["诡秘之主", "Mystery Lord"],
      "genres": ["fantasy", "mystery", "supernatural"],
      "chapters": [
        {
          "title": "Chapter 1: Crimson",
          "content": "In the tide of the era...",
          "order_number": 1,
          "source_url": "https://..."
        }
      ]
    }
```
    """
    
    # ───────────────────────────────────────────────────────────
    # PASO 1: Verificar que no exista una novela con ese nombre
    # ───────────────────────────────────────────────────────────
    
    existing = session.exec(
        select(Novel).where(Novel.name == data.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una novela con el nombre '{data.name}' (ID: {existing.id})"
        )
    # ¿Por qué verificar?
    # - Evitar duplicados
    # - Si el scraper se ejecuta dos veces, no crea la novela dos veces
    
    
    # ───────────────────────────────────────────────────────────
    # PASO 2: Crear la novela (sin imagen todavía)
    # ───────────────────────────────────────────────────────────
    
    novel = Novel(
        name=data.name,
        author=data.author,
        description=data.description,
        rating=data.rating,
        status=data.status,
        source_url=data.source_url,
        cover_path=None,  # Se asigna después
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(novel)
    session.commit()
    session.refresh(novel)  # ← Obtener el ID autogenerado
    # Ahora novel.id existe (ej: 5)
    
    print(f"✅ Novela creada con ID: {novel.id}")
    
    
    # ───────────────────────────────────────────────────────────
    # PASO 3: Procesar imagen de portada
    # ───────────────────────────────────────────────────────────
    
    cover_uploaded = False
    
    if data.image_path:
        # Convertir string a Path
        source_path = Path(data.image_path)
        
        # Verificar que el archivo existe
        if source_path.exists() and source_path.is_file():
            try:
                # Abrir imagen con Pillow
                img = Image.open(source_path)
            
                # Convertir a RGB si es necesario (WebP no soporta RGBA bien)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Crear fondo blanco
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
            
                # Nombre del archivo destino: {id}.webp
                target_filename = f"{novel.id}.webp"
                target_path = settings.UPLOAD_DIR / target_filename
            
                # Guardar como WebP con calidad optimizada
                img.save(
                    target_path,
                    format='WEBP',
                    quality=85,  # Buena calidad, buen tamaño
                    method=6     # Mejor compresión (0-6, más lento pero mejor)
                )
            
                # Actualizar BD con la ruta
                novel.cover_path = f"/static/novels/{target_filename}"
                session.add(novel)
                session.commit()
            
                cover_uploaded = True
            
                # Mostrar estadísticas
                original_size = source_path.stat().st_size
                new_size = target_path.stat().st_size
                reduction = ((original_size - new_size) / original_size) * 100
            
                print(f"✅ Portada convertida a WebP: {target_path}")
                print(f"   📊 Tamaño original: {original_size / 1024:.1f} KB")
                print(f"   📊 Tamaño WebP: {new_size / 1024:.1f} KB")
                print(f"   📊 Reducción: {reduction:.1f}%")
            
            except Exception as e:
                print(f"⚠️ Error al procesar imagen: {e}")
                # No falla el import si la imagen falla
        else:
            print(f"⚠️ Archivo de imagen no encontrado: {source_path}")
    
    
    # ───────────────────────────────────────────────────────────
    # PASO 4: Crear nombres alternativos
    # ───────────────────────────────────────────────────────────
    
    alt_names_created = 0
    assert novel.id is not None, "DB did not return novel id"

    for name in data.alternative_names:
        novel_name = NovelName(
             novel_id=novel.id, 
            name=name
        )
        session.add(novel_name)
        alt_names_created += 1
    
    if alt_names_created > 0:
        session.commit()
        print(f"✅ {alt_names_created} nombres alternativos creados")
    
    
    # ───────────────────────────────────────────────────────────
    # PASO 5: Asociar géneros (crear si no existen)
    # ───────────────────────────────────────────────────────────
    
    genres_created = 0
    genres_associated = 0
    
    for genre_name in data.genres:
        # Normalizar: minúsculas, sin espacios extra
        genre_name_clean = genre_name.lower().strip()
        
        # Buscar género existente
        genre = session.exec(
            select(Genre).where(Genre.name == genre_name_clean)
        ).first()
        
        # Si no existe, crearlo
        if not genre:
            genre = Genre(name=genre_name_clean)
            session.add(genre)
            session.commit()
            session.refresh(genre)
            genres_created += 1
            print(f"✅ Género creado: '{genre_name_clean}'")
        
        # Asociar a la novela (tabla intermedia)
        # Verificar que no exista ya la asociación
        existing_assoc = session.exec(
            select(NovelGenre)
            .where(NovelGenre.novel_id == novel.id)
            .where(NovelGenre.genre_id == genre.id)
        ).first()
        assert genre.id is not None, "DB did not return novel id"

        if not existing_assoc:
            association = NovelGenre(
                novel_id=novel.id,
                genre_id=genre.id
            )
            session.add(association)
            genres_associated += 1
    
    if genres_associated > 0:
        session.commit()
        print(f"✅ {genres_associated} géneros asociados")
    
    
    # ───────────────────────────────────────────────────────────
    # PASO 6: Crear capítulos (evitando duplicados)
    # ───────────────────────────────────────────────────────────

    chapters_created = 0
    chapters_skipped = 0

    for chapter_data in data.chapters:
        # Verificar si el capítulo ya existe
        existing_chapter = session.exec(
            select(Chapter)
            .where(Chapter.novel_id == novel.id)
            .where(Chapter.order_number == chapter_data.order_number)
        ).first()

        if existing_chapter:
            # Actualizar capítulo existente
            existing_chapter.title = chapter_data.title
            existing_chapter.content = chapter_data.content
            existing_chapter.source_url = chapter_data.source_url
            chapters_skipped += 1
            print(f"   ⏭️  Capítulo {chapter_data.order_number} ya existe, actualizado")
        else:
            # Crear nuevo capítulo
            chapter = Chapter(
                novel_id=novel.id,
                title=chapter_data.title,
                content=chapter_data.content,
                order_number=chapter_data.order_number,
                source_url=chapter_data.source_url,
                created_at=datetime.now()
            )
            session.add(chapter)
            chapters_created += 1

        # Commit cada 50 operaciones (optimización)
        total_processed = chapters_created + chapters_skipped
        if total_processed % 50 == 0:
            session.commit()
            print(f"   💾 {total_processed} capítulos procesados...")

    # Commit final de capítulos restantes
    if chapters_created > 0 or chapters_skipped > 0:
        session.commit()
        print(f"✅ {chapters_created} capítulos creados, {chapters_skipped} actualizados")
    
    
    # ───────────────────────────────────────────────────────────
    # PASO 7: Devolver respuesta con estadísticas
    # ───────────────────────────────────────────────────────────
    
    # Determinar el mensaje según lo que se hizo
    if chapters_skipped > 0 and chapters_created == 0:
        message = f"Novela '{novel.name}' ya existía, capítulos actualizados"
    elif chapters_created > 0 and chapters_skipped > 0:
        message = f"Novela '{novel.name}' actualizada parcialmente"
    else:
        message = f"Novela '{novel.name}' importada exitosamente"

    return NovelImportResponse(
        success=True,
        novel_id=novel.id,
        message=message,
        stats={
            "alternative_names_created": alt_names_created,
            "genres_created": genres_created,
            "genres_associated": genres_associated,
            "chapters_created": chapters_created,
            "chapters_updated": chapters_skipped,
            "cover_uploaded": cover_uploaded
        }
    )

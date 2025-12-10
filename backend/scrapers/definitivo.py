#!/usr/bin/env python3
"""
Scraper para NovelasLigera.com
Descarga novelas ligeras y genera JSON compatible con tu API
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os
from typing import Dict, List, Optional
from pathlib import Path
import argparse


class NovelasLigeraScraper:
    def __init__(self, base_url: str = "https://novelasligera.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_novel_info(self, novel_slug: str) -> Dict:
        """Obtiene información básica de la novela y lista de capítulos"""
        url = f"{self.base_url}/novela/{novel_slug}/"
        print(f"📖 Obteniendo información de: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            raw_text = response.text
            soup = BeautifulSoup(raw_text, 'html.parser')
            
            # Extraer metadatos
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            description = self._extract_description(soup)
            genres = self._extract_genres(soup)
            status = self._extract_status(soup)
            rating = self._extract_rating(soup, raw_text)
            image_url = self._extract_image(soup, raw_text)
            alternative_names = self._extract_alternative_names(soup)
            
            # Extraer lista de capítulos
            chapters_list = self._extract_chapter_urls(soup)
            
            return {
                "name": title,
                "author": author or "Desconocido",
                "description": description or "",
                "rating": rating,
                "status": status or "unknown",
                "source_url": url,
                "image_url": image_url,
                "alternative_names": alternative_names,
                "genres": genres,
                "chapters_urls": chapters_list
            }
        except Exception as e:
            print(f"❌ Error obteniendo información: {e}")
            raise
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrae el título de la novela"""
        selectors = [
            'h1.entry-title',
            'h1.novel-title',
            '.post-title h1',
            'header h1'
        ]
        
        for selector in selectors:
            title = soup.select_one(selector)
            if title:
                return title.get_text(strip=True)
        
        h1 = soup.find('h1')
        return h1.get_text(strip=True) if h1 else "Título Desconocido"
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el autor"""
        text = soup.get_text()
        
        # Buscar línea de "Autor:" que NO incluya "Traductor" ni otros metadatos
        match = re.search(r'Autor:\s*([^\n]+?)(?=\s*Traductor:|\s*Plan de publicación:|\s*Estado:|\s*$)', text, re.I)
        
        if match:
            author = match.group(1).strip()
            # Limpiar espacios y caracteres especiales
            author = re.sub(r'\s+', ' ', author)
            # Validar que no esté vacío y no contenga palabras clave de otros campos
            if (author and 
                author.lower() not in ['desconocido', 'unknown', ''] and
                'traductor' not in author.lower() and
                'plan de publicación' not in author.lower() and
                len(author) < 100):  # Evitar capturar demasiado texto
                return author
        
        return "Desconocido"
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae la descripción/sinopsis - solo texto descriptivo, sin navegación ni metadatos"""
        # Primero remover elementos de navegación del soup
        for nav_elem in soup.select('nav, header, footer, .menu, .navigation, .skip-link, noscript'):
            nav_elem.decompose()
        
        text = soup.get_text()
        
        # Buscar descripción entre el título y "Estado:"
        match = re.search(
            r'(?:The Villain Wants to Live-novela|El Villano.*?)\s+(.*?)\s+Estado:',
            text,
            re.DOTALL | re.I
        )
        
        if match:
            description = match.group(1).strip()
            
            # Limpiar texto de JavaScript deshabilitado
            description = re.sub(r'Sorry,?\s+you\s+have\s+Javascript\s+Disabled!?', '', description, flags=re.I)
            description = re.sub(r'To\s+see\s+this\s+page\s+as\s+it\s+is\s+meant\s+to\s+appear,?\s+please\s+enable\s+your\s+Javascript!?', '', description, flags=re.I)
            
            # Limpiar texto de navegación
            nav_patterns = [
                r'Saltar\s+al\s+contenido',
                r'Menú',
                r'Novelas\s+Chinas',
                r'Novelas\s+Coreanas',
                r'Novelas\s+Japonesas',
                r'Novelas\s+\+18',
                r'Reclutamiento\s+y\s+Otros',
                r'Reclutamiento',
                r'CONTACTO',
                r'El\s+Villano\s+Que\s+Quiere\s+Vivir',
            ]
            
            for pattern in nav_patterns:
                description = re.sub(pattern, '', description, flags=re.I)
            
            # Limpiar rating mezclado
            description = re.sub(r'Click\s+to\s+rate.*?\[Total:.*?Average:.*?\]', '', description, flags=re.DOTALL | re.I)
            description = re.sub(r'\[Total:.*?Average:.*?\]', '', description, flags=re.DOTALL | re.I)
            
            # Limpiar título repetido
            description = re.sub(r'The\s+Villain\s+Wants\s+to\s+Live-novela', '', description, flags=re.I)
            
            # Limpiar metadatos que puedan estar mezclados
            description = re.sub(r'Estado:.*$', '', description, flags=re.DOTALL | re.I)
            description = re.sub(r'Género:.*$', '', description, flags=re.DOTALL | re.I)
            description = re.sub(r'Autor:.*$', '', description, flags=re.DOTALL | re.I)
            description = re.sub(r'Traductor:.*$', '', description, flags=re.DOTALL | re.I)
            description = re.sub(r'Tipo:.*$', '', description, flags=re.DOTALL | re.I)
            description = re.sub(r'Original:.*$', '', description, flags=re.DOTALL | re.I)
            description = re.sub(r'Plan de publicación:.*$', '', description, flags=re.DOTALL | re.I)
            
            # Limpiar saltos de línea, tabs y espacios múltiples
            description = re.sub(r'[\t\n]+', ' ', description)
            description = re.sub(r'\s+', ' ', description)
            description = description.strip()
            
            # Solo devolver si tiene contenido válido (más de 50 caracteres)
            if len(description) > 50:
                return description[:2000]
        
        return None
    
    def _extract_genres(self, soup: BeautifulSoup) -> List[str]:
        """Extrae los géneros"""
        text = soup.get_text()
        
        # Buscar línea de "Género:"
        match = re.search(r'Género:\s*(.+?)(?:\n|$)', text, re.I)
        
        if match:
            genres_text = match.group(1)
            # Dividir por comas o puntos
            genres = re.split(r'[,.]', genres_text)
            # Limpiar y normalizar
            genres = [g.strip().lower() for g in genres if g.strip()]
            return genres[:10]
        
        return []
    
    def _extract_status(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el estado (completed/ongoing)"""
        text = soup.get_text()
        
        # Buscar línea de "Estado:"
        match = re.search(r'Estado:\s*(.+?)(?:\n|Tipo:)', text, re.I)
        
        if match:
            status_text = match.group(1).lower()
            
            if 'traducci' in status_text:
                return 'ongoing'
            elif any(word in status_text for word in ['completado', 'finalizado', 'completed']):
                return 'completed'
        
        return 'ongoing'  # Default a ongoing si no se encuentra
    
    def _extract_rating(self, soup: BeautifulSoup, raw_text: str = None) -> Optional[float]:
        """Extrae la calificación"""
        # Método 1: Buscar en el texto raw (más confiable)
        if raw_text:
            # Buscar rating en el patrón "Average: X.X"
            match = re.search(r'Average:\s*(\d+\.?\d*)', raw_text, re.I)
            if match:
                try:
                    rating = float(match.group(1))
                    return min(rating, 10.0)
                except:
                    pass
        
        # Método 2: Buscar en elementos con clases específicas
        rating_elem = soup.find('span', class_=re.compile('rating|score', re.I))
        if not rating_elem:
            rating_elem = soup.find('div', class_=re.compile('rating|score', re.I))
        
        if rating_elem:
            try:
                rating_text = rating_elem.get_text(strip=True)
                match = re.search(r'(\d+\.?\d*)', rating_text)
                if match:
                    rating = float(match.group(1))
                    return min(rating, 10.0)
            except:
                pass
        
        # Método 3: Buscar en atributos data
        rating_attrs = soup.find(attrs={'data-rating': True}) or soup.find(attrs={'itemprop': 'ratingValue'})
        if rating_attrs:
            try:
                rating = float(rating_attrs.get('data-rating') or rating_attrs.get('content', 0))
                return min(rating, 10.0)
            except:
                pass
        
        return None
    
    def _extract_image(self, soup: BeautifulSoup, raw_text: str = None) -> Optional[str]:
        """Extrae URL de la imagen de portada"""
        # Método 1: Buscar en meta tags (más confiable)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            src = og_image.get('content').strip()
            if src and not any(x in src for x in ['data:image', 'placeholder']):
                if src.startswith('//'):
                    return f"https:{src}"
                elif src.startswith('/'):
                    return f"{self.base_url}{src}"
                return src
        
        # Método 2: Buscar en selectores CSS específicos
        selectors = [
            '.elementor-widget-image img',
            '.featured-image img',
            '.post-thumbnail img',
            'img.summary_image',
            'img.novel-cover',
            'img.wp-post-image',
            'img[itemprop="image"]',
            '.entry-header img',
            '.novel-cover img'
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img:
                # Intentar múltiples atributos en orden de prioridad
                src = (img.get('data-lazy-src') or 
                       img.get('data-src') or 
                       img.get('src') or
                       img.get('data-original'))
                
                if src and not any(x in src for x in ['data:image', 'placeholder', 'loading', 'lazy']):
                    if src.startswith('//'):
                        return f"https:{src}"
                    elif src.startswith('/'):
                        return f"{self.base_url}{src}"
                    return src
        
        # Método 3: Buscar en el HTML raw con regex
        if raw_text:
            patterns = [
                r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
                r'<img[^>]+class=["\'](?:summary_image|novel-cover|wp-post-image|featured-image)["\'][^>]+(?:data-lazy-src|data-src|src)=["\']([^"\']+)["\']',
                r'<img[^>]+(?:data-lazy-src|data-src|src)=["\']([^"\']+)["\'][^>]+class=["\'](?:summary_image|novel-cover|wp-post-image|featured-image)["\']',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, raw_text, re.I)
                if match:
                    src = match.group(1)
                    # Evitar placeholders
                    if not any(x in src for x in ['data:image', 'placeholder', 'loading', 'lazy']):
                        if src.startswith('//'):
                            return f"https:{src}"
                        elif src.startswith('/'):
                            return f"{self.base_url}{src}"
                        return src
        
        return None
    
    def _extract_alternative_names(self, soup: BeautifulSoup) -> List[str]:
        """Extrae nombres alternativos"""
        text = soup.get_text()
        alt_names = []
        
        # Buscar nombre original en inglés al principio
        match = re.search(r'^([A-Z][A-Za-z\s]+?)-novela', text, re.MULTILINE)
        if match:
            original_name = match.group(1).strip()
            if original_name != "El Villano Que Quiere Vivir":
                alt_names.append(original_name)
        
        # Buscar abreviaciones en los títulos de capítulos (ej: TVWL)
        abbrev_match = re.findall(r'([A-Z]{3,})\s*–', text)
        if abbrev_match:
            # Tomar la abreviación más común
            from collections import Counter
            most_common = Counter(abbrev_match).most_common(1)
            if most_common:
                alt_names.append(most_common[0][0])
        
        return list(set(alt_names))[:5]
    
    def _extract_chapter_urls(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extrae URLs de todos los capítulos"""
        chapters = []
        
        chapter_links = soup.select('ul.lcp_catlist a, .chapter-list a, .wp-manga-chapter a')
        
        if not chapter_links:
            all_links = soup.find_all('a', href=re.compile(r'/capitulo-?\d+', re.I))
            chapter_links = all_links
        
        for link in chapter_links:
            href = link.get('href')
            title = link.get_text(strip=True)
            
            if href and 'capitulo' in href.lower():
                chapter_num = self._extract_chapter_number(href, title)
                
                chapters.append({
                    'url': href if href.startswith('http') else f"{self.base_url}{href}",
                    'title': title,
                    'number': chapter_num
                })
        
        chapters.sort(key=lambda x: x['number'])
        
        return chapters
    
    def _extract_chapter_number(self, url: str, title: str) -> int:
        """Extrae el número de capítulo de la URL o título"""
        match = re.search(r'capitulo-?(\d+)', url, re.I)
        if match:
            return int(match.group(1))
        
        match = re.search(r'cap[íi]tulo\s*(\d+)', title, re.I)
        if match:
            return int(match.group(1))
        
        match = re.search(r'(\d+)', title)
        return int(match.group(1)) if match else 0
    
    def scrape_chapter(self, chapter_url: str) -> Optional[str]:
        """Descarga el contenido de un capítulo"""
        try:
            print(f"  📄 Descargando: {chapter_url}")
            response = self.session.get(chapter_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content = self._extract_chapter_content(soup)
            
            if content:
                content = self._clean_content(content)
                return content
            
            return None
            
        except Exception as e:
            print(f"  ❌ Error en capítulo: {e}")
            return None
    
    def _extract_chapter_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el contenido del capítulo"""
        selectors = [
            '.entry-content',
            '.chapter-content',
            'article .content',
            '.post-content',
            'div[itemprop="articleBody"]'
        ]
        
        for selector in selectors:
            content_div = soup.select_one(selector)
            if content_div:
                for unwanted in content_div.select(
                    'script, style, .ads, .social-share, nav, '
                    '.sharedaddy, .jp-relatedposts, .wpcnt, '
                    '.code-block, .adsbox, iframe, .adsbygoogle'
                ):
                    unwanted.decompose()
                
                paragraphs = []
                for elem in content_div.find_all(['p', 'div'], recursive=True):
                    text = elem.get_text(separator=' ', strip=True)
                    
                    if (text and 
                        len(text) > 30 and
                        not self._is_spam_text(text)):
                        paragraphs.append(text)
                
                if paragraphs:
                    return '\n\n'.join(paragraphs)
        
        return None
    
    def _is_spam_text(self, text: str) -> bool:
        """Detecta si un texto es spam o contenido no deseado"""
        spam_patterns = [
            r'[Aa]umentar.*fuente',
            r'[Rr]educir.*fuente',
            r'[Rr]establecer.*fuente',
            r'[Pp]agina\s+[Aa]nterior',
            r'[Pp]agina\s+[Ss]iguiente',
            r'[Pp]atrocin',
            r'[Ii]nvitame\s+un\s+cafe',
            r'[Dd]onativo',
            r'\$.*=.*[Cc]ap',
            r'^NT:',
            r'^TL:',
            r'[Ss]kydark',
            r'[Cc]lick\s+to\s+rate',
            r'\[Total:.*Average:',
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, text, re.I):
                return True
        
        if len(text) < 50 and text.count('$') > 0:
            return True
        
        return False
    
    def _clean_content(self, content: str) -> str:
        """Limpia el contenido del capítulo de forma agresiva"""
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        spam_lines = [
            r'^.*[Aa]umentar.*fuente.*$',
            r'^.*[Rr]educir.*fuente.*$',
            r'^.*[Pp]agina\s+[Aa]nterior.*$',
            r'^.*[Pp]atrocin.*\d+\$.*$',
            r'^.*[Ii]nvitame\s+un\s+cafe.*$',
            r'^NT:.*$',
            r'^TL:.*$',
            r'^\s*\d+\s*$',
        ]
        
        for pattern in spam_lines:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.I)
        
        content = re.sub(
            r'Si estas leyendo las novelas.*?gringos.*?\.',
            '',
            content,
            flags=re.DOTALL | re.I
        )
        
        content = re.sub(
            r'(Patrocinio|patrocinar|Invitame).*?(\$|dolares).*?(cap|capitulo)',
            '',
            content,
            flags=re.I | re.DOTALL
        )
        
        lines = [line.strip() for line in content.split('\n')]
        lines = [line for line in lines if line]
        
        content = '\n\n'.join(lines)
        
        return content.strip()
    
    def download_image(self, image_url: str, output_dir: str) -> Optional[str]:
        """Descarga la imagen de portada"""
        if not image_url:
            return None
        
        try:
            print(f"🖼️  Descargando portada...")
            response = self.session.get(image_url, timeout=30)
            response.raise_for_status()
            
            ext = os.path.splitext(image_url)[1] or '.jpg'
            filename = f"cover{ext}"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Portada guardada: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error descargando imagen: {e}")
            return None
    
    def scrape_novel(
        self, 
        novel_slug: str, 
        start_chapter: int = 1, 
        end_chapter: Optional[int] = None,
        output_dir: str = "output"
    ) -> Dict:
        """Scrape completo de la novela"""
        
        Path(output_dir).mkdir(exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"🚀 Iniciando scraping: {novel_slug}")
        print(f"{'='*60}\n")
        
        novel_info = self.get_novel_info(novel_slug)
        
        print(f"\n📚 Novela: {novel_info['name']}")
        print(f"✍️  Autor: {novel_info['author']}")
        print(f"📊 Capítulos encontrados: {len(novel_info['chapters_urls'])}")
        
        chapters_urls = novel_info['chapters_urls']
        
        if end_chapter is None:
            end_chapter = len(chapters_urls)
        
        filtered_chapters = [
            ch for ch in chapters_urls 
            if start_chapter <= ch['number'] <= end_chapter
        ]
        
        print(f"📥 Descargando capítulos {start_chapter} al {end_chapter} ({len(filtered_chapters)} capítulos)")
        
        chapters_data = []
        skipped_chapters = []
        
        for i, chapter_info in enumerate(filtered_chapters, 1):
            print(f"\n[{i}/{len(filtered_chapters)}] Capítulo {chapter_info['number']}: {chapter_info['title']}")
            
            content = self.scrape_chapter(chapter_info['url'])
            
            if content and len(content) > 500:
                chapters_data.append({
                    "title": chapter_info['title'],
                    "content": content,
                    "order_number": chapter_info['number'],
                    "source_url": chapter_info['url']
                })
                print(f"  ✅ Descargado ({len(content)} caracteres)")
            else:
                skipped_chapters.append(chapter_info['number'])
                print(f"  ⚠️  Capítulo muy corto o sin contenido, OMITIDO")
            
            time.sleep(1)
        
        image_path = None
        if novel_info['image_url']:
            image_path = self.download_image(novel_info['image_url'], output_dir)
        
        output_data = {
            "name": novel_info['name'],
            "author": novel_info['author'],
            "description": novel_info['description'],
            "rating": novel_info['rating'],
            "status": novel_info['status'],
            "source_url": novel_info['source_url'],
            "image_path": image_path,
            "alternative_names": novel_info['alternative_names'],
            "genres": novel_info['genres'],
            "chapters": chapters_data
        }
        
        json_path = os.path.join(output_dir, f"{novel_slug}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ COMPLETADO")
        print(f"📁 JSON guardado: {json_path}")
        print(f"📊 Capítulos exitosos: {len(chapters_data)}/{len(filtered_chapters)}")
        if skipped_chapters:
            print(f"⚠️  Capítulos omitidos: {', '.join(map(str, skipped_chapters))}")
        if image_path:
            print(f"🖼️  Portada guardada")
        print(f"{'='*60}\n")
        
        return output_data


def main():
    parser = argparse.ArgumentParser(
        description='Scraper para NovelasLigera.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Descargar novela completa
  python scraper.py el-villano-que-quiere-vivir

  # Descargar capítulos 1-50
  python scraper.py el-villano-que-quiere-vivir --start 1 --end 50

  # Especificar directorio de salida
  python scraper.py el-villano-que-quiere-vivir --output ./novelas/
        """
    )
    
    parser.add_argument(
        'novel_slug',
        help='Slug de la novela (parte final de la URL)'
    )
    
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='Capítulo inicial (default: 1)'
    )
    
    parser.add_argument(
        '--end',
        type=int,
        default=None,
        help='Capítulo final (default: todos)'
    )
    
    parser.add_argument(
        '--output',
        default='output',
        help='Directorio de salida (default: ./output/)'
    )
    
    args = parser.parse_args()
    
    scraper = NovelasLigeraScraper()
    
    try:
        result = scraper.scrape_novel(
            novel_slug=args.novel_slug,
            start_chapter=args.start,
            end_chapter=args.end,
            output_dir=args.output
        )
        
        print("\n🎉 Listo para enviar a tu API!")
        print(f"📤 Usa el archivo: {args.output}/{args.novel_slug}.json")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping cancelado por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

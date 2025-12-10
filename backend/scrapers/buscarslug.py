 #!/usr/bin/env python3
"""
novel_finder.py
Ayuda a encontrar el slug de novelas en NovelasLigera.com
Soporta múltiples métodos: URL, slug, o búsqueda por nombre
"""

import requests
from bs4 import BeautifulSoup
import argparse
import re
from typing import Optional


def find_novel_slug(query: str) -> Optional[str]:
    """
    Encuentra el slug de una novela a partir de diferentes tipos de entrada:
    - URL completa: https://novelasligera.com/novela/el-villano-que-quiere-vivir/
    - Slug: el-villano-que-quiere-vivir
    - Nombre: El Villano Que Quiere Vivir
    """
    base_url = "https://novelasligera.com"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Método 1: Si ya es una URL completa, extraer el slug
    if query.startswith('http'):
        match = re.search(r'/novela/([^/]+)', query)
        if match:
            slug = match.group(1).rstrip('/')
            # Verificar que la URL existe
            test_url = f"{base_url}/novela/{slug}/"
            try:
                response = session.head(test_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    print(f"✅ URL válida detectada, slug: {slug}")
                    return slug
            except:
                pass
    
    # Método 2: Si parece un slug (solo letras, números, guiones)
    if re.match(r'^[a-z0-9-]+$', query.lower()):
        # Verificar que existe
        test_url = f"{base_url}/novela/{query}/"
        try:
            response = session.head(test_url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print(f"✅ Slug válido detectado: {query}")
                return query
        except:
            pass
    
    # Método 3: Buscar por nombre
    print(f"🔍 Buscando novela por nombre: '{query}'...")
    slug = search_novels_by_name(query, session)
    if slug:
        return slug
    
    return None


def search_novels_by_name(query: str, session: requests.Session = None) -> Optional[str]:
    """Busca novelas por nombre y devuelve el slug de la primera coincidencia"""
    
    if session is None:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    # URL de búsqueda
    search_url = f"https://novelasligera.com/?s={query.replace(' ', '+')}"
    
    try:
        response = session.get(search_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar resultados
        results = []
        
        # Diferentes selectores para los resultados de búsqueda
        article_selectors = [
            'article.post',
            '.search-results article',
            'article',
            '.post',
        ]
        
        articles = []
        for selector in article_selectors:
            articles = soup.select(selector)
            if articles:
                break
        
        if not articles:
            return None
        
        for article in articles[:10]:  # Máximo 10 resultados
            # Extraer título y link
            title_elem = article.find(['h2', 'h3', 'h1'])
            if not title_elem:
                continue
            
            link_elem = title_elem.find('a')
            if not link_elem or not link_elem.get('href'):
                continue
            
            url = link_elem.get('href')
            title = title_elem.get_text(strip=True)
            
            # Extraer slug de la URL
            match = re.search(r'/novela/([^/]+)', url)
            if match:
                slug = match.group(1)
                
                results.append({
                    'title': title,
                    'slug': slug,
                    'url': url
                })
        
        if not results:
            return None
        
        # Si solo hay un resultado, devolver el slug
        if len(results) == 1:
            print(f"✅ Encontrada: '{results[0]['title']}' (slug: {results[0]['slug']})")
            return results[0]['slug']
        
        # Si hay múltiples resultados, devolver el primero (más relevante)
        print(f"📚 Encontradas {len(results)} novela(s), usando la primera:")
        print(f"   '{results[0]['title']}' (slug: {results[0]['slug']})")
        return results[0]['slug']
        
    except Exception as e:
        print(f"❌ Error en la búsqueda: {e}")
        return None


def search_novels(query: str):
    """Busca novelas en NovelasLigera.com y muestra todos los resultados"""
    
    print(f"\n🔍 Buscando: '{query}'\n")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # URL de búsqueda
    search_url = f"https://novelasligera.com/?s={query.replace(' ', '+')}"
    
    try:
        response = session.get(search_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar resultados
        results = []
        
        # Diferentes selectores para los resultados de búsqueda
        article_selectors = [
            'article.post',
            '.search-results article',
            'article',
            '.post',
        ]
        
        articles = []
        for selector in article_selectors:
            articles = soup.select(selector)
            if articles:
                break
        
        if not articles:
            print("❌ No se encontraron resultados")
            return []
        
        for article in articles[:10]:  # Máximo 10 resultados
            # Extraer título y link
            title_elem = article.find(['h2', 'h3', 'h1'])
            if not title_elem:
                continue
            
            link_elem = title_elem.find('a')
            if not link_elem or not link_elem.get('href'):
                continue
            
            url = link_elem.get('href')
            title = title_elem.get_text(strip=True)
            
            # Extraer slug de la URL
            match = re.search(r'/novela/([^/]+)', url)
            if match:
                slug = match.group(1)
                
                # Extraer descripción si existe
                desc_elem = article.find(['p', 'div'], class_=re.compile('excerpt|summary|content', re.I))
                description = desc_elem.get_text(strip=True)[:150] if desc_elem else ""
                
                results.append({
                    'title': title,
                    'slug': slug,
                    'url': url,
                    'description': description
                })
        
        if not results:
            print("❌ No se encontraron novelas en los resultados")
            return []
        
        # Mostrar resultados
        print(f"📚 Encontradas {len(results)} novela(s):\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   Slug: {result['slug']}")
            print(f"   URL: {result['url']}")
            if result['description']:
                print(f"   📖 {result['description']}")
            print()
        
        # Mostrar comandos para descargar
        print("=" * 60)
        print("💡 Para descargar alguna, usa:\n")
        for result in results[:3]:  # Solo las primeras 3
            print(f"python supercraping.py {result['slug']} --start 1 --end 100")
        print("=" * 60 + "\n")
        
        return results
        
    except Exception as e:
        print(f"❌ Error en la búsqueda: {e}")
        return []


def list_popular_novels():
    """Lista las novelas populares o recientes"""
    
    print("\n📊 Obteniendo novelas populares...\n")
    
    try:
        response = requests.get("https://novelasligera.com", timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar secciones de novelas populares/recientes
        novel_links = []
        
        # Selectores comunes para listas de novelas
        sections = soup.select('.novel-list, .popular-novels, .recent-novels, .widget')
        
        for section in sections:
            links = section.select('a[href*="/novela/"]')
            for link in links[:15]:  # Máximo 15 por sección
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if href and title and '/novela/' in href:
                    match = re.search(r'/novela/([^/]+)', href)
                    if match:
                        slug = match.group(1)
                        novel_links.append({
                            'title': title,
                            'slug': slug,
                            'url': href
                        })
        
        # Eliminar duplicados
        seen = set()
        unique_novels = []
        for novel in novel_links:
            if novel['slug'] not in seen:
                seen.add(novel['slug'])
                unique_novels.append(novel)
        
        if not unique_novels:
            print("❌ No se pudieron obtener las novelas populares")
            return []
        
        print(f"📚 Novelas encontradas ({len(unique_novels)}):\n")
        
        for i, novel in enumerate(unique_novels[:20], 1):  # Mostrar máximo 20
            print(f"{i:2d}. {novel['title']}")
            print(f"    Slug: {novel['slug']}")
            print()
        
        print("=" * 60)
        print("💡 Para descargar alguna, usa:\n")
        print(f"python supercraping.py SLUG --start 1 --end 100")
        print("=" * 60 + "\n")
        
        return unique_novels
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description='Busca novelas en NovelasLigera.com y obtiene sus slugs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Buscar una novela específica (muestra todos los resultados)
  python novel_finder.py "solo leveling"
  
  # Buscar por palabra clave
  python novel_finder.py "villano"
  
  # Encontrar slug automáticamente (devuelve solo el slug)
  python novel_finder.py --find "El Villano Que Quiere Vivir"
  python novel_finder.py --find "https://novelasligera.com/novela/el-villano-que-quiere-vivir/"
  python novel_finder.py --find "el-villano-que-quiere-vivir"
  
  # Listar novelas populares
  python novel_finder.py --popular
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Término de búsqueda, URL, o slug'
    )
    
    parser.add_argument(
        '--popular',
        action='store_true',
        help='Listar novelas populares/recientes'
    )
    
    parser.add_argument(
        '--find',
        metavar='INPUT',
        help='Encuentra el slug automáticamente desde URL, slug, o nombre (devuelve solo el slug)'
    )
    
    args = parser.parse_args()
    
    if args.popular:
        list_popular_novels()
    elif args.find:
        slug = find_novel_slug(args.find)
        if slug:
            print(f"\n✅ Slug encontrado: {slug}\n")
            print(f"💡 Usa este comando para descargar:")
            print(f"python supercraping.py {slug} --start 1 --end 100\n")
        else:
            print(f"\n❌ No se pudo encontrar el slug para: '{args.find}'\n")
    elif args.query:
        search_novels(args.query)
    else:
        print("\n❌ Debes proporcionar un término de búsqueda, usar --find, o usar --popular\n")
        print("Ejemplos:")
        print("  python novel_finder.py 'solo leveling'")
        print("  python novel_finder.py --find 'El Villano Que Quiere Vivir'")
        print("  python novel_finder.py --popular\n")


if __name__ == "__main__":
    main()

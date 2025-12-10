 #!/usr/bin/env python3
"""
test_metadata.py
Prueba la extracción de metadatos sin descargar capítulos
"""

import sys
import json
from definitivo import NovelasLigeraScraper

def test_metadata(novel_slug: str):
    """Prueba solo la extracción de metadatos"""
    
    print(f"\n{'='*60}")
    print(f"🧪 Probando extracción de metadatos")
    print(f"{'='*60}\n")
    
    scraper = NovelasLigeraScraper()
    
    try:
        # Solo obtener info, no descargar capítulos
        novel_info = scraper.get_novel_info(novel_slug)
        
        # Mostrar resultados
        print(f"\n{'='*60}")
        print("📊 METADATOS EXTRAÍDOS")
        print(f"{'='*60}\n")
        
        print(f"📚 Título: {novel_info['name']}")
        print(f"✍️  Autor: {novel_info['author']}")
        print(f"📖 Descripción: {novel_info['description'][:200]}..." if novel_info['description'] else "📖 Descripción: (vacío)")
        print(f"⭐ Rating: {novel_info['rating']}")
        print(f"📊 Estado: {novel_info['status']}")
        print(f"🏷️  Géneros: {', '.join(novel_info['genres'])}")
        print(f"📝 Nombres alternativos: {', '.join(novel_info['alternative_names'])}")
        print(f"🖼️  Imagen URL: {novel_info['image_url']}")
        print(f"📑 Total capítulos: {len(novel_info['chapters_urls'])}")
        
        # JSON completo
        print(f"\n{'='*60}")
        print("📄 JSON COMPLETO (sin capítulos):")
        print(f"{'='*60}\n")
        
        # Crear JSON sin los capítulos para que sea más legible
        json_output = {
            "name": novel_info['name'],
            "author": novel_info['author'],
            "description": novel_info['description'],
            "rating": novel_info['rating'],
            "status": novel_info['status'],
            "source_url": novel_info['source_url'],
            "image_url": novel_info['image_url'],
            "alternative_names": novel_info['alternative_names'],
            "genres": novel_info['genres'],
            "total_chapters": len(novel_info['chapters_urls'])
        }
        
        print(json.dumps(json_output, indent=2, ensure_ascii=False))
        
        # Verificación
        print(f"\n{'='*60}")
        print("✅ VERIFICACIÓN")
        print(f"{'='*60}\n")
        
        issues = []
        
        if novel_info['author'] == "Desconocido":
            issues.append("⚠️  Autor no encontrado")
        
        if not novel_info['description'] or len(novel_info['description']) < 50:
            issues.append("⚠️  Descripción vacía o muy corta")
        
        if not novel_info['genres']:
            issues.append("⚠️  No se encontraron géneros")
        
        if not novel_info['alternative_names']:
            issues.append("ℹ️  No se encontraron nombres alternativos")
        
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("✅ Todos los metadatos extraídos correctamente")
        
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso: python test_metadata.py SLUG-DE-LA-NOVELA")
        print("\nEjemplo:")
        print("  python test_metadata.py el-villano-que-quiere-vivir\n")
        sys.exit(1)
    
    slug = sys.argv[1]
    success = test_metadata(slug)
    
    sys.exit(0 if success else 1)

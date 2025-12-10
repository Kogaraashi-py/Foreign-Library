 #!/usr/bin/env python3
"""
send_to_api.py
Script para enviar el JSON generado por el scraper a tu API
Diseñado para funcionar dentro de la carpeta scrapers/
"""

import requests
import json
import argparse
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent))

# IMPORTANTE: Importar configuración de tu proyecto
try:
    from core.config import settings
    API_BASE_URL = str(settings.API_V1_STR) if hasattr(settings, 'API_V1_STR') else "http://localhost:8000"
except ImportError:
    # Fallback si no puede importar
    API_BASE_URL = "http://localhost:8000"
    print("⚠️  No se pudo importar configuración, usando URL por defecto")


def upload_novel_to_api(
    json_path: str, 
    api_url: str = None,
    api_key: str = None
):
    """
    Envía el JSON de la novela a tu API
    
    Args:
        json_path: Ruta al archivo JSON (relativa o absoluta)
        api_url: URL del endpoint (default: tu servidor local)
        api_key: API key si requiere autenticación
    """
    
    print(f"\n{'='*60}")
    print(f"📤 Enviando novela a API")
    print(f"{'='*60}\n")
    
    # Convertir a Path absoluto
    json_path = Path(json_path)
    if not json_path.is_absolute():
        json_path = Path(__file__).parent / json_path
    
    # Verificar que existe
    if not json_path.exists():
        print(f"❌ Error: No se encontró el archivo {json_path}")
        return False
    
    # Leer el JSON
    print(f"📖 Leyendo: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        novel_data = json.load(f)
    
    print(f"✓ Novela: {novel_data.get('name', 'Sin nombre')}")
    print(f"✓ Capítulos: {len(novel_data.get('chapters', []))}")
    
    # Procesar ruta de imagen
    image_path = novel_data.get('image_path')
    if image_path:
        # Convertir a ruta absoluta si es relativa
        img_path = Path(image_path)
        if not img_path.is_absolute():
            # Asumir que está en la misma carpeta que el JSON
            img_path = json_path.parent / img_path.name
        
        if img_path.exists():
            # Actualizar con ruta absoluta
            novel_data['image_path'] = str(img_path.absolute())
            print(f"🖼️  Imagen: {img_path.name} ✅")
        else:
            print(f"⚠️  Imagen no encontrada: {img_path}")
            novel_data['image_path'] = None
    
    # URL del endpoint
    if not api_url:
        api_url = f"{API_BASE_URL}/admin/import-novel"
    
    # Headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    # Enviar
    print(f"\n📡 Enviando a: {api_url}")
    print(f"📦 Tamaño del JSON: {len(json.dumps(novel_data)) / 1024:.1f} KB")
    
    try:
        response = requests.post(
            api_url,
            json=novel_data,
            headers=headers,
            timeout=300  # 5 minutos
        )
        
        response.raise_for_status()
        
        print(f"\n✅ ¡Éxito!")
        print(f"Status: {response.status_code}")
        
        # Mostrar respuesta
        try:
            result = response.json()
            print(f"\n📊 Respuesta de la API:")
            print(f"   Novel ID: {result.get('novel_id')}")
            print(f"   Message: {result.get('message')}")
            
            if 'stats' in result:
                stats = result['stats']
                print(f"\n📈 Estadísticas:")
                print(f"   Nombres alternativos: {stats.get('alternative_names_created', 0)}")
                print(f"   Géneros creados: {stats.get('genres_created', 0)}")
                print(f"   Géneros asociados: {stats.get('genres_associated', 0)}")
                print(f"   Capítulos creados: {stats.get('chapters_created', 0)}")
                print(f"   Portada subida: {'✅' if stats.get('cover_uploaded') else '❌'}")
        except:
            print(f"\nRespuesta: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: No se pudo conectar a {api_url}")
        print(f"   ¿Está corriendo tu servidor FastAPI?")
        print(f"   Ejecuta: uvicorn main:app --reload")
        return False
        
    except requests.exceptions.Timeout:
        print(f"\n❌ Error: Timeout después de 5 minutos")
        print(f"   La novela tiene muchos capítulos, intenta con menos")
        return False
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Error HTTP: {e}")
        
        if hasattr(e.response, 'text'):
            print(f"\nRespuesta del servidor:")
            try:
                error_detail = e.response.json()
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                print(e.response.text)
        
        return False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Envía novelas a tu API FastAPI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Enviar novela (desde carpeta scrapers/)
  python send_to_api.py mis_novelas/el-villano-que-quiere-vivir.json

  # Especificar URL personalizada
  python send_to_api.py mis_novelas/mi-novela.json \\
    --url http://192.168.1.100:8000/admin/import-novel

  # Con autenticación
  python send_to_api.py mis_novelas/mi-novela.json --key TOKEN

  # Enviar todas las novelas de la carpeta
  for file in mis_novelas/*.json; do
    python send_to_api.py "$file"
    sleep 2
  done
        """
    )
    
    parser.add_argument(
        'json_file',
        help='Ruta al JSON (ej: mis_novelas/novela.json)'
    )
    
    parser.add_argument(
        '--url',
        default=None,
        help='URL del endpoint (default: http://localhost:8000/admin/import-novel)'
    )
    
    parser.add_argument(
        '--key',
        default=None,
        help='API key para autenticación'
    )
    
    args = parser.parse_args()
    
    success = upload_novel_to_api(
        json_path=args.json_file,
        api_url=args.url,
        api_key=args.key
    )
    
    if success:
        print(f"\n🎉 Novela importada correctamente!")
        print(f"   Puedes verla en tu aplicación web\n")
    else:
        print(f"\n⚠️  La importación falló\n")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

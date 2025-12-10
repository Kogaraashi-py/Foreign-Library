 #!/usr/bin/env python3
"""
send_to_api.py
Script para enviar el JSON generado por el scraper a tu API
Envía el JSON tal cual sin modificar imágenes ni convertir a base64
"""

import requests
import json
import argparse
import os
from pathlib import Path


def upload_novel_to_api(json_path: str, api_url: str, api_key: str = None):
    """
    Envía el JSON de la novela a tu API
    
    Args:
        json_path: Ruta al archivo JSON
        api_url: URL del endpoint de tu API (ej: http://localhost:8000/novels/upload)
        api_key: API key si tu endpoint requiere autenticación
    """
    
    print(f"\n{'='*60}")
    print(f"📤 Enviando novela a API")
    print(f"{'='*60}\n")
    
    # Verificar que el archivo existe
    if not os.path.exists(json_path):
        print(f"❌ Error: No se encontró el archivo {json_path}")
        return False
    
    # Leer el JSON
    print(f"📖 Leyendo: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        novel_data = json.load(f)
    
    print(f"✓ Novela: {novel_data.get('name', 'Sin nombre')}")
    print(f"✓ Capítulos: {len(novel_data.get('chapters', []))}")

    # Mantener la imagen como está - no modificar
    image_path = novel_data.get('image_path')
    if image_path:
        print(f"🖼️  Imagen: {image_path}")
        if os.path.exists(image_path):
            print("  ✅ Imagen local encontrada")
        else:
            print("  ⚠️  Imagen local no encontrada, enviando ruta")
    
    # Preparar headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    # Enviar a la API
    print(f"\n📡 Enviando a: {api_url}")
    
    try:
        response = requests.post(
            api_url,
            json=novel_data,
            headers=headers,
            timeout=300  # 5 minutos timeout para novelas grandes
        )
        
        response.raise_for_status()
        
        print(f"\n✅ ¡Éxito!")
        print(f"Status: {response.status_code}")
        
        # Mostrar respuesta de la API
        try:
            result = response.json()
            print(f"\nRespuesta de la API:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except:
            print(f"\nRespuesta: {response.text}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error al enviar:")
        print(f"{type(e).__name__}: {e}")
        
        if hasattr(e.response, 'text'):
            print(f"\nRespuesta del servidor:")
            print(e.response.text)
        
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Envía el JSON de una novela a tu API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Enviar a API local
  python upload_api.py output/el-villano-que-quiere-vivir.json \\
    --url http://localhost:8000/novels/upload

  # Enviar con autenticación
  python upload_api.py output/mi-novela.json \\
    --url https://mi-api.com/novels/upload \\
    --key mi_api_key_secreta

  # Enviar todos los JSON de una carpeta
  for file in output/*.json; do
    python upload_api.py "$file" --url http://localhost:8000/novels/upload
  done
        """
    )
    
    parser.add_argument(
        'json_file',
        help='Ruta al archivo JSON generado por el scraper'
    )
    
    parser.add_argument(
        '--url',
        required=True,
        help='URL del endpoint de tu API'
    )
    
    parser.add_argument(
        '--key',
        default=None,
        help='API key para autenticación (opcional)'
    )
    
    args = parser.parse_args()
    
    success = upload_novel_to_api(
        json_path=args.json_file,
        api_url=args.url,
        api_key=args.key
    )
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()

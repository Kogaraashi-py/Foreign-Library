 #!/usr/bin/env python3
"""
batch_download.py
Script para descargar múltiples novelas automáticamente
Usa definitivo.py para el scraping
"""

import sys
import time
from definitivo import NovelasLigeraScraper


# ============================================================
# CONFIGURACIÓN - Edita esta lista con las novelas que quieres
# ============================================================

NOVELAS = [
    {
        'slug': 'el-villano-que-quiere-vivir',
        'start': 1,
        'end': 5,
    },
    {
        'slug': 'las-heroinas-estan-intentando-matarme',
        'start': 1,
        'end': 5,
    },
    # Agrega más novelas aquí...
    # {
    #     'slug': 'nombre-de-otra-novela',
    #     'start': 1,
    #     'end': None,  # None = todos los capítulos
    # },
]

OUTPUT_DIR = './mis_novelas'
PAUSE_BETWEEN_NOVELS = 5  # segundos

# ============================================================


def main():
    print("=" * 60)
    print("📚 Descargador por Lotes - NovelasLigera.com")
    print("=" * 60)
    print(f"\nTotal de novelas a descargar: {len(NOVELAS)}\n")
    
    scraper = NovelasLigeraScraper()
    
    success = 0
    failed = 0
    failed_novels = []
    
    for i, novel_config in enumerate(NOVELAS, 1):
        slug = novel_config['slug']
        start = novel_config.get('start', 1)
        end = novel_config.get('end', None)
        
        print("\n" + "-" * 60)
        print(f"📖 [{i}/{len(NOVELAS)}] Descargando: {slug}")
        if end:
            print(f"📥 Capítulos: {start} al {end}")
        else:
            print(f"📥 Capítulos: desde {start} hasta el final")
        print("-" * 60)
        
        try:
            result = scraper.scrape_novel(
                novel_slug=slug,
                start_chapter=start,
                end_chapter=end,
                output_dir=OUTPUT_DIR
            )
            
            print(f"✅ {slug} descargada exitosamente")
            success += 1
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Descarga cancelada por el usuario")
            break
            
        except Exception as e:
            print(f"❌ Error descargando {slug}: {e}")
            failed += 1
            failed_novels.append(slug)
        
        # Pausa entre novelas (excepto en la última)
        if i < len(NOVELAS):
            print(f"\n⏳ Esperando {PAUSE_BETWEEN_NOVELS} segundos antes de la siguiente...")
            time.sleep(PAUSE_BETWEEN_NOVELS)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Exitosas: {success}/{len(NOVELAS)}")
    print(f"❌ Fallidas: {failed}/{len(NOVELAS)}")
    
    if failed_novels:
        print(f"\n⚠️  Novelas que fallaron:")
        for novel in failed_novels:
            print(f"  • {novel}")
    
    print(f"\n📁 Archivos guardados en: {OUTPUT_DIR}/")
    print("=" * 60 + "\n")
    
    print("💡 Próximos pasos:")
    print(f"  1. Verifica los JSON: python verify_json.py {OUTPUT_DIR}/*.json")
    print(f"  2. Sube a tu API: python send_to_api.py {OUTPUT_DIR}/NOVELA.json --url TU_API")


if __name__ == "__main__":
    main()

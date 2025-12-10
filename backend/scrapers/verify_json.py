#!/usr/bin/env python3
"""
Script para verificar la calidad del JSON antes de enviarlo a la API
"""

import json
import argparse
import re
from typing import Dict, List


class NovelJSONVerifier:
    def __init__(self, json_path: str):
        self.json_path = json_path
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.errors = []
        self.warnings = []
        self.info = []
    
    def verify(self) -> bool:
        """Ejecuta todas las verificaciones"""
        print(f"\n{'='*60}")
        print(f"🔍 Verificando: {self.json_path}")
        print(f"{'='*60}\n")
        
        self._check_basic_fields()
        self._check_chapters()
        self._check_content_quality()
        self._check_spam()
        
        self._print_results()
        
        return len(self.errors) == 0
    
    def _check_basic_fields(self):
        """Verifica campos básicos requeridos"""
        required_fields = ['name', 'author', 'chapters']
        
        for field in required_fields:
            if field not in self.data or not self.data[field]:
                self.errors.append(f"Campo requerido faltante: {field}")
        
        # Verificar que el nombre no sea genérico
        if self.data.get('name') in ['Título Desconocido', 'Sin nombre', '']:
            self.warnings.append("El título parece ser genérico o vacío")
        
        # Verificar autor
        if self.data.get('author') == 'Desconocido':
            self.warnings.append("Autor desconocido - considera buscar esta información manualmente")
        
        # Verificar descripción
        if not self.data.get('description') or len(self.data.get('description', '')) < 50:
            self.warnings.append("Descripción muy corta o vacía")
    
    def _check_chapters(self):
        """Verifica la estructura de capítulos"""
        chapters = self.data.get('chapters', [])
        
        if not chapters:
            self.errors.append("No hay capítulos en el JSON")
            return
        
        self.info.append(f"Total de capítulos: {len(chapters)}")
        
        # Verificar que tengan los campos requeridos
        required_chapter_fields = ['title', 'content', 'order_number', 'source_url']
        
        for i, chapter in enumerate(chapters):
            for field in required_chapter_fields:
                if field not in chapter:
                    self.errors.append(f"Capítulo {i+1}: falta campo '{field}'")
        
        # Verificar orden correcto
        order_numbers = [ch.get('order_number', 0) for ch in chapters]
        if order_numbers != sorted(order_numbers):
            self.warnings.append("Los capítulos no están en orden correcto")
        
        # Verificar duplicados
        if len(order_numbers) != len(set(order_numbers)):
            self.warnings.append("Hay números de capítulo duplicados")
    
    def _check_content_quality(self):
        """Verifica la calidad del contenido"""
        chapters = self.data.get('chapters', [])
        
        short_chapters = []
        empty_chapters = []
        avg_length = 0
        
        for ch in chapters:
            content = ch.get('content', '')
            length = len(content)
            
            if length == 0:
                empty_chapters.append(ch.get('order_number', '?'))
            elif length < 500:
                short_chapters.append(ch.get('order_number', '?'))
            
            avg_length += length
        
        if chapters:
            avg_length = avg_length // len(chapters)
            self.info.append(f"Longitud promedio: {avg_length:,} caracteres")
        
        if empty_chapters:
            self.errors.append(f"Capítulos vacíos: {', '.join(map(str, empty_chapters))}")
        
        if short_chapters:
            self.warnings.append(f"Capítulos muy cortos (<500 chars): {', '.join(map(str, short_chapters))}")
    
    def _check_spam(self):
        """Detecta contenido spam en los capítulos"""
        spam_patterns = [
            (r'[Pp]atrocin', 'Menciones de patrocinio'),
            (r'[Ii]nvitame.*cafe', 'Invitaciones a café'),
            (r'\$.*=.*cap', 'Precios de capítulos'),
            (r'[Aa]umentar.*fuente', 'Controles de fuente'),
            (r'[Pp]agina\s+[Aa]nterior', 'Navegación de página'),
        ]
        
        chapters = self.data.get('chapters', [])
        spam_found = {}
        
        for ch in chapters:
            content = ch.get('content', '')
            ch_num = ch.get('order_number', '?')
            
            for pattern, name in spam_patterns:
                if re.search(pattern, content, re.I):
                    if name not in spam_found:
                        spam_found[name] = []
                    spam_found[name].append(ch_num)
        
        if spam_found:
            for spam_type, chapters_affected in spam_found.items():
                if len(chapters_affected) > 3:
                    self.warnings.append(
                        f"Spam detectado ({spam_type}): "
                        f"{len(chapters_affected)} capítulos afectados"
                    )
    
    def _print_results(self):
        """Imprime los resultados de la verificación"""
        print("\n📊 RESULTADOS:\n")
        
        # Info
        if self.info:
            print("ℹ️  Información:")
            for msg in self.info:
                print(f"  • {msg}")
            print()
        
        # Warnings
        if self.warnings:
            print("⚠️  Advertencias:")
            for msg in self.warnings:
                print(f"  • {msg}")
            print()
        
        # Errors
        if self.errors:
            print("❌ Errores:")
            for msg in self.errors:
                print(f"  • {msg}")
            print()
        
        # Resumen
        print(f"{'='*60}")
        if not self.errors:
            print("✅ JSON VÁLIDO - Listo para enviar a la API")
        else:
            print(f"❌ JSON INVÁLIDO - {len(self.errors)} error(es) encontrado(s)")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Verifica la calidad del JSON antes de enviarlo a la API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Verificar un JSON
  python verify_json.py output/el-villano-que-quiere-vivir.json

  # Verificar todos los JSON de una carpeta
  for file in output/*.json; do
    python verify_json.py "$file"
  done
        """
    )
    
    parser.add_argument(
        'json_file',
        help='Ruta al archivo JSON a verificar'
    )
    
    args = parser.parse_args()
    
    try:
        verifier = NovelJSONVerifier(args.json_file)
        is_valid = verifier.verify()
        
        exit(0 if is_valid else 1)
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {args.json_file}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: JSON inválido - {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        exit(1)


if __name__ == "__main__":
    main()

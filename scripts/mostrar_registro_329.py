#!/usr/bin/env python3
"""
Script para cargar el dataset FOLIO y mostrar el contenido del registro con id 329.
"""

import json
from pathlib import Path

# Ruta al dataset
dataset_path = Path(__file__).parent.parent / 'datasets' / 'folio_train.json'

def main():
    print(f"Cargando dataset desde: {dataset_path}")
    
    # Cargar el dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        folio_data = json.load(f)
    
    print(f"✓ Dataset cargado: {len(folio_data)} registros\n")
    
    # Obtener el registro con índice 329
    registro_id = 291
    
    if registro_id >= len(folio_data):
        print(f"❌ Error: El registro {registro_id} no existe. El dataset tiene {len(folio_data)} registros (índices 0-{len(folio_data)-1})")
        return
    
    registro = folio_data[registro_id]
    
    print("=" * 80)
    print(f"REGISTRO ID {registro_id}")
    print("=" * 80)
    print()
    
    # Mostrar el contenido completo del registro
    print(json.dumps(registro, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()


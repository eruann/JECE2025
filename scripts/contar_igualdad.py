#!/usr/bin/env python3
"""
Script para contar cuántos registros tienen el símbolo "=" en premises-FOL o conclusion-FOL.
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
    
    total_registros = len(folio_data)
    print(f"✓ Dataset cargado: {total_registros} registros\n")
    
    # Contar registros con "=" en premises-FOL o conclusion-FOL
    registros_con_igualdad = 0
    
    for registro in folio_data:
        premises_fol = registro.get('premises-FOL', '')
        conclusion_fol = registro.get('conclusion-FOL', '')
        
        # Verificar si "=" aparece en alguno de los dos campos
        if '=' in premises_fol or '=' in conclusion_fol:
            registros_con_igualdad += 1
    
    # Calcular porcentaje
    porcentaje = (registros_con_igualdad / total_registros) * 100
    
    # Mostrar resultados
    print("=" * 80)
    print("RESULTADOS: Registros con símbolo '=' en premises-FOL o conclusion-FOL")
    print("=" * 80)
    print()
    print(f"Total de registros: {total_registros}")
    print(f"Registros con '=': {registros_con_igualdad}")
    print(f"Porcentaje: {porcentaje:.2f}%")
    print()

if __name__ == '__main__':
    main()


"""
Pipeline completo para procesar el dataset FOLIO.

Este script ejecuta todas las tareas en secuencia:
1. Descarga el dataset FOLIO
2. Para cada registro, construye el condicional global
3. Parsea y calcula métricas
4. Exporta resultados a JSON y SVG
"""

import sys
from pathlib import Path
import json
from tqdm import tqdm

# Importar módulos desde src/ (archivos simples, no paquete instalable)
# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from download_folio import download_folio_dataset
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics
from serialize import export_complete_analysis


def process_folio_dataset(
    output_dir='outputs',
    max_records=None,
    save_json=True,
    save_svg=True
):
    """
    Procesa el dataset FOLIO completo.
    
    Args:
        output_dir: Directorio donde guardar resultados
        max_records: Número máximo de registros a procesar (None = todos)
        save_json: Si guardar JSON
        save_svg: Si guardar SVG
    """
    print("=" * 80)
    print("Pipeline de Procesamiento FOLIO")
    print("=" * 80)
    
    # 1. Descargar dataset
    print("\n1. Descargando dataset FOLIO...")
    try:
        dataset = download_folio_dataset(save_path='datasets/folio_train.json', split='train')
        print(f"✓ Dataset descargado: {len(dataset)} registros")
    except Exception as e:
        print(f"✗ Error al descargar dataset: {e}")
        return
    
    # 2. Procesar cada registro
    print(f"\n2. Procesando registros...")
    results = []
    
    records_to_process = dataset[:max_records] if max_records else dataset
    
    for idx, record in enumerate(tqdm(records_to_process, desc="Procesando")):
        try:
            premises = record.get('premises', [])
            conclusion = record.get('conclusion', '')
            
            if not premises or not conclusion:
                continue
            
            # Parsear condicional global
            ast = parse_global_conditional(premises, conclusion)
            
            # Calcular métricas
            metrics = calculate_all_metrics(ast)
            
            # Construir fórmula original para referencia
            formula = f"({' ∧ '.join(premises)}) → {conclusion}"
            
            # Guardar resultado
            result = {
                'record_id': idx,
                'original_formula': formula,
                'premises': premises,
                'conclusion': conclusion,
                'metrics': metrics
            }
            
            results.append(result)
            
            # Exportar análisis individual si se solicita
            if save_json or save_svg:
                export_complete_analysis(
                    ast,
                    original_formula=formula,
                    output_dir=output_dir,
                    base_name=f'record_{idx:05d}'
                )
        
        except Exception as e:
            print(f"\n⚠ Error procesando registro {idx}: {e}")
            continue
    
    # 3. Guardar resumen
    print(f"\n3. Guardando resumen...")
    summary_path = Path(output_dir) / 'summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_processed': len(results),
            'records': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Resumen guardado en: {summary_path}")
    print(f"\n✓ Pipeline completado: {len(results)} registros procesados")
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Procesar dataset FOLIO')
    parser.add_argument('--max-records', type=int, default=None,
                       help='Número máximo de registros a procesar')
    parser.add_argument('--output-dir', type=str, default='outputs',
                       help='Directorio de salida')
    parser.add_argument('--no-svg', action='store_true',
                       help='No generar archivos SVG')
    
    args = parser.parse_args()
    
    process_folio_dataset(
        output_dir=args.output_dir,
        max_records=args.max_records,
        save_json=True,
        save_svg=not args.no_svg
    )


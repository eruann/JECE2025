"""
Prueba rápida de alineación de subfórmulas con texto natural usando el ejemplo 329.

Soporta OpenAI y OpenRouter APIs.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict

# Agregar src/ al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from download_folio import download_folio_dataset
from build_conditionals import parse_global_conditional
from subformula_alignment import (
    extract_all_subformulas,
    align_subformula,
    FREE_MODELS
)


def test_example_329(provider: str = "openrouter", 
                     model: str = None,
                     max_subformulas: int = 5):
    """
    Prueba rápida con el ejemplo 329.
    
    Args:
        provider: "openai" o "openrouter"
        model: Modelo específico (opcional, usa defaults)
        max_subformulas: Número máximo de subfórmulas a probar (para ahorrar costos)
    """
    print("=" * 80)
    print("PRUEBA DE ALINEACIÓN DE SUBFÓRMULAS - Ejemplo 329")
    print("=" * 80)
    print(f"Proveedor: {provider}")
    if model:
        # Verificar si es un modelo gratuito
        model_lower = model.lower()
        if model_lower in FREE_MODELS:
            print(f"Modelo: {model} (GRATIS ✅)")
        else:
            print(f"Modelo: {model}")
    else:
        print(f"Modelo: default")
    print(f"Máximo de subfórmulas a probar: {max_subformulas}")
    print("\n💡 Tip: Usa --model deepseek-r1 o --model qwen para modelos GRATUITOS")
    
    # 1. Cargar dataset y encontrar ejemplo 329
    print("\n1. Cargando dataset FOLIO...")
    try:
        dataset = download_folio_dataset(split='train')
    except Exception as e:
        print(f"❌ Error al cargar dataset: {e}")
        print("   Asegúrate de tener HF_TOKEN configurado en .env")
        return
    
    record_329 = None
    for record in dataset:
        if record.get('example_id') == 329:
            record_329 = record
            break
    
    if not record_329:
        print("❌ No se encontró el ejemplo 329")
        return
    
    print("✓ Ejemplo 329 encontrado")
    
    # 2. Extraer datos
    premises_fol = record_329.get('premises-FOL', record_329.get('premises', []))
    conclusion_fol = record_329.get('conclusion-FOL', record_329.get('conclusion', ''))
    
    premises_natural = record_329.get('premises', [])
    conclusion_natural = record_329.get('conclusion', '')
    
    # Normalizar formatos
    if isinstance(premises_natural, str):
        premises_natural = [p.strip() for p in premises_natural.split('\n') if p.strip()]
    if isinstance(premises_fol, str):
        premises_fol = [p.strip() for p in premises_fol.split('\n') if p.strip()]
    if not isinstance(premises_natural, list):
        premises_natural = [premises_natural] if premises_natural else []
    if not isinstance(premises_fol, list):
        premises_fol = [premises_fol] if premises_fol else []
    
    print(f"\n2. Premisas naturales: {len(premises_natural)}")
    for i, p in enumerate(premises_natural, 1):
        preview = p[:80] + "..." if len(p) > 80 else p
        print(f"   {i}. {preview}")
    print(f"\n   Conclusión natural: {conclusion_natural[:80]}...")
    
    # 3. Parsear AST
    print("\n3. Parseando fórmulas FOL...")
    try:
        ast = parse_global_conditional(premises_fol, conclusion_fol)
        print("✓ AST parseado correctamente")
    except Exception as e:
        print(f"❌ Error al parsear: {e}")
        return
    
    # 4. Extraer subfórmulas
    print("\n4. Extrayendo subfórmulas del AST...")
    subformulas = extract_all_subformulas(ast)
    print(f"✓ Encontradas {len(subformulas)} subfórmulas")
    
    # Mostrar primeras 5
    print("\n   Primeras 5 subfórmulas:")
    for i, (fol_str, node, meta) in enumerate(subformulas[:5], 1):
        preview = fol_str[:60] + "..." if len(fol_str) > 60 else fol_str
        print(f"   {i}. [{meta['node_type']}] {preview}")
    
    # 5. Probar alineación con LLM
    print(f"\n5. Probando alineación con LLM (primeras {max_subformulas} subfórmulas)...")
    
    # Verificar API key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    if provider == "openrouter":
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("⚠ Advertencia: OPENROUTER_API_KEY no encontrada en .env")
            print("   Configura tu API key en .env: OPENROUTER_API_KEY=tu_key")
    elif provider == "openai":
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠ Advertencia: OPENAI_API_KEY no encontrada en .env")
            print("   Configura tu API key en .env: OPENAI_API_KEY=tu_key")
    
    if not api_key:
        print("\n❌ No se puede continuar sin API key")
        return
    
    print("   API key encontrada ✓")
    
    results = []
    for i, (fol_str, node, meta) in enumerate(subformulas[:max_subformulas], 1):
        print(f"\n   [{i}/{min(max_subformulas, len(subformulas))}] Subfórmula:")
        preview = fol_str[:80] + "..." if len(fol_str) > 80 else fol_str
        print(f"   FOL: {preview}")
        print(f"   Tipo: {meta['node_type']}")
        
        try:
            alignment = align_subformula(
                fol_str,
                premises_natural,
                conclusion_natural,
                provider=provider,
                model=model
            )
            
            results.append({
                'subformula_fol': fol_str,
                'node_type': meta['node_type'],
                'metadata': meta,
                'alignment': alignment
            })
            
            if 'error' in alignment:
                print(f"   ❌ Error: {alignment['error']}")
            else:
                span = alignment.get('span', 'N/A')
                span_preview = span[:60] + "..." if len(span) > 60 else span
                print(f"   ✓ Span encontrado: \"{span_preview}\"")
                print(f"   ✓ Ubicación: {alignment.get('location', 'N/A')}")
                print(f"   ✓ Confianza: {alignment.get('confidence', 0):.2f}")
                if 'explanation' in alignment:
                    exp_preview = alignment['explanation'][:60] + "..." if len(alignment['explanation']) > 60 else alignment['explanation']
                    print(f"   ✓ Explicación: {exp_preview}")
        
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
            results.append({
                'subformula_fol': fol_str,
                'node_type': meta['node_type'],
                'metadata': meta,
                'alignment': {'error': str(e)}
            })
    
    # 6. Guardar resultados
    output_file = project_root / 'outputs' / 'random_test' / '329' / 'subformula_alignment_test.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'example_id': 329,
        'provider': provider,
        'model': model or 'default',
        'premises_natural': premises_natural,
        'conclusion_natural': conclusion_natural,
        'premises_fol': premises_fol,
        'conclusion_fol': conclusion_fol,
        'total_subformulas': len(subformulas),
        'tested_subformulas': len(results),
        'max_subformulas_tested': max_subformulas,
        'results': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n6. Resultados guardados en: {output_file}")
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Total de subfórmulas encontradas: {len(subformulas)}")
    print(f"Subfórmulas probadas: {len(results)}")
    
    successful = sum(1 for r in results if 'error' not in r.get('alignment', {}))
    failed = len(results) - successful
    
    print(f"✓ Exitosas: {successful}")
    print(f"❌ Fallidas: {failed}")
    
    if successful > 0:
        avg_confidence = sum(
            r.get('alignment', {}).get('confidence', 0) 
            for r in results 
            if 'error' not in r.get('alignment', {})
        ) / successful
        print(f"Confianza promedio: {avg_confidence:.2f}")
    
    print("\n" + "=" * 80)
    print("PRUEBA COMPLETADA")
    print("=" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Prueba de alineación de subfórmulas con ejemplo 329')
    parser.add_argument('--provider', choices=['openai', 'openrouter'], default='openrouter',
                       help='Proveedor de LLM a usar (default: openrouter)')
    parser.add_argument('--model', type=str, default=None,
                       help='Modelo específico (ej: "openai/gpt-4o-mini", "deepseek-r1", "qwen", "anthropic/claude-3-haiku")')
    parser.add_argument('--max-subformulas', type=int, default=5,
                       help='Número máximo de subfórmulas a probar (default: 5)')
    
    args = parser.parse_args()
    
    test_example_329(
        provider=args.provider,
        model=args.model,
        max_subformulas=args.max_subformulas
    )


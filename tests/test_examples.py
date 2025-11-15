"""
Script de prueba con los ejemplos proporcionados para validar el pipeline completo.

Ejemplo 1: Sin XOR
Ejemplo 2: Con XOR (⊕)
"""

# Importar módulos desde src/ (archivos simples, no paquete instalable)
import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from build_conditionals import build_global_conditional, parse_global_conditional
from metrics import calculate_all_metrics
from serialize import export_complete_analysis
from fol_parser import FOLParser


def test_example_1():
    """Prueba el Ejemplo 1: Sin XOR."""
    print("=" * 80)
    print("EJEMPLO 1: Sin XOR")
    print("=" * 80)
    
    premises = [
        "GenusBulbophyllum(bulbophyllumAttenuatum)",
        "∀x (GenusBulbophyllum(x) → Orchid(x))"
    ]
    conclusion = "¬Orchid(bulbophyllumAttenuatum)"
    
    print("\nPremisas:")
    for i, prem in enumerate(premises, 1):
        print(f"  {i}. {prem}")
    print(f"\nConclusión: {conclusion}")
    
    # Construir condicional global
    conditional = build_global_conditional(premises, conclusion)
    print(f"\nCondicional global:")
    print(f"  {conditional}")
    
    # Parsear
    print("\nParseando fórmula...")
    try:
        ast = parse_global_conditional(premises, conclusion)
        print("✓ Parseo exitoso")
        print(f"\nAST (representación): {ast}")
    except Exception as e:
        print(f"✗ Error al parsear: {e}")
        return
    
    # Calcular métricas
    print("\nCalculando métricas...")
    metrics = calculate_all_metrics(ast)
    
    print("\nMétricas calculadas:")
    print(f"  Profundidad total: {metrics['total_depth']}")
    print(f"  Profundidad de operador: {metrics['operator_depth']}")
    print(f"  Número de subfórmulas: {metrics['num_subformulas']}")
    print(f"  Número de cuantificadores: {metrics['num_quantifiers']}")
    print(f"  Distribución de conectivas:")
    for conn_type, count in metrics['connective_distribution'].items():
        if count > 0:
            print(f"    {conn_type}: {count}")
    
    # Exportar análisis completo
    print("\nExportando análisis completo...")
    try:
        files = export_complete_analysis(
            ast, 
            original_formula=conditional,
            output_dir='outputs',
            base_name='ejemplo_1'
        )
        print(f"✓ JSON exportado: {files['json']}")
        if 'svg' in files:
            print(f"✓ SVG exportado: {files['svg']}")
        else:
            print("⚠ SVG no disponible (graphviz no instalado)")
    except Exception as e:
        print(f"✗ Error al exportar: {e}")
        import traceback
        traceback.print_exc()


def test_example_2():
    """Prueba el Ejemplo 2: Con XOR (⊕)."""
    print("\n" + "=" * 80)
    print("EJEMPLO 2: Con XOR (⊕)")
    print("=" * 80)
    
    premises = [
        "∀x (DrinkRegularly(x, coffee) → IsDependentOn(x, caffeine))",
        "∀x (DrinkRegularly(x, coffee) ∨ (¬WantToBeAddictedTo(x, caffeine)))",
        "∀x (¬WantToBeAddictedTo(x, caffeine) → ¬AwareThatDrug(x, caffeine))",
        "¬(Student(rina) ⊕ ¬AwareThatDrug(rina, caffeine))",
        "¬(IsDependentOn(rina, caffeine) ⊕ Student(rina))"
    ]
    conclusion = "¬WantToBeAddictedTo(rina, caffeine) ∨ (¬AwareThatDrug(rina, caffeine))"
    
    print("\nPremisas:")
    for i, prem in enumerate(premises, 1):
        print(f"  {i}. {prem}")
    print(f"\nConclusión: {conclusion}")
    
    # Construir condicional global
    conditional = build_global_conditional(premises, conclusion)
    print(f"\nCondicional global:")
    print(f"  {conditional}")
    
    # Parsear
    print("\nParseando fórmula...")
    try:
        ast = parse_global_conditional(premises, conclusion)
        print("✓ Parseo exitoso")
        print(f"\nAST (representación): {ast}")
    except Exception as e:
        print(f"✗ Error al parsear: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Calcular métricas
    print("\nCalculando métricas...")
    metrics = calculate_all_metrics(ast)
    
    print("\nMétricas calculadas:")
    print(f"  Profundidad total: {metrics['total_depth']}")
    print(f"  Profundidad de operador: {metrics['operator_depth']}")
    print(f"  Número de subfórmulas: {metrics['num_subformulas']}")
    print(f"  Número de cuantificadores: {metrics['num_quantifiers']}")
    print(f"  Distribución de conectivas:")
    for conn_type, count in metrics['connective_distribution'].items():
        if count > 0:
            print(f"    {conn_type}: {count}")
    
    # Verificar que XOR está presente
    if metrics['connective_distribution'].get('XOR', 0) > 0:
        print("\n✓ XOR detectado correctamente en la fórmula")
    else:
        print("\n⚠ Advertencia: No se detectó XOR en la distribución de conectivas")
    
    # Exportar análisis completo
    print("\nExportando análisis completo...")
    try:
        files = export_complete_analysis(
            ast, 
            original_formula=conditional,
            output_dir='outputs',
            base_name='ejemplo_2'
        )
        print(f"✓ JSON exportado: {files['json']}")
        if 'svg' in files:
            print(f"✓ SVG exportado: {files['svg']}")
        else:
            print("⚠ SVG no disponible (graphviz no instalado)")
    except Exception as e:
        print(f"✗ Error al exportar: {e}")
        import traceback
        traceback.print_exc()


def test_individual_formulas():
    """Prueba fórmulas individuales para verificar el parser."""
    print("\n" + "=" * 80)
    print("PRUEBAS ADICIONALES: Fórmulas individuales")
    print("=" * 80)
    
    parser = FOLParser()
    
    test_cases = [
        "GenusBulbophyllum(bulbophyllumAttenuatum)",
        "¬Orchid(bulbophyllumAttenuatum)",
        "∀x (GenusBulbophyllum(x) → Orchid(x))",
        "Student(rina) ⊕ ¬AwareThatDrug(rina, caffeine)",
        "¬(Student(rina) ⊕ ¬AwareThatDrug(rina, caffeine))",
    ]
    
    for formula in test_cases:
        print(f"\nFórmula: {formula}")
        try:
            ast = parser.parse(formula)
            print(f"  ✓ Parseo exitoso: {ast}")
        except Exception as e:
            print(f"  ✗ Error: {e}")


if __name__ == '__main__':
    print("Iniciando pruebas del pipeline FOL Parser")
    print("=" * 80)
    
    # Crear directorio de salida
    from pathlib import Path
    Path('outputs').mkdir(exist_ok=True)
    
    # Ejecutar pruebas
    test_example_1()
    test_example_2()
    test_individual_formulas()
    
    print("\n" + "=" * 80)
    print("Pruebas completadas")
    print("=" * 80)


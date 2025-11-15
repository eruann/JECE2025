"""
Ejemplo de uso del paquete FOL Parser.

Este archivo muestra cómo usar los módulos exportables del paquete.
"""

# Opción 1: Importar desde el paquete (si está instalado)
# from JECE2025 import (
#     FOLParser, parse_global_conditional, calculate_all_metrics, 
#     export_complete_analysis
# )

# Opción 2: Importar módulos directamente (actual)
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics
from serialize import export_complete_analysis


def ejemplo_basico():
    """Ejemplo básico de uso del parser."""
    # Crear parser
    parser = FOLParser()
    
    # Parsear una fórmula
    formula = "GenusBulbophyllum(bulbophyllumAttenuatum)"
    ast = parser.parse(formula)
    
    print(f"Fórmula: {formula}")
    print(f"AST: {ast}")
    return ast


def ejemplo_condicional_completo():
    """Ejemplo completo: condicional global con métricas."""
    # Premisas y conclusión
    premises = [
        "GenusBulbophyllum(bulbophyllumAttenuatum)",
        "∀x (GenusBulbophyllum(x) → Orchid(x))"
    ]
    conclusion = "¬Orchid(bulbophyllumAttenuatum)"
    
    # Parsear condicional global
    ast = parse_global_conditional(premises, conclusion)
    
    # Calcular métricas
    metrics = calculate_all_metrics(ast)
    
    print("Métricas calculadas:")
    print(f"  Profundidad total: {metrics['total_depth']}")
    print(f"  Profundidad de operador: {metrics['operator_depth']}")
    print(f"  Número de subfórmulas: {metrics['num_subformulas']}")
    print(f"  Número de cuantificadores: {metrics['num_quantifiers']}")
    print(f"  Distribución de conectivas: {metrics['connective_distribution']}")
    
    return ast, metrics


def ejemplo_exportacion():
    """Ejemplo de exportación a JSON y SVG."""
    premises = [
        "Student(rina) ⊕ ¬AwareThatDrug(rina, caffeine)"
    ]
    conclusion = "¬WantToBeAddictedTo(rina, caffeine)"
    
    # Parsear
    ast = parse_global_conditional(premises, conclusion)
    
    # Exportar análisis completo
    formula_str = f"({' ∧ '.join(premises)}) → {conclusion}"
    files = export_complete_analysis(
        ast,
        original_formula=formula_str,
        output_dir='outputs',
        base_name='ejemplo_export'
    )
    
    print(f"Archivos generados:")
    print(f"  JSON: {files['json']}")
    if 'svg' in files:
        print(f"  SVG: {files['svg']}")
    
    return files


if __name__ == '__main__':
    print("=" * 60)
    print("Ejemplo 1: Uso básico del parser")
    print("=" * 60)
    ejemplo_basico()
    
    print("\n" + "=" * 60)
    print("Ejemplo 2: Condicional completo con métricas")
    print("=" * 60)
    ejemplo_condicional_completo()
    
    print("\n" + "=" * 60)
    print("Ejemplo 3: Exportación")
    print("=" * 60)
    ejemplo_exportacion()


#!/usr/bin/env python3
"""
Ejemplo mínimo de cómo cargar los módulos
"""

# PASO 1: Configurar el path (SIEMPRE estas 3 líneas)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# PASO 2: Importar lo que necesites
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics

# PASO 3: Usar
if __name__ == '__main__':
    print("Cargando módulos...")
    
    # Crear parser
    parser = FOLParser()
    
    # Parsear fórmula
    formula = "GenusBulbophyllum(bulbophyllumAttenuatum)"
    ast = parser.parse(formula)
    print(f"✓ Parseado: {ast}")
    
    # Condicional global
    premises = ["P(a)", "Q(b)"]
    conclusion = "R(c)"
    ast = parse_global_conditional(premises, conclusion)
    print(f"✓ Condicional: {ast}")
    
    # Métricas
    metrics = calculate_all_metrics(ast)
    print(f"✓ Métricas calculadas: {metrics['num_subformulas']} subfórmulas")
    
    print("\n✅ Todo funcionando correctamente!")

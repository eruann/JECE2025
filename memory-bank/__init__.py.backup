"""
Paquete para análisis de fórmulas de Lógica de Primer Orden (FOL) del dataset FOLIO.

Módulos principales:
- fol_parser: Parser de fórmulas FOL con soporte para operadores y cuantificadores
- build_conditionals: Construcción de condicionales globales
- metrics: Cálculo de métricas guiadas por Gamut
- serialize: Exportación a JSON y SVG
- download_folio: Descarga del dataset FOLIO desde HuggingFace
"""

__version__ = "0.1.0"

# Exportar clases y funciones principales
from fol_parser import FOLParser, FOLASTNode, get_parser
from build_conditionals import (
    build_global_conditional,
    parse_global_conditional,
    needs_parentheses
)
from metrics import (
    calculate_total_depth,
    calculate_operator_depth,
    calculate_quantifier_scope,
    calculate_connective_scope,
    calculate_variable_binding,
    count_subformulas,
    count_quantifiers,
    count_connectives,
    calculate_all_metrics
)
from serialize import (
    ast_to_json,
    ast_to_svg,
    export_complete_analysis
)
from download_folio import download_folio_dataset

__all__ = [
    # Versión
    '__version__',
    
    # Parser
    'FOLParser',
    'FOLASTNode',
    'get_parser',
    
    # Construcción de condicionales
    'build_global_conditional',
    'parse_global_conditional',
    'needs_parentheses',
    
    # Métricas
    'calculate_total_depth',
    'calculate_operator_depth',
    'calculate_quantifier_scope',
    'calculate_connective_scope',
    'calculate_variable_binding',
    'count_subformulas',
    'count_quantifiers',
    'count_connectives',
    'calculate_all_metrics',
    
    # Serialización
    'ast_to_json',
    'ast_to_svg',
    'export_complete_analysis',
    
    # Descarga de datos
    'download_folio_dataset',
]


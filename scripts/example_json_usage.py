"""
Ejemplo de cómo usar el JSON mejorado con IDs serializables para alcance y ligadura.

Este script muestra cómo:
1. Cargar un JSON generado por el sistema
2. Encontrar nodos por ID
3. Reconstruir relaciones de alcance y ligadura
4. Usar la información estructurada
"""

import json
import sys
from pathlib import Path

# Agregar src/ al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from serialize import find_node_by_id, get_scope_and_binding_info


def example_basic_usage(json_path: str):
    """Ejemplo básico de uso del JSON."""
    print("=" * 80)
    print("Ejemplo: Uso básico del JSON con IDs serializables")
    print("=" * 80)
    
    # Cargar JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ast = data['ast']
    metrics = data['metrics']
    
    print(f"\nFórmula original: {data.get('original_formula', 'N/A')}")
    print(f"\nEstructura del JSON:")
    print(f"  - AST: {len(str(ast))} caracteres")
    print(f"  - Métricas: {list(metrics.keys())}")
    
    # Mostrar algunos IDs de ejemplo
    print(f"\nEjemplo de IDs en el AST:")
    def show_ids(node, depth=0):
        if depth > 2:  # Limitar profundidad para el ejemplo
            return
        indent = "  " * depth
        node_id = node.get('id', 'N/A')
        node_type = node.get('type', 'N/A')
        print(f"{indent}- {node_id}: {node_type}")
        if 'children' in node:
            for child in node['children'][:2]:  # Solo primeros 2 hijos
                if isinstance(child, dict):
                    show_ids(child, depth + 1)
    
    show_ids(ast)
    print("  ...")
    
    # Mostrar métricas de alcance
    print(f"\nAlcances de cuantificadores:")
    quantifier_scopes = metrics.get('quantifier_scope', {})
    for quantifier_id, scope_ids in quantifier_scopes.items():
        quantifier_node = find_node_by_id(ast, quantifier_id)
        if quantifier_node:
            quantifier_type = quantifier_node.get('type', 'N/A')
            quantifier_var = quantifier_node.get('value', 'N/A')
            print(f"  - {quantifier_id}: {quantifier_type}{quantifier_var}")
            print(f"    Alcance: {len(scope_ids)} nodo(s) -> {scope_ids}")
    
    # Mostrar ligaduras
    print(f"\nLigaduras de variables:")
    variable_bindings = metrics.get('variable_binding', {})
    for quantifier_id, bound_ids in variable_bindings.items():
        quantifier_node = find_node_by_id(ast, quantifier_id)
        if quantifier_node:
            quantifier_type = quantifier_node.get('type', 'N/A')
            quantifier_var = quantifier_node.get('value', 'N/A')
            print(f"  - {quantifier_id}: {quantifier_type}{quantifier_var}")
            print(f"    Variables ligadas: {len(bound_ids)} ocurrencia(s) -> {bound_ids}")


def example_structured_info(json_path: str):
    """Ejemplo usando la función get_scope_and_binding_info()."""
    print("\n" + "=" * 80)
    print("Ejemplo: Uso de get_scope_and_binding_info()")
    print("=" * 80)
    
    # Cargar JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Obtener información estructurada
    info = get_scope_and_binding_info(data)
    
    print(f"\nAlcances de cuantificadores ({len(info['quantifier_scopes'])}):")
    for scope_info in info['quantifier_scopes']:
        quantifier = scope_info['quantifier']
        if quantifier:
            print(f"\n  Cuantificador: {scope_info['quantifier_id']}")
            print(f"    Tipo: {quantifier.get('type', 'N/A')}")
            print(f"    Variable: {quantifier.get('value', 'N/A')}")
            print(f"    Alcance: {len(scope_info['scope_nodes'])} nodo(s)")
            print(f"    IDs del alcance: {scope_info['scope_ids']}")
            
            # Mostrar el primer nodo del alcance como ejemplo
            if scope_info['scope_nodes']:
                first_scope = scope_info['scope_nodes'][0]
                print(f"    Primer nodo del alcance: {first_scope.get('id')} ({first_scope.get('type')})")
    
    print(f"\nLigaduras de variables ({len(info['variable_bindings'])}):")
    for binding_info in info['variable_bindings']:
        quantifier = binding_info['quantifier']
        if quantifier:
            print(f"\n  Cuantificador: {binding_info['quantifier_id']}")
            print(f"    Tipo: {quantifier.get('type', 'N/A')}")
            print(f"    Variable: {quantifier.get('value', 'N/A')}")
            print(f"    Variables ligadas: {len(binding_info['bound_variables'])} ocurrencia(s)")
            print(f"    IDs ligados: {binding_info['bound_ids']}")
            
            # Mostrar las primeras variables ligadas como ejemplo
            for bound_var in binding_info['bound_variables'][:3]:
                print(f"      - {bound_var.get('id')}: {bound_var.get('type')} = {bound_var.get('value', 'N/A')}")


def example_reconstruct_tree(json_path: str):
    """Ejemplo de cómo reconstruir información del árbol desde el JSON."""
    print("\n" + "=" * 80)
    print("Ejemplo: Reconstrucción de información del árbol")
    print("=" * 80)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ast = data['ast']
    metrics = data['metrics']
    
    # Función auxiliar para obtener la fórmula representada por un nodo
    def node_to_string(node):
        """Convierte un nodo a string (simplificado)."""
        node_type = node.get('type', '')
        value = node.get('value', '')
        
        if node_type in {'FORALL', 'EXISTS'}:
            var = value if value else 'x'
            symbol = '∀' if node_type == 'FORALL' else '∃'
            children = node.get('children', [])
            if children:
                scope = node_to_string(children[0])
                return f"{symbol}{var}({scope})"
            return f"{symbol}{var}"
        
        elif node_type == 'PREDICATE':
            pred_name = value if value else 'P'
            children = node.get('children', [])
            if children:
                args = [node_to_string(c) if isinstance(c, dict) else str(c) 
                       for c in children]
                return f"{pred_name}({', '.join(args)})"
            return pred_name
        
        elif node_type in {'AND', 'OR', 'XOR', 'IMPLIES', 'BICOND'}:
            symbol_map = {
                'AND': '∧', 'OR': '∨', 'XOR': '⊕',
                'IMPLIES': '→', 'BICOND': '↔'
            }
            symbol = symbol_map.get(node_type, node_type)
            children = node.get('children', [])
            if len(children) == 2:
                return f"({node_to_string(children[0])} {symbol} {node_to_string(children[1])})"
            elif len(children) == 1:
                return node_to_string(children[0])
            return symbol
        
        elif node_type == 'NOT':
            children = node.get('children', [])
            if children:
                return f"¬{node_to_string(children[0])}"
            return '¬'
        
        elif node_type in {'TERM', 'VARIABLE', 'ATOM'}:
            return value if value else node_type
        
        return node_type
    
    # Mostrar la fórmula completa
    print(f"\nFórmula completa reconstruida:")
    formula = node_to_string(ast)
    print(f"  {formula}")
    
    # Mostrar alcances reconstruidos
    print(f"\nAlcances reconstruidos:")
    quantifier_scopes = metrics.get('quantifier_scope', {})
    for quantifier_id, scope_ids in quantifier_scopes.items():
        quantifier_node = find_node_by_id(ast, quantifier_id)
        if quantifier_node:
            quantifier_str = node_to_string(quantifier_node)
            scope_nodes = [find_node_by_id(ast, sid) for sid in scope_ids]
            scope_strs = [node_to_string(n) for n in scope_nodes if n]
            print(f"\n  {quantifier_id}: {quantifier_str}")
            print(f"    Alcance: {' ∧ '.join(scope_strs) if len(scope_strs) > 1 else scope_strs[0] if scope_strs else 'N/A'}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ejemplo de uso del JSON con IDs serializables')
    parser.add_argument('json_path', type=str, help='Ruta al archivo JSON generado')
    parser.add_argument('--structured', action='store_true', 
                       help='Mostrar ejemplo usando get_scope_and_binding_info()')
    parser.add_argument('--reconstruct', action='store_true',
                       help='Mostrar ejemplo de reconstrucción del árbol')
    
    args = parser.parse_args()
    
    if not Path(args.json_path).exists():
        print(f"Error: Archivo no encontrado: {args.json_path}")
        sys.exit(1)
    
    # Ejemplo básico siempre
    example_basic_usage(args.json_path)
    
    # Ejemplos opcionales
    if args.structured:
        example_structured_info(args.json_path)
    
    if args.reconstruct:
        example_reconstruct_tree(args.json_path)
    
    print("\n" + "=" * 80)
    print("Para más información, ver:")
    print("  - find_node_by_id(): Encuentra un nodo por ID")
    print("  - get_scope_and_binding_info(): Extrae información estructurada")
    print("=" * 80)


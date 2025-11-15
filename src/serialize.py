"""
Serialización del AST y métricas a JSON y SVG.

Permite exportar:
- AST + métricas a JSON
- Visualización del AST a SVG usando graphviz
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from graphviz import Digraph

try:
    from .fol_parser import FOLASTNode
    from .metrics import calculate_all_metrics
except ImportError:
    from fol_parser import FOLASTNode
    from metrics import calculate_all_metrics


def ast_to_json(ast: FOLASTNode, metrics: Optional[Dict[str, Any]] = None, 
                filepath: Optional[str] = None) -> Dict[str, Any]:
    """
    Serializa el AST y métricas a formato JSON.
    
    Args:
        ast: Nodo raíz del AST
        metrics: Diccionario de métricas (si es None, se calculan)
        filepath: Ruta donde guardar el JSON (opcional)
    
    Returns:
        Diccionario con AST y métricas
    """
    if metrics is None:
        metrics = calculate_all_metrics(ast)
    
    result = {
        'ast': ast.to_dict(),
        'metrics': metrics
    }
    
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"AST y métricas guardados en: {filepath}")
    
    return result


def ast_to_svg(ast: FOLASTNode, filename: str = 'ast', 
               directory: str = 'outputs', format: str = 'svg', 
               also_png: bool = False) -> Optional[str]:
    """
    Exporta el AST a formato SVG usando graphviz.
    
    Args:
        ast: Nodo raíz del AST
        filename: Nombre del archivo (sin extensión)
        directory: Directorio donde guardar el archivo
        format: Formato de salida ('svg', 'png', 'pdf')
    
    Returns:
        Ruta del archivo generado, o None si graphviz no está disponible
    """
    try:
        # Crear directorio si no existe
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Crear grafo dirigido
        dot = Digraph(comment='FOL AST', format=format)
        dot.attr(rankdir='TB')  # Top to bottom
        dot.attr('node', shape='box', style='rounded')
        
        # Contador para IDs únicos
        node_counter = {'count': 0}
        node_id_map = {}  # Mapa de objetos AST a IDs de graphviz
        
        def add_node(ast_node: FOLASTNode, parent_id: Optional[str] = None):
            """Agrega un nodo y recursivamente sus hijos."""
            # Generar ID único para este nodo
            node_id = f"node_{node_counter['count']}"
            node_counter['count'] += 1
            node_id_map[id(ast_node)] = node_id
            
            # Crear etiqueta para el nodo
            label = _create_node_label(ast_node)
            
            # Agregar nodo al grafo
            dot.node(node_id, label)
            
            # Conectar con el padre si existe
            if parent_id:
                dot.edge(parent_id, node_id)
            
            # Recursivamente agregar hijos
            for child in ast_node.children:
                add_node(child, node_id)
        
        # Construir el grafo
        add_node(ast)
        
        # Renderizar formato principal
        output_path = dot.render(filename=filename, directory=directory, cleanup=False, format=format)
        
        # Si se pidió PNG también, generar PNG adicional (no limpiar para mantenerlo)
        if also_png and format != 'png':
            try:
                png_path = dot.render(filename=filename, directory=directory, cleanup=False, format='png')
                print(f"Árbol AST exportado a PNG: {png_path}")
            except Exception as png_error:
                print(f"⚠ Advertencia: No se pudo generar PNG: {png_error}")
        
        print(f"Árbol AST exportado a: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠ Advertencia: No se pudo exportar SVG (graphviz no disponible o error): {e}")
        return None


def _create_node_label(ast_node: FOLASTNode) -> str:
    """
    Crea una etiqueta legible para un nodo del AST en el grafo.
    
    Args:
        ast_node: Nodo del AST
    
    Returns:
        String con la etiqueta
    """
    node_type = ast_node.node_type
    
    # Para operadores binarios, mostrar el símbolo
    symbol_map = {
        'AND': '∧',
        'OR': '∨',
        'XOR': '⊕',
        'IMPLIES': '→',
        'BICOND': '↔',
        'NOT': '¬',
        'FORALL': '∀',
        'EXISTS': '∃'
    }
    
    if node_type in symbol_map:
        symbol = symbol_map[node_type]
        if node_type in {'FORALL', 'EXISTS'}:
            # Mostrar variable ligada
            var_name = ast_node.value if ast_node.value else 'x'
            return f"{symbol}{var_name}"
        return symbol
    
    # Para predicados, mostrar nombre y argumentos
    if node_type == 'PREDICATE':
        pred_name = ast_node.value if ast_node.value else 'P'
        if ast_node.children:
            args = []
            for child in ast_node.children:
                if isinstance(child, FOLASTNode):
                    if child.node_type == 'TERM':
                        args.append(child.value if child.value else '?')
                    else:
                        args.append(str(child))
                else:
                    args.append(str(child))
            args_str = ', '.join(args)
            return f"{pred_name}({args_str})"
        return pred_name
    
    # Para átomos, términos y constantes
    if node_type in {'ATOM', 'TERM', 'VARIABLE', 'NAME'}:
        value = ast_node.value if ast_node.value else node_type
        return str(value)
    
    # Por defecto, mostrar el tipo
    return node_type


def export_complete_analysis(ast: FOLASTNode, 
                            original_formula: str,
                            output_dir: str = 'outputs',
                            base_name: str = 'analysis') -> Dict[str, str]:
    """
    Exporta análisis completo: JSON con AST+métricas y SVG del árbol.
    
    Args:
        ast: Nodo raíz del AST
        original_formula: Fórmula original (para incluir en JSON)
        output_dir: Directorio de salida
        base_name: Nombre base para los archivos
    
    Returns:
        Diccionario con rutas de archivos generados
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Calcular métricas
    metrics = calculate_all_metrics(ast)
    
    # Agregar fórmula original a los resultados
    result_data = {
        'original_formula': original_formula,
        'ast': ast.to_dict(),
        'metrics': metrics
    }
    
    # Guardar JSON
    json_path = Path(output_dir) / f"{base_name}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    # Exportar SVG y PNG (opcional)
    svg_path = ast_to_svg(ast, filename=base_name, directory=output_dir, format='svg', also_png=True)
    
    result = {'json': str(json_path)}
    if svg_path:
        result['svg'] = svg_path
        # Buscar PNG correspondiente (graphviz lo genera automáticamente cuando also_png=True)
        png_path = Path(output_dir) / f"{base_name}.png"
        if png_path.exists():
            result['png'] = str(png_path)
    
    return result


if __name__ == '__main__':
    # Prueba básica
    try:
        from .fol_parser import FOLParser
    except ImportError:
        from fol_parser import FOLParser
    
    parser = FOLParser()
    formula = "∀x (GenusBulbophyllum(x) → Orchid(x))"
    ast = parser.parse(formula)
    
    # Exportar JSON
    result = ast_to_json(ast, filepath='outputs/test.json')
    print(f"JSON exportado. Métricas: {result['metrics']}")
    
    # Exportar SVG
    svg_path = ast_to_svg(ast, filename='test', directory='outputs')
    print(f"SVG exportado: {svg_path}")


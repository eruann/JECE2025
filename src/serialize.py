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
    from .metrics import calculate_all_metrics, calculate_quantifier_scope, calculate_variable_binding
except ImportError:
    from fol_parser import FOLASTNode
    from metrics import calculate_all_metrics, calculate_quantifier_scope, calculate_variable_binding


def ast_to_json(ast: FOLASTNode, metrics: Optional[Dict[str, Any]] = None, 
                filepath: Optional[str] = None) -> Dict[str, Any]:
    """
    Serializa el AST y métricas a formato JSON con IDs únicos y referencias claras.
    
    El JSON resultante incluye:
    - AST con IDs únicos en cada nodo
    - Métricas con referencias a esos IDs para alcance y ligadura
    
    Args:
        ast: Nodo raíz del AST
        metrics: Diccionario de métricas (si es None, se calculan con IDs serializables)
        filepath: Ruta donde guardar el JSON (opcional)
    
    Returns:
        Diccionario con AST y métricas, donde las métricas usan IDs serializables
    """
    # Construir mapa de IDs primero al serializar el AST
    node_id_map = {}
    counter = {'count': 0}
    
    def build_id_map(node: FOLASTNode):
        """Construye el mapa de IDs recursivamente."""
        if id(node) not in node_id_map:
            node_id = f"node_{counter['count']}"
            counter['count'] += 1
            node_id_map[id(node)] = node_id
        
        for child in node.children:
            if isinstance(child, FOLASTNode):
                build_id_map(child)
    
    build_id_map(ast)
    
    # Serializar AST con IDs
    ast_dict = ast.to_dict(node_id_map, counter)
    
    # Calcular métricas usando los mismos IDs
    if metrics is None:
        metrics = calculate_all_metrics(ast, node_id_map)
    
    result = {
        'ast': ast_dict,
        'metrics': metrics
    }
    
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"AST y métricas guardados en: {filepath}")
    
    return result


def find_node_by_id(ast_dict: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
    """
    Encuentra un nodo en el AST serializado por su ID.
    
    Útil para reconstruir relaciones de alcance y ligadura desde el JSON.
    
    Args:
        ast_dict: Diccionario del AST (resultado de to_dict())
        node_id: ID del nodo a buscar (ej: "node_0", "node_5")
    
    Returns:
        Diccionario del nodo encontrado, o None si no existe
    
    Ejemplo:
        >>> json_data = json.load(open('analysis.json'))
        >>> ast = json_data['ast']
        >>> metrics = json_data['metrics']
        >>> # Encontrar el alcance de un cuantificador
        >>> quantifier_id = list(metrics['quantifier_scope'].keys())[0]
        >>> scope_ids = metrics['quantifier_scope'][quantifier_id]
        >>> quantifier_node = find_node_by_id(ast, quantifier_id)
        >>> scope_nodes = [find_node_by_id(ast, sid) for sid in scope_ids]
    """
    if ast_dict.get('id') == node_id:
        return ast_dict
    
    if 'children' in ast_dict:
        for child in ast_dict['children']:
            if isinstance(child, dict):
                result = find_node_by_id(child, node_id)
                if result is not None:
                    return result
    
    return None


def get_scope_and_binding_info(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrae información estructurada de alcance y ligadura desde el JSON.
    
    Convierte los IDs en referencias a los nodos completos para facilitar el uso.
    
    Args:
        json_data: Diccionario completo del JSON (con 'ast' y 'metrics')
    
    Returns:
        Diccionario con:
        - 'quantifier_scopes': Lista de dicts con 'quantifier', 'scope_nodes', 'quantifier_id'
        - 'variable_bindings': Lista de dicts con 'quantifier', 'bound_variables', 'quantifier_id'
    
    Ejemplo:
        >>> import json
        >>> with open('analysis.json') as f:
        ...     data = json.load(f)
        >>> info = get_scope_and_binding_info(data)
        >>> for scope_info in info['quantifier_scopes']:
        ...     print(f"Cuantificador {scope_info['quantifier_id']}: {scope_info['quantifier']['type']}")
        ...     print(f"  Alcance: {len(scope_info['scope_nodes'])} nodos")
    """
    ast = json_data['ast']
    metrics = json_data.get('metrics', {})
    
    result = {
        'quantifier_scopes': [],
        'variable_bindings': []
    }
    
    # Procesar alcances de cuantificadores
    quantifier_scopes = metrics.get('quantifier_scope', {})
    for quantifier_id, scope_ids in quantifier_scopes.items():
        quantifier_node = find_node_by_id(ast, quantifier_id)
        scope_nodes = [find_node_by_id(ast, sid) for sid in scope_ids if find_node_by_id(ast, sid) is not None]
        
        result['quantifier_scopes'].append({
            'quantifier_id': quantifier_id,
            'quantifier': quantifier_node,
            'scope_nodes': scope_nodes,
            'scope_ids': scope_ids
        })
    
    # Procesar ligaduras de variables
    variable_bindings = metrics.get('variable_binding', {})
    for quantifier_id, bound_ids in variable_bindings.items():
        quantifier_node = find_node_by_id(ast, quantifier_id)
        bound_nodes = [find_node_by_id(ast, bid) for bid in bound_ids if find_node_by_id(ast, bid) is not None]
        
        result['variable_bindings'].append({
            'quantifier_id': quantifier_id,
            'quantifier': quantifier_node,
            'bound_variables': bound_nodes,
            'bound_ids': bound_ids
        })
    
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
        # Configurar fuente que soporte Unicode (especialmente símbolos matemáticos)
        # Usar solo DejaVu Sans (mejor soporte Unicode en Linux)
        dot.attr('node', fontname='DejaVu Sans')
        dot.attr('graph', fontname='DejaVu Sans')
        dot.attr('edge', fontname='DejaVu Sans')
        
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
        output_path = dot.render(filename=filename, directory=directory, cleanup=True, format=format)
        
        # Si se pidió PNG también, generar PNG adicional (no limpiar para mantenerlo)
        if also_png and format != 'png':
            try:
                png_path = dot.render(filename=filename, directory=directory, cleanup=True, format='png')
                print(f"Árbol AST exportado a PNG: {png_path}")
            except Exception as png_error:
                print(f"⚠ Advertencia: No se pudo generar PNG: {png_error}")
        
        # Limpiar archivos temporales de graphviz (archivos sin extensión)
        import os
        dir_path = Path(directory)
        if dir_path.exists():
            for temp_file in dir_path.glob(filename):
                if temp_file.is_file() and not temp_file.suffix:
                    try:
                        temp_file.unlink()
                    except:
                        pass
        
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
        String con la etiqueta (usando HTML para mejor renderizado de Unicode)
    """
    node_type = ast_node.node_type
    
    # Para operadores binarios, mostrar el símbolo
    # Usar entidades HTML para mejor compatibilidad con graphviz
    symbol_map = {
        'AND': '∧',  # U+2227
        'OR': '∨',   # U+2228
        'XOR': '⊕',  # U+2295
        'IMPLIES': '→',  # U+2192
        'BICOND': '↔',  # U+2194
        'NOT': '¬',  # U+00AC
        'FORALL': '∀',  # U+2200
        'EXISTS': '∃'   # U+2203
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


def ast_to_svg_with_scope_binding(ast: FOLASTNode, filename: str = 'ast_scope', 
                                   directory: str = 'outputs', format: str = 'svg', 
                                   also_png: bool = False) -> Optional[str]:
    """
    Exporta el AST a formato SVG con visualización de alcance y ligadura.
    
    Marca visualmente:
    - Alcance de cada cuantificador: nodos en el alcance tienen fondo coloreado
    - Ligadura de variables: arcos punteados conectan cuantificadores con variables ligadas
    
    Args:
        ast: Nodo raíz del AST
        filename: Nombre del archivo (sin extensión)
        directory: Directorio donde guardar el archivo
        format: Formato de salida ('svg', 'png', 'pdf')
        also_png: Si True, también genera PNG
    
    Returns:
        Ruta del archivo generado, o None si graphviz no está disponible
    """
    try:
        # Crear directorio si no existe
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Calcular alcance y ligadura
        quantifier_scopes = calculate_quantifier_scope(ast)
        variable_bindings = calculate_variable_binding(ast)
        
        # Crear grafo dirigido
        dot = Digraph(comment='FOL AST with Scope and Binding', format=format)
        dot.attr(rankdir='TB')  # Top to bottom
        dot.attr('node', shape='box', style='rounded')
        dot.attr('node', fontname='DejaVu Sans')
        dot.attr('graph', fontname='DejaVu Sans')
        dot.attr('edge', fontname='DejaVu Sans')
        
        # Contador para IDs únicos
        node_counter = {'count': 0}
        node_id_map = {}  # Mapa de objetos AST a IDs de graphviz
        
        # Colores para diferentes cuantificadores (cada uno tiene un color único)
        quantifier_colors = [
            '#E3F2FD',  # Azul claro
            '#F3E5F5',  # Púrpura claro
            '#E8F5E9',  # Verde claro
            '#FFF3E0',  # Naranja claro
            '#FCE4EC',  # Rosa claro
            '#E0F2F1',  # Turquesa claro
        ]
        quantifier_color_map = {}  # Mapa de cuantificador a color
        
        # Asignar colores a cuantificadores
        for idx, quantifier in enumerate(quantifier_scopes.keys()):
            quantifier_color_map[id(quantifier)] = quantifier_colors[idx % len(quantifier_colors)]
        
        # Construir conjunto de nodos en alcance para cada cuantificador
        scope_nodes = {}  # id(nodo) -> lista de ids de cuantificadores cuyo alcance incluye este nodo
        def mark_scope_nodes(node: FOLASTNode, quantifier_id: int):
            """Marca recursivamente todos los nodos en el alcance de un cuantificador."""
            node_id_obj = id(node)
            if node_id_obj not in scope_nodes:
                scope_nodes[node_id_obj] = []
            if quantifier_id not in scope_nodes[node_id_obj]:
                scope_nodes[node_id_obj].append(quantifier_id)
            for child in node.children:
                mark_scope_nodes(child, quantifier_id)
        
        for quantifier, scope_list in quantifier_scopes.items():
            quantifier_id = id(quantifier)
            for scope_node in scope_list:
                # Marcar recursivamente todos los nodos en el alcance (pero no el cuantificador mismo)
                mark_scope_nodes(scope_node, quantifier_id)
        
        def add_node(ast_node: FOLASTNode, parent_id: Optional[str] = None):
            """Agrega un nodo y recursivamente sus hijos."""
            # Generar ID único para este nodo
            node_id = f"node_{node_counter['count']}"
            node_counter['count'] += 1
            node_id_map[id(ast_node)] = node_id
            
            # Crear etiqueta para el nodo
            label = _create_node_label(ast_node)
            
            # Determinar color de fondo según alcance
            node_id_obj = id(ast_node)
            node_attrs = {}
            
            # Si este nodo está en el alcance de algún cuantificador, colorearlo
            if node_id_obj in scope_nodes:
                quantifier_ids = scope_nodes[node_id_obj]
                if quantifier_ids:
                    # Usar el color del primer cuantificador (si hay múltiples, usar el más externo)
                    # En caso de múltiples alcances anidados, usar gradiente o color mixto
                    if len(quantifier_ids) == 1:
                        color = quantifier_color_map[quantifier_ids[0]]
                        node_attrs['fillcolor'] = color
                        node_attrs['style'] = 'rounded,filled'
                    else:
                        # Múltiples alcances: usar color del más externo o color mixto
                        color = quantifier_color_map[quantifier_ids[-1]]  # Último = más externo
                        node_attrs['fillcolor'] = color
                        node_attrs['style'] = 'rounded,filled'
            
            # Si es un cuantificador, marcar con borde más grueso y color más oscuro
            # (pero NO colorear el fondo con el color del alcance - el cuantificador no está en su propio alcance)
            if ast_node.node_type in {'FORALL', 'EXISTS'}:
                quantifier_id = id(ast_node)
                if quantifier_id in quantifier_color_map:
                    # Crear versión más oscura del color para el borde
                    base_color = quantifier_color_map[quantifier_id]
                    # Convertir hex a RGB, oscurecer, volver a hex
                    hex_color = base_color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    darker_rgb = tuple(max(0, c - 60) for c in rgb)  # Oscurecer cada componente
                    darker_hex = '#{:02x}{:02x}{:02x}'.format(*darker_rgb)
                    
                    node_attrs['color'] = darker_hex
                    node_attrs['penwidth'] = '2.5'
                    # El cuantificador tiene fondo blanco o muy claro, no el color de su alcance
                    if 'style' not in node_attrs:
                        node_attrs['style'] = 'rounded,filled'
                    # Sobrescribir cualquier color de fondo que pueda haber sido asignado por el alcance
                    node_attrs['fillcolor'] = '#FFFFFF'  # Fondo blanco para el cuantificador
                    node_attrs['color'] = darker_hex  # Borde oscuro del color del alcance
            
            # Agregar nodo al grafo con atributos
            dot.node(node_id, label, **node_attrs)
            
            # Conectar con el padre si existe (arco normal del árbol)
            if parent_id:
                dot.edge(parent_id, node_id)
            
            # Recursivamente agregar hijos
            for child in ast_node.children:
                add_node(child, node_id)
        
        # Construir el grafo
        add_node(ast)
        
        # Agregar arcos de ligadura (conectar cuantificadores con variables ligadas)
        for quantifier, bound_occurrences in variable_bindings.items():
            quantifier_id = id(quantifier)
            quantifier_node_id = node_id_map.get(quantifier_id)
            
            if quantifier_node_id:
                for bound_node in bound_occurrences:
                    bound_node_id = id(bound_node)
                    bound_node_gviz_id = node_id_map.get(bound_node_id)
                    
                    if bound_node_gviz_id:
                        # Crear arco punteado con color del cuantificador (más oscuro)
                        base_color = quantifier_color_map.get(quantifier_id, '#888888')
                        # Convertir hex a RGB, oscurecer, volver a hex
                        hex_color = base_color.lstrip('#')
                        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                        darker_rgb = tuple(max(0, c - 80) for c in rgb)  # Oscurecer más para el arco
                        edge_color = '#{:02x}{:02x}{:02x}'.format(*darker_rgb)
                        
                        dot.edge(
                            quantifier_node_id, 
                            bound_node_gviz_id,
                            style='dashed',
                            color=edge_color,
                            penwidth='2',
                            constraint='false',  # No afectar el layout del árbol principal
                            label=''  # Sin etiqueta, solo visual
                        )
        
        # Renderizar formato principal
        output_path = dot.render(filename=filename, directory=directory, cleanup=True, format=format)
        
        # Si se pidió PNG también, generar PNG adicional
        if also_png and format != 'png':
            try:
                png_path = dot.render(filename=filename, directory=directory, cleanup=True, format='png')
                print(f"Árbol AST con alcance y ligadura exportado a PNG: {png_path}")
            except Exception as png_error:
                print(f"⚠ Advertencia: No se pudo generar PNG: {png_error}")
        
        # Limpiar archivos temporales de graphviz
        import os
        dir_path = Path(directory)
        if dir_path.exists():
            for temp_file in dir_path.glob(filename):
                if temp_file.is_file() and not temp_file.suffix:
                    try:
                        temp_file.unlink()
                    except:
                        pass
        
        print(f"Árbol AST con alcance y ligadura exportado a: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠ Advertencia: No se pudo exportar SVG con alcance/ligadura (graphviz no disponible o error): {e}")
        import traceback
        traceback.print_exc()
        return None


def export_complete_analysis(ast: FOLASTNode, 
                            original_formula: str,
                            output_dir: str = 'outputs',
                            base_name: str = 'analysis',
                            include_scope_binding: bool = True) -> Dict[str, str]:
    """
    Exporta análisis completo: JSON con AST+métricas y SVG del árbol.
    
    Args:
        ast: Nodo raíz del AST
        original_formula: Fórmula original (para incluir en JSON)
        output_dir: Directorio de salida
        base_name: Nombre base para los archivos
        include_scope_binding: Si True, también genera SVG con visualización de alcance y ligadura
    
    Returns:
        Diccionario con rutas de archivos generados
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Usar ast_to_json para generar JSON con IDs serializables y métricas correctas
    json_path = Path(output_dir) / f"{base_name}.json"
    result_data = ast_to_json(ast, filepath=str(json_path))
    
    # Agregar fórmula original a los resultados
    result_data['original_formula'] = original_formula
    
    # Exportar SVG básico y PNG
    svg_path = ast_to_svg(ast, filename=base_name, directory=output_dir, format='svg', also_png=True)
    
    result = {'json': str(json_path)}
    if svg_path:
        result['svg'] = svg_path
        # Buscar PNG correspondiente
        png_path = Path(output_dir) / f"{base_name}.png"
        if png_path.exists():
            result['png'] = str(png_path)
    
    # Exportar SVG con alcance y ligadura si se solicita
    if include_scope_binding:
        svg_scope_path = ast_to_svg_with_scope_binding(
            ast, 
            filename=f"{base_name}_scope", 
            directory=output_dir, 
            format='svg', 
            also_png=True
        )
        if svg_scope_path:
            result['svg_scope'] = svg_scope_path
            # Buscar PNG correspondiente
            png_scope_path = Path(output_dir) / f"{base_name}_scope.png"
            if png_scope_path.exists():
                result['png_scope'] = str(png_scope_path)
    
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


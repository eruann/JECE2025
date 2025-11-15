"""
Cálculo de métricas guiadas por Gamut para fórmulas FOL.

Métricas implementadas:
- Profundidad total (altura del árbol)
- Profundidad de operador (máx. niveles de conectivas/cuántificadores hasta cada átomo)
- Alcance (scope) de cada cuantificador y conectiva
- Ligadura de variables (mapa cuantificador → ocurrencias ligadas)
- Conteos: #subfórmulas, #cuantificadores, distribución de conectivas (incl. ⊕)
"""

from typing import Dict, List, Set, Tuple, Any
from fol_parser import FOLASTNode


def calculate_total_depth(ast: FOLASTNode) -> int:
    """
    Calcula la profundidad total (altura) del árbol AST.
    
    Args:
        ast: Nodo raíz del AST
    
    Returns:
        Profundidad máxima del árbol (1 para un átomo)
    """
    if not ast.children:
        return 1
    
    if len(ast.children) == 0:
        return 1
    
    return 1 + max(calculate_total_depth(child) for child in ast.children)


def calculate_operator_depth(ast: FOLASTNode, current_depth: int = 0) -> int:
    """
    Calcula la profundidad máxima de operadores (conectivas/cuántificadores) 
    hasta cada átomo.
    
    Args:
        ast: Nodo del AST
        current_depth: Profundidad actual (para recursión)
    
    Returns:
        Profundidad máxima de operadores
    """
    # Tipos que son operadores (conectivas o cuantificadores)
    operator_types = {
        'AND', 'OR', 'XOR', 'IMPLIES', 'BICOND', 'NOT', 
        'FORALL', 'EXISTS'
    }
    
    # Si es un operador, incrementamos la profundidad
    if ast.node_type in operator_types:
        current_depth += 1
    
    # Si es un átomo o término, retornamos la profundidad actual
    if ast.node_type in {'ATOM', 'TERM', 'PREDICATE', 'NAME'}:
        return current_depth
    
    # Si tiene hijos, calculamos la profundidad máxima de ellos
    if ast.children:
        return max(calculate_operator_depth(child, current_depth) 
                  for child in ast.children)
    
    return current_depth


def calculate_quantifier_scope(ast: FOLASTNode, 
                                parent_scope: List[FOLASTNode] = None) -> Dict[FOLASTNode, List[FOLASTNode]]:
    """
    Calcula el alcance (scope) de cada cuantificador en el AST.
    
    El scope de un cuantificador es la subfórmula sobre la cual actúa.
    
    Args:
        ast: Nodo raíz del AST
        parent_scope: Lista de cuantificadores padre (para recursión)
    
    Returns:
        Diccionario que mapea cada nodo cuantificador a su scope (lista de nodos)
    """
    if parent_scope is None:
        parent_scope = []
    
    scopes = {}
    
    if ast.node_type in {'FORALL', 'EXISTS'}:
        # Este es un cuantificador
        # Su scope es el hijo (la fórmula cuantificada)
        if ast.children:
            scope_formula = ast.children[0]
            scopes[ast] = [scope_formula]
            
            # Recursivamente calcular scopes dentro del scope de este cuantificador
            new_parent_scope = parent_scope + [ast]
            sub_scopes = calculate_quantifier_scope(scope_formula, new_parent_scope)
            scopes.update(sub_scopes)
    else:
        # No es cuantificador, pero puede contener cuantificadores en sus hijos
        for child in ast.children:
            sub_scopes = calculate_quantifier_scope(child, parent_scope)
            scopes.update(sub_scopes)
    
    return scopes


def calculate_connective_scope(ast: FOLASTNode) -> Dict[FOLASTNode, List[FOLASTNode]]:
    """
    Calcula el alcance (scope) de cada conectiva en el AST.
    
    El scope de una conectiva son sus operandos (hijos).
    
    Args:
        ast: Nodo raíz del AST
    
    Returns:
        Diccionario que mapea cada conectiva a su scope (lista de operandos)
    """
    scopes = {}
    
    connective_types = {'AND', 'OR', 'XOR', 'IMPLIES', 'BICOND', 'NOT'}
    
    if ast.node_type in connective_types:
        # Esta conectiva tiene como scope sus hijos (operandos)
        scopes[ast] = ast.children.copy()
    
    # Recursivamente calcular scopes de conectivas en los hijos
    for child in ast.children:
        sub_scopes = calculate_connective_scope(child)
        scopes.update(sub_scopes)
    
    return scopes


def calculate_variable_binding(ast: FOLASTNode, 
                               bound_vars: Dict[str, FOLASTNode] = None,
                               bindings: Dict[FOLASTNode, List[FOLASTNode]] = None) -> Dict[FOLASTNode, List[FOLASTNode]]:
    """
    Calcula la ligadura de variables: mapa de cada cuantificador a las 
    ocurrencias de variables que liga.
    
    Args:
        ast: Nodo del AST
        bound_vars: Diccionario variable -> cuantificador que la liga
        bindings: Diccionario acumulativo de ligaduras (para recursión)
    
    Returns:
        Diccionario que mapea cada cuantificador a lista de nodos que representan
        ocurrencias ligadas de su variable
    """
    if bound_vars is None:
        bound_vars = {}
    if bindings is None:
        bindings = {}
    
    if ast.node_type in {'FORALL', 'EXISTS'}:
        # Este es un cuantificador que liga una variable
        var_name = ast.value  # Nombre de la variable ligada
        
        # Crear entrada en bindings si no existe
        if ast not in bindings:
            bindings[ast] = []
        
        # Agregar esta variable al conjunto de variables ligadas
        new_bound_vars = bound_vars.copy()
        new_bound_vars[var_name] = ast
        
        # Recursivamente buscar ocurrencias de esta variable en el scope
        if ast.children:
            scope_formula = ast.children[0]
            _find_bound_occurrences(scope_formula, var_name, ast, bindings, new_bound_vars)
    
    # Recursivamente procesar hijos
    for child in ast.children:
        calculate_variable_binding(child, bound_vars, bindings)
    
    return bindings


def _find_bound_occurrences(node: FOLASTNode, 
                           var_name: str, 
                           quantifier: FOLASTNode,
                           bindings: Dict[FOLASTNode, List[FOLASTNode]],
                           bound_vars: Dict[str, FOLASTNode]):
    """Función auxiliar para encontrar ocurrencias ligadas de una variable."""
    
    # Si es un término o átomo con el nombre de la variable
    if node.node_type in {'TERM', 'ATOM', 'VARIABLE'}:
        if node.value == var_name:
            # Esta es una ocurrencia ligada
            if quantifier not in bindings:
                bindings[quantifier] = []
            bindings[quantifier].append(node)
    
    # Si es un predicado, revisar sus argumentos (términos)
    if node.node_type == 'PREDICATE':
        for child in node.children:
            if isinstance(child, FOLASTNode) and child.node_type == 'TERM':
                if child.value == var_name:
                    if quantifier not in bindings:
                        bindings[quantifier] = []
                    bindings[quantifier].append(child)
    
    # Recursivamente buscar en hijos
    for child in node.children:
        # No buscar dentro de otros cuantificadores que liguen la misma variable
        # (shadowing)
        if isinstance(child, FOLASTNode):
            if child.node_type in {'FORALL', 'EXISTS'}:
                # Si este cuantificador liga la misma variable, no buscar más profundo
                if child.value == var_name:
                    continue
            _find_bound_occurrences(child, var_name, quantifier, bindings, bound_vars)


def count_subformulas(ast: FOLASTNode) -> int:
    """
    Cuenta el número total de subfórmulas en el AST.
    
    Cada nodo que representa una fórmula (no solo términos/átomos) cuenta como subfórmula.
    
    Args:
        ast: Nodo raíz del AST
    
    Returns:
        Número de subfórmulas
    """
    # Tipos que representan subfórmulas (no solo términos)
    formula_types = {
        'AND', 'OR', 'XOR', 'IMPLIES', 'BICOND', 'NOT',
        'FORALL', 'EXISTS', 'PREDICATE', 'ATOM'
    }
    
    count = 0
    if ast.node_type in formula_types:
        count = 1
    
    # Sumar subfórmulas de los hijos
    for child in ast.children:
        count += count_subformulas(child)
    
    return count


def count_quantifiers(ast: FOLASTNode) -> int:
    """
    Cuenta el número total de cuantificadores en el AST.
    
    Args:
        ast: Nodo raíz del AST
    
    Returns:
        Número de cuantificadores (∀ y ∃)
    """
    count = 0
    if ast.node_type in {'FORALL', 'EXISTS'}:
        count = 1
    
    for child in ast.children:
        count += count_quantifiers(child)
    
    return count


def count_connectives(ast: FOLASTNode) -> Dict[str, int]:
    """
    Cuenta la distribución de conectivas en el AST.
    
    Args:
        ast: Nodo raíz del AST
    
    Returns:
        Diccionario con conteos de cada tipo de conectiva:
        {'AND': n, 'OR': m, 'XOR': k, 'IMPLIES': l, 'BICOND': p, 'NOT': q}
    """
    distribution = {
        'AND': 0,
        'OR': 0,
        'XOR': 0,
        'IMPLIES': 0,
        'BICOND': 0,
        'NOT': 0
    }
    
    if ast.node_type in distribution:
        distribution[ast.node_type] += 1
    
    # Recursivamente contar en hijos
    for child in ast.children:
        child_dist = count_connectives(child)
        for conn_type, count in child_dist.items():
            distribution[conn_type] += count
    
    return distribution


def calculate_all_metrics(ast: FOLASTNode) -> Dict[str, Any]:
    """
    Calcula todas las métricas y las retorna en un diccionario.
    
    Args:
        ast: Nodo raíz del AST
    
    Returns:
        Diccionario con todas las métricas calculadas
    """
    metrics = {
        'total_depth': calculate_total_depth(ast),
        'operator_depth': calculate_operator_depth(ast),
        'quantifier_scope': {
            # Convertir nodos a IDs para serialización
            id(q): [id(n) for n in scope] 
            for q, scope in calculate_quantifier_scope(ast).items()
        },
        'connective_scope': {
            id(c): [id(n) for n in scope]
            for c, scope in calculate_connective_scope(ast).items()
        },
        'variable_binding': {
            id(q): [id(n) for n in occurrences]
            for q, occurrences in calculate_variable_binding(ast).items()
        },
        'num_subformulas': count_subformulas(ast),
        'num_quantifiers': count_quantifiers(ast),
        'connective_distribution': count_connectives(ast)
    }
    
    return metrics


if __name__ == '__main__':
    # Prueba básica
    from fol_parser import FOLParser
    
    parser = FOLParser()
    formula = "∀x (GenusBulbophyllum(x) → Orchid(x))"
    ast = parser.parse(formula)
    
    print(f"Fórmula: {formula}")
    print(f"Profundidad total: {calculate_total_depth(ast)}")
    print(f"Profundidad de operador: {calculate_operator_depth(ast)}")
    print(f"Número de subfórmulas: {count_subformulas(ast)}")
    print(f"Número de cuantificadores: {count_quantifiers(ast)}")
    print(f"Distribución de conectivas: {count_connectives(ast)}")
    
    bindings = calculate_variable_binding(ast)
    print(f"Ligaduras de variables: {len(bindings)} cuantificadores")


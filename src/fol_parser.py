"""
Parser de Fórmulas de Lógica de Primer Orden (FOL) usando Lark.

Soporta operadores: ∧, ∨, →, ↔, ¬, ⊕ (XOR)
Soporta cuantificadores: ∀, ∃
Preserva nombres exactos de predicados y constantes.
"""

from lark import Lark, Transformer, Tree
from typing import Any, Dict, List, Tuple, Union


# Gramática Lark para FOL completa
FOL_GRAMMAR = """
?start: formula

?formula: biconditional

?biconditional: implication ("↔" implication)* -> bicond

?implication: disjunction ("→" disjunction)* -> implies

?disjunction: conjunction ("∨" conjunction)* -> or

?conjunction: xor_expr ("∧" xor_expr)* -> and

?xor_expr: negation ("⊕" negation)* -> xor

?negation: "¬" negation -> not
         | quantified

?quantified: "∀" variable "(" formula ")" -> forall
           | "∃" variable "(" formula ")" -> exists
           | atom

?atom: predicate
     | equality
     | "(" formula ")"

predicate: NAME "(" term_list? ")" -> predicate
         | NAME -> constant_or_var

equality: term "=" term -> equals

term_list: term ("," term)* -> term_list

term: NAME -> term

variable: NAME -> variable

NAME: /[a-zA-Z_][a-zA-Z0-9_]*/

%import common.WS
%ignore WS
"""


class FOLASTNode:
    """Nodo del AST para fórmulas FOL."""
    
    def __init__(self, node_type: str, value: Any = None, children: List = None):
        self.node_type = node_type
        self.value = value
        self.children = children if children is not None else []
    
    def __repr__(self):
        if self.value is not None:
            return f"{self.node_type}({self.value})"
        if self.children:
            return f"{self.node_type}({', '.join(map(str, self.children))})"
        return self.node_type
    
    def to_dict(self):
        """Convierte el nodo a diccionario para serialización."""
        result = {"type": self.node_type}
        if self.value is not None:
            result["value"] = self.value
        if self.children:
            result["children"] = [child.to_dict() if isinstance(child, FOLASTNode) else child 
                                 for child in self.children]
        return result


class FOLTransformer(Transformer):
    """Transformer que convierte el árbol Lark a AST estructurado."""
    
    def __init__(self):
        super().__init__()
        self.visit_tokens = True
    
    def _default(self, data, children, meta):
        """Maneja cualquier nodo que no tenga un método específico."""
        # Si tiene un solo hijo, retornarlo directamente
        if len(children) == 1:
            return children[0]
        # Si tiene múltiples hijos, retornar el primero (para casos de opcionales)
        if children:
            return children[0]
        return None
    
    def _ensure_fol_node(self, arg):
        """Asegura que el argumento sea un FOLASTNode."""
        from lark import Tree
        if isinstance(arg, Tree):
            # Operadores lógicos importantes que NO deben ser desenrollados
            logical_operators = ('or', 'and', 'xor', 'implies', 'bicond', 'not', 'forall', 'exists', 'equals')
            
            # Si es un operador lógico, transformarlo correctamente
            if arg.data in logical_operators:
                # Para operadores binarios con un solo hijo (de repeticiones vacías), 
                # retornar el hijo directamente sin crear el nodo wrapper
                if arg.data in ('or', 'and', 'xor', 'implies', 'bicond') and len(arg.children) == 1:
                    return self._ensure_fol_node(arg.children[0])
                elif arg.data == 'not' and len(arg.children) == 1:
                    return FOLASTNode("NOT", children=[self._ensure_fol_node(arg.children[0])])
                elif arg.data in ('forall', 'exists') and len(arg.children) >= 2:
                    var_node = self._ensure_fol_node(arg.children[0])
                    var_name = var_node.value if isinstance(var_node, FOLASTNode) and var_node.value else str(var_node)
                    formula = self._ensure_fol_node(arg.children[1])
                    node_type = arg.data.upper()
                    return FOLASTNode(node_type, value=var_name, children=[formula])
                elif arg.data in ('or', 'and', 'xor', 'implies', 'bicond') and len(arg.children) >= 2:
                    left = self._ensure_fol_node(arg.children[0])
                    right = self._ensure_fol_node(arg.children[1])
                    node_type = arg.data.upper()
                    if node_type == 'OR':
                        return FOLASTNode("OR", children=[left, right])
                    elif node_type == 'AND':
                        return FOLASTNode("AND", children=[left, right])
                    elif node_type == 'XOR':
                        return FOLASTNode("XOR", children=[left, right])
                    elif node_type == 'IMPLIES':
                        return FOLASTNode("IMPLIES", children=[left, right])
                    elif node_type == 'BICOND':
                        return FOLASTNode("BICOND", children=[left, right])
            
            # Para otros nodos, si tienen un solo hijo y NO es un operador lógico,
            # retornar ese hijo (evitar wrappings innecesarios de nodos intermedios de la gramática)
            if len(arg.children) == 1 and arg.data not in logical_operators:
                return self._ensure_fol_node(arg.children[0])
            
            # Para otros casos, transformar recursivamente los hijos
            if arg.children:
                transformed_children = [self._ensure_fol_node(child) for child in arg.children]
                return FOLASTNode(arg.data.upper(), children=transformed_children)
            # Si no tiene hijos, crear un nodo simple
            return FOLASTNode(arg.data.upper())
        return arg
    
    def formula(self, args):
        return args[0]
    
    def bicond(self, args):
        # Asociatividad izquierda para ↔
        # Lark puede pasar la repetición como lista anidada, así que aplanamos
        flat_args = []
        for arg in args:
            if isinstance(arg, list):
                flat_args.extend(arg)
            else:
                flat_args.append(arg)
        args = [self._ensure_fol_node(arg) for arg in flat_args]
        if len(args) == 1:
            return args[0]  # Si solo hay un elemento, retornarlo directamente
        result = args[0]
        for i in range(1, len(args)):
            result = FOLASTNode("BICOND", children=[result, args[i]])
        return result
    
    def implies(self, args):
        # Asociatividad izquierda para →
        # Lark puede pasar la repetición como lista anidada, así que aplanamos
        flat_args = []
        for arg in args:
            if isinstance(arg, list):
                flat_args.extend(arg)
            else:
                flat_args.append(arg)
        args = [self._ensure_fol_node(arg) for arg in flat_args]
        if len(args) == 1:
            return args[0]  # Si solo hay un elemento, retornarlo directamente
        result = args[0]
        for i in range(1, len(args)):
            result = FOLASTNode("IMPLIES", children=[result, args[i]])
        return result
    
    def or_(self, args):
        # Asociatividad izquierda para ∨
        # Lark puede pasar la repetición como lista anidada, así que aplanamos
        flat_args = []
        for arg in args:
            if isinstance(arg, list):
                flat_args.extend(arg)
            else:
                flat_args.append(arg)
        args = [self._ensure_fol_node(arg) for arg in flat_args]
        if len(args) == 1:
            return args[0]  # Si solo hay un elemento, retornarlo directamente
        result = args[0]
        for i in range(1, len(args)):
            result = FOLASTNode("OR", children=[result, args[i]])
        return result
    
    def and_(self, args):
        # Asociatividad izquierda para ∧
        # Lark puede pasar la repetición como lista anidada, así que aplanamos
        flat_args = []
        for arg in args:
            # Si es una lista (de la repetición *), aplanarla
            if isinstance(arg, list):
                flat_args.extend(arg)
            else:
                flat_args.append(arg)
        args = [self._ensure_fol_node(arg) for arg in flat_args]
        if len(args) == 1:
            return args[0]  # Si solo hay un elemento, retornarlo directamente
        result = args[0]
        for i in range(1, len(args)):
            result = FOLASTNode("AND", children=[result, args[i]])
        return result
    
    def xor(self, args):
        # Asociatividad izquierda para ⊕
        # Lark puede pasar la repetición como lista anidada, así que aplanamos
        flat_args = []
        for arg in args:
            if isinstance(arg, list):
                flat_args.extend(arg)
            else:
                flat_args.append(arg)
        args = [self._ensure_fol_node(arg) for arg in flat_args]
        if len(args) == 1:
            return args[0]  # Si solo hay un elemento, retornarlo directamente
        result = args[0]
        for i in range(1, len(args)):
            result = FOLASTNode("XOR", children=[result, args[i]])
        return result
    
    def not_(self, args):
        return FOLASTNode("NOT", children=[self._ensure_fol_node(args[0])])
    
    def forall(self, args):
        # args[0] es la variable, args[1] es la fórmula
        var_node = self._ensure_fol_node(args[0])
        var_name = var_node.value if isinstance(var_node, FOLASTNode) and var_node.value else str(var_node)
        formula = self._ensure_fol_node(args[1])
        return FOLASTNode("FORALL", value=var_name, children=[formula])
    
    def exists(self, args):
        # args[0] es la variable, args[1] es la fórmula
        var_node = self._ensure_fol_node(args[0])
        var_name = var_node.value if isinstance(var_node, FOLASTNode) and var_node.value else str(var_node)
        formula = self._ensure_fol_node(args[1])
        return FOLASTNode("EXISTS", value=var_name, children=[formula])
    
    def predicate(self, args):
        pred_name = args[0].value if isinstance(args[0], FOLASTNode) else str(args[0])
        if len(args) > 1 and isinstance(args[1], FOLASTNode) and args[1].node_type == "TERM_LIST":
            # Hay términos
            terms = args[1].children
            return FOLASTNode("PREDICATE", value=pred_name, children=terms)
        else:
            # Predicado sin argumentos (constante o variable)
            return FOLASTNode("ATOM", value=pred_name)
    
    def constant_or_var(self, args):
        name = args[0].value if isinstance(args[0], FOLASTNode) else str(args[0])
        return FOLASTNode("ATOM", value=name)
    
    def term_list(self, args):
        # Agrupa los términos en una lista
        return FOLASTNode("TERM_LIST", children=args)
    
    def term(self, args):
        term_name = args[0].value if isinstance(args[0], FOLASTNode) else str(args[0])
        return FOLASTNode("TERM", value=term_name)
    
    def variable(self, args):
        var_name = args[0].value if isinstance(args[0], FOLASTNode) else str(args[0])
        return FOLASTNode("VARIABLE", value=var_name)
    
    def equals(self, args):
        """Maneja igualdad entre términos: t1 = t2 (fórmula atómica de identidad)"""
        # args debería ser [term1, term2]
        left = self._ensure_fol_node(args[0])
        right = self._ensure_fol_node(args[1])
        return FOLASTNode("EQUALS", children=[left, right])
    
    def NAME(self, token):
        # Preserva el nombre exacto del token
        return FOLASTNode("NAME", value=token.value)


class FOLParser:
    """Parser principal para fórmulas FOL."""
    
    def __init__(self):
        self.parser = Lark(FOL_GRAMMAR, start='formula', parser='lalr', transformer=FOLTransformer())
    
    def parse(self, formula: str) -> FOLASTNode:
        """
        Parsea una fórmula FOL y retorna el AST.
        
        Args:
            formula: String con la fórmula FOL
        
        Returns:
            FOLASTNode: Raíz del AST
        """
        try:
            tree = self.parser.parse(formula)
            return tree
        except Exception as e:
            raise ValueError(f"Error al parsear la fórmula '{formula}': {e}")
    
    def parse_file(self, filepath: str) -> FOLASTNode:
        """Parsea una fórmula desde un archivo."""
        with open(filepath, 'r', encoding='utf-8') as f:
            formula = f.read().strip()
        return self.parse(formula)


# Instancia global del parser
_parser_instance = None

def get_parser() -> FOLParser:
    """Obtiene una instancia singleton del parser."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = FOLParser()
    return _parser_instance


if __name__ == '__main__':
    # Prueba básica del parser
    parser = FOLParser()
    
    # Ejemplo simple
    test_formula = "GenusBulbophyllum(bulbophyllumAttenuatum)"
    print(f"Parseando: {test_formula}")
    ast = parser.parse(test_formula)
    print(f"AST: {ast}")
    print(f"AST (dict): {ast.to_dict()}")
    
    # Ejemplo con cuantificador
    test_formula2 = "∀x (GenusBulbophyllum(x) → Orchid(x))"
    print(f"\nParseando: {test_formula2}")
    ast2 = parser.parse(test_formula2)
    print(f"AST: {ast2}")
    print(f"AST (dict): {ast2.to_dict()}")


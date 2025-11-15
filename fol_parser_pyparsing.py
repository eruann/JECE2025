"""
Parser de Fórmulas de Lógica de Primer Orden (FOL) usando pyparsing.

Soporta operadores: ∧, ∨, →, ↔, ¬, ⊕ (XOR)
Soporta cuantificadores: ∀, ∃
Preserva nombres exactos de predicados y constantes.

pyparsing es más flexible que Lark para manejar repeticiones y estructuras recursivas.
"""

from pyparsing import (
    Word, alphas, alphanums, oneOf, Forward, Group, 
    Optional, ZeroOrMore, OneOrMore, Suppress, 
    delimitedList, ParseException, ParserElement
)
from typing import Any, List
from fol_parser import FOLASTNode  # Reutilizamos la clase AST


class FOLParserPyparsing:
    """Parser FOL usando pyparsing."""
    
    def __init__(self):
        # Configurar para preservar nombres exactos
        ParserElement.setDefaultWhitespaceChars(' \t')
        
        # Identificadores (nombres de predicados, constantes, variables)
        identifier = Word(alphas + '_', alphanums + '_')
        
        # Términos (constantes o variables)
        term = identifier.copy()
        
        # Lista de términos
        term_list = delimitedList(term, ',')
        
        # Predicados
        predicate = Group(
            identifier('pred_name') + 
            Optional(Suppress('(') + term_list('terms') + Suppress(')'))
        )
        
        # Variable para cuantificadores
        variable = identifier.copy()
        
        # Fórmula (definición recursiva)
        formula = Forward()
        
        # Átomos
        atom = predicate | Group(Suppress('(') + formula + Suppress(')'))
        
        # Negación
        negation = Forward()
        negation <<= (
            (Suppress('¬') + negation)('not') |
            atom
        )
        
        # Cuantificadores
        quantified = (
            (Suppress('∀') + variable('var') + Suppress('(') + formula('scope') + Suppress(')'))('forall') |
            (Suppress('∃') + variable('var') + Suppress('(') + formula('scope') + Suppress(')'))('exists') |
            negation
        )
        
        # XOR (más baja precedencia entre binarios)
        xor_expr = Forward()
        xor_expr <<= quantified + ZeroOrMore(Suppress('⊕') + quantified)('xor')
        
        # Conjunción
        conjunction = xor_expr + ZeroOrMore(Suppress('∧') + xor_expr)('and')
        
        # Disyunción
        disjunction = conjunction + ZeroOrMore(Suppress('∨') + conjunction)('or')
        
        # Implicación
        implication = disjunction + ZeroOrMore(Suppress('→') + disjunction)('implies')
        
        # Bicondicional
        biconditional = implication + ZeroOrMore(Suppress('↔') + implication)('bicond')
        
        formula <<= biconditional
        
        self.parser = formula
        self.identifier = identifier
        self.term = term
        self.predicate = predicate
    
    def _transform_result(self, result, parent=None):
        """Transforma el resultado de pyparsing a FOLASTNode."""
        # Si es string, es un átomo simple
        if isinstance(result, str):
            return FOLASTNode("ATOM", value=result)
        
        # Si es lista, procesar elementos
        if isinstance(result, list):
            if len(result) == 0:
                return None
            if len(result) == 1:
                return self._transform_result(result[0])
            # Múltiples elementos
            return [self._transform_result(item) for item in result]
        
        # Si no tiene atributos especiales, puede ser un ParseResults
        if not hasattr(result, 'asList'):
            return result
        
        # Es un ParseResults de pyparsing
        result_list = result.asList()
        
        # Verificar si tiene nombre (de Group o named results)
        if hasattr(result, 'getName'):
            name = result.getName()
        else:
            name = None
        
        if name == 'pred_name':
            # Es parte de un predicado
            return FOLASTNode("NAME", value=result[0])
        
        if name == 'terms':
            # Lista de términos
            terms = []
            for item in result:
                if isinstance(item, str):
                    terms.append(FOLASTNode("TERM", value=item))
                else:
                    terms.append(self._transform_result(item))
            return FOLASTNode("TERM_LIST", children=terms)
        
        if name == 'var':
            # Variable de cuantificador
            var_name = result[0] if isinstance(result, list) else str(result)
            return FOLASTNode("VARIABLE", value=var_name)
        
        if name == 'scope':
            # Scope de cuantificador
            return self._transform_result(result[0])
        
        if name == 'not':
            # Negación
            child = self._transform_result(result[0])
            return FOLASTNode("NOT", children=[child])
        
        if name == 'forall':
            # Cuantificador universal
            var_node = self._transform_result(result.var)
            var_name = var_node.value if isinstance(var_node, FOLASTNode) else str(var_node)
            scope = self._transform_result(result.scope)
            return FOLASTNode("FORALL", value=var_name, children=[scope])
        
        if name == 'exists':
            # Cuantificador existencial
            var_node = self._transform_result(result.var)
            var_name = var_node.value if isinstance(var_node, FOLASTNode) else str(var_node)
            scope = self._transform_result(result.scope)
            return FOLASTNode("EXISTS", value=var_name, children=[scope])
        
        if name == 'xor':
            # XOR - puede tener múltiples elementos
            elements = [self._transform_result(result[0])]
            if hasattr(result, 'xor') and result.xor:
                elements.extend([self._transform_result(item) for item in result.xor])
            
            if len(elements) == 1:
                return elements[0]
            
            # Combinar con asociatividad izquierda
            result_node = elements[0]
            for elem in elements[1:]:
                result_node = FOLASTNode("XOR", children=[result_node, elem])
            return result_node
        
        if name == 'and':
            # Conjunción
            elements = [self._transform_result(result[0])]
            if hasattr(result, 'and') and result.and_:
                elements.extend([self._transform_result(item) for item in result.and_])
            
            if len(elements) == 1:
                return elements[0]
            
            # Combinar con asociatividad izquierda
            result_node = elements[0]
            for elem in elements[1:]:
                result_node = FOLASTNode("AND", children=[result_node, elem])
            return result_node
        
        if name == 'or':
            # Disyunción
            elements = [self._transform_result(result[0])]
            if hasattr(result, 'or') and result.or_:
                elements.extend([self._transform_result(item) for item in result.or_])
            
            if len(elements) == 1:
                return elements[0]
            
            # Combinar con asociatividad izquierda
            result_node = elements[0]
            for elem in elements[1:]:
                result_node = FOLASTNode("OR", children=[result_node, elem])
            return result_node
        
        if name == 'implies':
            # Implicación
            elements = [self._transform_result(result[0])]
            if hasattr(result, 'implies') and result.implies:
                elements.extend([self._transform_result(item) for item in result.implies])
            
            if len(elements) == 1:
                return elements[0]
            
            # Combinar con asociatividad izquierda
            result_node = elements[0]
            for elem in elements[1:]:
                result_node = FOLASTNode("IMPLIES", children=[result_node, elem])
            return result_node
        
        if name == 'bicond':
            # Bicondicional
            elements = [self._transform_result(result[0])]
            if hasattr(result, 'bicond') and result.bicond:
                elements.extend([self._transform_result(item) for item in result.bicond])
            
            if len(elements) == 1:
                return elements[0]
            
            # Combinar con asociatividad izquierda
            result_node = elements[0]
            for elem in elements[1:]:
                result_node = FOLASTNode("BICOND", children=[result_node, elem])
            return result_node
        
        # Predicado (estructura por defecto)
        if hasattr(result, 'pred_name'):
            pred_name = result.pred_name[0] if isinstance(result.pred_name, list) else str(result.pred_name)
            if hasattr(result, 'terms') and result.terms:
                terms = self._transform_result(result.terms)
                if isinstance(terms, FOLASTNode) and terms.node_type == "TERM_LIST":
                    return FOLASTNode("PREDICATE", value=pred_name, children=terms.children)
                return FOLASTNode("PREDICATE", value=pred_name, children=[terms])
            else:
                return FOLASTNode("ATOM", value=pred_name)
        
        # Por defecto, intentar procesar como lista
        if isinstance(result, list):
            if len(result) == 1:
                return self._transform_result(result[0])
            return [self._transform_result(item) for item in result]
        
        # Si no se puede transformar, retornar como está
        return result
    
    def parse(self, formula: str) -> FOLASTNode:
        """
        Parsea una fórmula FOL y retorna el AST.
        
        Args:
            formula: String con la fórmula FOL
        
        Returns:
            FOLASTNode: Raíz del AST
        """
        try:
            result = self.parser.parseString(formula, parseAll=True)
            ast = self._transform_result(result[0])
            return ast
        except ParseException as e:
            raise ValueError(f"Error al parsear la fórmula '{formula}': {e}")


if __name__ == '__main__':
    # Prueba básica
    parser = FOLParserPyparsing()
    
    # Ejemplo simple
    test_formula = "GenusBulbophyllum(bulbophyllumAttenuatum)"
    print(f"Parseando: {test_formula}")
    try:
        ast = parser.parse(test_formula)
        print(f"AST: {ast}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Ejemplo con cuantificador
    test_formula2 = "∀x (GenusBulbophyllum(x) → Orchid(x))"
    print(f"\nParseando: {test_formula2}")
    try:
        ast2 = parser.parse(test_formula2)
        print(f"AST: {ast2}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Ejemplo con XOR
    test_formula3 = "Student(rina) ⊕ ¬AwareThatDrug(rina, caffeine)"
    print(f"\nParseando: {test_formula3}")
    try:
        ast3 = parser.parse(test_formula3)
        print(f"AST: {ast3}")
    except Exception as e:
        print(f"Error: {e}")


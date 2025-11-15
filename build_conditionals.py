"""
Construcción de condicionales globales a partir de premisas y conclusiones.

Para cada registro del dataset FOLIO, construye:
(Prem1 ∧ Prem2 ∧ ... ∧ PremN) → Conclusión

Sin modificar el texto original de las premisas y conclusión.
"""

from typing import List, Union
from fol_parser import FOLParser, FOLASTNode


def build_global_conditional(premises: List[str], conclusion: str) -> str:
    """
    Construye el condicional global a partir de premisas y conclusión.
    
    Args:
        premises: Lista de premisas (cada una es una fórmula FOL)
        conclusion: Conclusión (fórmula FOL)
    
    Returns:
        String con la fórmula condicional global:
        (Prem1 ∧ Prem2 ∧ ... ∧ PremN) → Conclusión
    """
    if not premises:
        raise ValueError("Debe haber al menos una premisa")
    
    # Unir premisas con ∧
    if len(premises) == 1:
        premises_conjunction = premises[0]
    else:
        premises_conjunction = " ∧ ".join(f"({prem})" if needs_parentheses(prem) else prem 
                                         for prem in premises)
    
    # Construir condicional global
    # Si la conclusión necesita paréntesis, los agregamos
    if needs_parentheses(conclusion):
        conclusion_wrapped = f"({conclusion})"
    else:
        conclusion_wrapped = conclusion
    
    global_conditional = f"({premises_conjunction}) → {conclusion_wrapped}"
    
    return global_conditional


def needs_parentheses(formula: str) -> bool:
    """
    Determina si una fórmula necesita paréntesis cuando se usa como operando.
    
    Esto es una heurística simple. Una fórmula necesita paréntesis si:
    - Ya contiene operadores binarios (∧, ∨, →, ↔, ⊕)
    - Comienza con ¬ seguido de algo que no sea un átomo simple
    """
    formula = formula.strip()
    
    # Si ya está entre paréntesis externos, no necesita más
    if formula.startswith('(') and formula.endswith(')'):
        # Verificar que los paréntesis están balanceados
        count = 0
        for i, char in enumerate(formula):
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
            if count == 0 and i < len(formula) - 1:
                # Paréntesis se cierran antes del final
                return True
        if count == 0:
            # Paréntesis balanceados al inicio y final
            return False
    
    # Verificar si contiene operadores binarios
    binary_ops = ['∧', '∨', '→', '↔', '⊕']
    for op in binary_ops:
        if op in formula:
            return True
    
    # Si comienza con ¬ y hay más estructura después
    if formula.startswith('¬'):
        remaining = formula[1:].strip()
        if remaining.startswith('(') or any(op in remaining for op in binary_ops):
            return True
    
    return False


def parse_global_conditional(premises: List[str], conclusion: str) -> FOLASTNode:
    """
    Construye y parsea el condicional global.
    
    SOLUCIÓN ROBUSTA: Parsea cada premisa y la conclusión individualmente,
    luego combina los ASTs manualmente. Esto evita problemas con AND muy largos
    en el parser cuando hay muchas premisas.
    
    Args:
        premises: Lista de premisas
        conclusion: Conclusión
    
    Returns:
        FOLASTNode: AST del condicional global parseado
    """
    parser = FOLParser()
    
    # Parsear cada premisa individualmente
    premise_asts = []
    for premise in premises:
        try:
            ast = parser.parse(premise)
            premise_asts.append(ast)
        except Exception as e:
            raise ValueError(f"Error al parsear premisa '{premise}': {e}")
    
    # Parsear la conclusión
    try:
        conclusion_ast = parser.parse(conclusion)
    except Exception as e:
        raise ValueError(f"Error al parsear conclusión '{conclusion}': {e}")
    
    # Combinar premisas con AND (asociatividad izquierda)
    if len(premise_asts) == 0:
        raise ValueError("Debe haber al menos una premisa")
    elif len(premise_asts) == 1:
        premises_conjunction = premise_asts[0]
    else:
        # Construir AND izquierdo-asociativo: ((A ∧ B) ∧ C) ∧ D ...
        premises_conjunction = premise_asts[0]
        for premise_ast in premise_asts[1:]:
            premises_conjunction = FOLASTNode("AND", children=[premises_conjunction, premise_ast])
    
    # Construir el condicional global: (Premises) → Conclusion
    global_conditional_ast = FOLASTNode("IMPLIES", children=[premises_conjunction, conclusion_ast])
    
    return global_conditional_ast


if __name__ == '__main__':
    # Ejemplo 1 del usuario
    premises1 = [
        "GenusBulbophyllum(bulbophyllumAttenuatum)",
        "∀x (GenusBulbophyllum(x) → Orchid(x))"
    ]
    conclusion1 = "¬Orchid(bulbophyllumAttenuatum)"
    
    conditional1 = build_global_conditional(premises1, conclusion1)
    print("Ejemplo 1:")
    print(f"Condicional global: {conditional1}")
    
    # Parsear y mostrar AST
    ast1 = parse_global_conditional(premises1, conclusion1)
    print(f"AST: {ast1}")
    
    # Ejemplo 2 con XOR
    premises2 = [
        "∀x (DrinkRegularly(x, coffee) → IsDependentOn(x, caffeine))",
        "∀x (DrinkRegularly(x, coffee) ∨ (¬WantToBeAddictedTo(x, caffeine)))",
        "∀x (¬WantToBeAddictedTo(x, caffeine) → ¬AwareThatDrug(x, caffeine))",
        "¬(Student(rina) ⊕ ¬AwareThatDrug(rina, caffeine))",
        "¬(IsDependentOn(rina, caffeine) ⊕ Student(rina))"
    ]
    conclusion2 = "¬WantToBeAddictedTo(rina, caffeine) ∨ (¬AwareThatDrug(rina, caffeine))"
    
    conditional2 = build_global_conditional(premises2, conclusion2)
    print("\nEjemplo 2:")
    print(f"Condicional global: {conditional2}")
    
    # Parsear y mostrar AST
    ast2 = parse_global_conditional(premises2, conclusion2)
    print(f"AST: {ast2}")


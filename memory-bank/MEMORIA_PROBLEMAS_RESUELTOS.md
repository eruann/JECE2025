# Memoria de Problemas Resueltos

## Problema 1: Reglas Duplicadas en Gramática Lark

**Fecha:** Durante desarrollo inicial

**Error:**
```
lark.exceptions.GrammarError: Rules defined twice:
  * <biconditional : implication>
```

**Causa Raíz:**
La gramática tenía alternativas redundantes:
```lark
?biconditional: implication ("↔" implication)* -> bicond
             | implication  # ← Esta alternativa causaba duplicación
```

**Solución:**
Eliminar alternativas redundantes, usar solo repeticiones opcionales:
```lark
?biconditional: implication ("↔" implication)* -> bicond
```

**Resultado:** ✅ Gramática funciona correctamente

---

## Problema 2: Objetos Tree sin Transformar

**Fecha:** Durante pruebas iniciales

**Error:**
```
AttributeError: 'Tree' object has no attribute 'node_type'
```

**Causa Raíz:**
Algunos nodos Tree de Lark no se transformaban completamente a FOLASTNode, especialmente en repeticiones.

**Solución:**
Implementar `_ensure_fol_node()` que:
1. Detecta si un argumento es un Tree sin transformar
2. Lo transforma recursivamente
3. Maneja casos especiales (operadores lógicos, nodos con un solo hijo)

**Código Clave:**
```python
def _ensure_fol_node(self, arg):
    from lark import Tree
    if isinstance(arg, Tree):
        # Transformar recursivamente
        # Manejar casos especiales
        ...
    return arg
```

**Resultado:** ✅ Todos los nodos se transforman correctamente

---

## Problema 3: Wrappers OR/AND Innecesarios

**Fecha:** Durante pruebas

**Síntoma:**
AST mostraba `OR(AND(PREDICATE(...)))` cuando debería ser solo `PREDICATE(...)`

**Causa Raíz:**
Cuando una repetición tenía un solo elemento, Lark creaba un Tree con ese elemento, y nuestro transformer lo envolvía en OR/AND innecesarios.

**Solución:**
1. Detectar operadores lógicos importantes (NOT, FORALL, EXISTS) y preservarlos siempre
2. Si un operador binario tiene un solo hijo, retornar ese hijo directamente
3. Solo desenrollar nodos intermedios de la gramática, no operadores lógicos

**Código Clave:**
```python
# En _ensure_fol_node
if arg.data in ('or', 'and', 'xor', 'implies', 'bicond') and len(arg.children) == 1:
    return self._ensure_fol_node(arg.children[0])  # Desenrollar wrapper
elif arg.data == 'not':
    return FOLASTNode("NOT", children=[...])  # Preservar NOT
```

**Resultado:** ✅ AST limpio sin wrappers innecesarios

---

## Problema 4: Pérdida de Premisas en AND Largos

**Fecha:** Durante pruebas con ejemplo 2 (5 premisas)

**Síntoma:**
- Condicional con 5 premisas solo mostraba 2 en el AST
- XOR no se detectaba en las métricas
- Algunas premisas se perdían completamente

**Causa Raíz:**
Lark tenía problemas parseando strings muy largos con muchos ANDs anidados:
```
((A ∧ B) ∧ C) ∧ D) ∧ E
```

**Solución Implementada:**
Cambiar `parse_global_conditional()` para:
1. Parsear cada premisa individualmente (esto ya funcionaba)
2. Parsear la conclusión individualmente
3. Combinar los ASTs manualmente con nodos AND

**Código Clave:**
```python
def parse_global_conditional(premises, conclusion):
    parser = FOLParser()
    
    # Parsear individualmente
    premise_asts = [parser.parse(p) for p in premises]
    conclusion_ast = parser.parse(conclusion)
    
    # Combinar manualmente (evita problema de Lark)
    result = premise_asts[0]
    for ast in premise_asts[1:]:
        result = FOLASTNode("AND", children=[result, ast])
    
    return FOLASTNode("IMPLIES", children=[result, conclusion_ast])
```

**Resultado:** 
- ✅ Todas las premisas se preservan correctamente
- ✅ XOR se detecta en las métricas
- ✅ Funciona con cualquier número de premisas

---

## Problema 5: Graphviz No Instalado

**Fecha:** Durante pruebas

**Error:**
```
graphviz.backend.execute.ExecutableNotFound: failed to execute PosixPath('dot')
```

**Causa Raíz:**
Graphviz es una dependencia del sistema, no de Python. No todos los usuarios lo tienen instalado.

**Solución:**
1. Hacer `ast_to_svg()` retornar `None` si falla
2. Manejar errores gracefully con try/except
3. Continuar con exportación JSON aunque falle SVG
4. Documentar que Graphviz es opcional

**Código Clave:**
```python
def ast_to_svg(...):
    try:
        # ... código de graphviz ...
        return output_path
    except Exception as e:
        print(f"⚠ Advertencia: No se pudo exportar SVG: {e}")
        return None
```

**Resultado:** 
- ✅ Código funciona aunque Graphviz no esté instalado
- ✅ Usuario puede instalar Graphviz después si quiere
- ✅ JSON siempre se exporta correctamente

---

## Problema 6: Instalación de Dependencias

**Fecha:** Inicio del proyecto

**Error:**
```
ERROR: Could not find a version that satisfies the requirement lark-parser>=1.1.7
```

**Causa Raíz:**
El paquete correcto es `lark`, no `lark-parser`.

**Solución:**
Cambiar `requirements.txt`:
```
lark-parser>=1.1.7  # ❌ Incorrecto
lark>=1.0.0        # ✅ Correcto
```

**Resultado:** ✅ Instalación funciona correctamente

---

## Problema 7: Preservación de NOT y FORALL

**Fecha:** Durante desarrollo

**Síntoma:**
- `¬Orchid(x)` se parseaba como `PREDICATE(Orchid)` (perdía el NOT)
- `∀x (P(x))` se parseaba como solo `FORALL(x)` (perdía el scope)

**Causa Raíz:**
`_ensure_fol_node()` estaba desenrollando demasiado, incluso operadores lógicos importantes.

**Solución:**
1. Crear lista de operadores lógicos importantes que NO deben desenrollarse
2. Preservar NOT, FORALL, EXISTS siempre
3. Solo desenrollar nodos intermedios de la gramática

**Código Clave:**
```python
logical_operators = ('or', 'and', 'xor', 'implies', 'bicond', 'not', 'forall', 'exists')

if arg.data == 'not':
    return FOLASTNode("NOT", children=[...])  # Preservar
elif arg.data in ('forall', 'exists'):
    return FOLASTNode(node_type, value=var_name, children=[scope])  # Preservar
```

**Resultado:** 
- ✅ NOT se preserva correctamente
- ✅ FORALL/EXISTS preservan su scope
- ✅ Estructura del AST es correcta

---

## Resumen de Soluciones

| Problema | Solución | Estado |
|----------|----------|--------|
| Reglas duplicadas | Eliminar alternativas redundantes | ✅ Resuelto |
| Trees sin transformar | `_ensure_fol_node()` recursivo | ✅ Resuelto |
| Wrappers innecesarios | Detectar y desenrollar solo nodos intermedios | ✅ Resuelto |
| Pérdida de premisas | Parsear individualmente y combinar ASTs | ✅ Resuelto |
| Graphviz faltante | Exportación SVG opcional | ✅ Resuelto |
| Dependencias incorrectas | Usar `lark` en lugar de `lark-parser` | ✅ Resuelto |
| Pérdida de NOT/FORALL | Preservar operadores lógicos importantes | ✅ Resuelto |

## Lecciones Aprendidas

1. **Parsear individualmente es más robusto** que parsear strings complejos
2. **Transformar recursivamente** asegura que todos los nodos se conviertan correctamente
3. **Preservar estructura lógica** es más importante que simplificar
4. **Hacer features opcionales** mejora la robustez del código
5. **Probar con casos reales** (como ejemplo 2) revela problemas que casos simples no muestran


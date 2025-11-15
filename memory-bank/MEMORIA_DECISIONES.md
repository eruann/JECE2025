# Memoria de Decisiones - Parser FOL para FOLIO

## Decisión 1: Elección del Parser

**Fecha:** Inicio del proyecto

**Contexto:** Necesitábamos un parser para fórmulas FOL que soportara:
- Operadores Unicode (∧, ∨, →, ↔, ¬, ⊕)
- Cuantificadores (∀, ∃)
- Preservación de nombres exactos
- Estructuras recursivas complejas

**Opciones Consideradas:**

1. **Lark** ✅ (Elegida)
   - Pros: Gramática declarativa, buena comunidad, maneja recursión
   - Contras: Problemas con repeticiones largas

2. **NLTK (nltk.sem.logic)**
   - Pros: Específico para lógica
   - Contras: No soporta XOR, sintaxis diferente, requeriría extensión significativa

3. **pyparsing**
   - Pros: Muy flexible
   - Contras: Más verboso, requiere más trabajo de implementación

4. **PLY**
   - Pros: Estable y probado
   - Contras: Más complejo, requiere archivos separados

**Decisión:** Usar Lark por su simplicidad y porque ya teníamos código funcionando.

**Resultado:** Funciona bien después de implementar la solución de parsear individualmente.

---

## Decisión 2: Solución para AND Largos

**Fecha:** Durante desarrollo

**Problema:** Lark perdía premisas cuando había 5+ elementos en un AND largo.

**Opciones Consideradas:**

1. **Arreglar la gramática Lark** ❌
   - Intentamos varias veces sin éxito
   - El problema era inherente a cómo Lark maneja repeticiones

2. **Cambiar a pyparsing** ⚠️
   - Crearíamos un prototipo pero requería mucho trabajo
   - No garantizaba solución

3. **Parsear individualmente y combinar ASTs** ✅ (Elegida)
   - Parsear cada premisa por separado (ya funcionaba)
   - Combinar ASTs manualmente
   - Evita completamente el problema

**Decisión:** Implementar solución de parsear individualmente.

**Resultado:** 
- Funciona perfectamente con cualquier número de premisas
- Más robusto y predecible
- No depende de cómo sea la fórmula larga

**Código Clave:**
```python
def parse_global_conditional(premises, conclusion):
    # Parsear cada premisa individualmente
    premise_asts = [parser.parse(p) for p in premises]
    conclusion_ast = parser.parse(conclusion)
    
    # Combinar manualmente
    result = premise_asts[0]
    for ast in premise_asts[1:]:
        result = FOLASTNode("AND", children=[result, ast])
    
    return FOLASTNode("IMPLIES", children=[result, conclusion_ast])
```

---

## Decisión 3: Estructura del AST

**Fecha:** Inicio del proyecto

**Contexto:** Necesitábamos representar fórmulas FOL como árboles para calcular métricas.

**Opciones Consideradas:**

1. **Usar Trees de Lark directamente** ❌
   - Pros: Ya están disponibles
   - Contras: Difícil de trabajar, no preserva tipos claros

2. **Crear clase FOLASTNode personalizada** ✅ (Elegida)
   - Pros: Control total, fácil serialización, tipos claros
   - Contras: Requiere implementación

**Decisión:** Crear `FOLASTNode` con:
- `node_type`: Tipo del nodo (AND, OR, XOR, etc.)
- `value`: Valor (nombre de predicado, variable, etc.)
- `children`: Lista de hijos

**Resultado:** 
- Fácil de trabajar
- Serialización simple a JSON
- Cálculo de métricas directo

---

## Decisión 4: Manejo de XOR

**Fecha:** Durante desarrollo

**Problema:** NLTK no soporta XOR, necesitábamos asegurar que Lark lo manejara.

**Decisión:** 
- Incluir ⊕ directamente en la gramática Lark
- Crear nodo XOR en el AST
- Asegurar que se detecte en las métricas

**Resultado:** 
- XOR funciona perfectamente
- Se detecta correctamente en distribución de conectivas
- Preservado en todas las transformaciones

---

## Decisión 5: Exportación SVG Opcional

**Fecha:** Durante desarrollo

**Problema:** Graphviz no siempre está instalado, causaba errores.

**Opciones:**

1. **Requerir Graphviz** ❌
   - Limitaría uso del código

2. **Hacer SVG opcional** ✅ (Elegida)
   - Manejar errores gracefully
   - Continuar con JSON aunque falle SVG

**Decisión:** Hacer `ast_to_svg()` retornar `None` si falla, continuar con JSON.

**Resultado:** 
- Código más robusto
- Funciona aunque Graphviz no esté instalado
- Usuario puede instalar Graphviz después si quiere visualizaciones

---

## Decisión 6: Modularidad del Código

**Fecha:** Final del desarrollo

**Contexto:** Usuario preguntó si los módulos son exportables.

**Decisión:** 
- Crear `__init__.py` con exports principales
- Documentar todos los módulos
- Crear `example_usage.py` con ejemplos
- Crear `README.md` completo

**Resultado:**
- Código completamente modular
- Fácil de importar y usar
- Bien documentado

---

## Lecciones Aprendidas

1. **Parsear individualmente es más robusto** que parsear strings largos complejos
2. **Lark funciona bien** para casos individuales, pero tiene limitaciones con repeticiones muy largas
3. **Crear AST personalizado** da más control que usar estructuras del parser
4. **Hacer features opcionales** (como SVG) mejora la robustez del código
5. **Documentar decisiones** ayuda a entender por qué se hizo algo de cierta manera

---

## Próximas Decisiones Potenciales

1. **¿Agregar más validación de fórmulas mal formadas?**
2. **¿Optimizar para datasets muy grandes?**
3. **¿Agregar más métricas según necesidades del proyecto?**
4. **¿Mejorar visualizaciones SVG con colores y mejor layout?**


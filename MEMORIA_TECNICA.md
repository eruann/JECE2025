# Memoria Técnica - Parser FOL para Dataset FOLIO

## Fecha de Creación
2025

## Objetivo del Proyecto

Desarrollar un sistema completo para procesar fórmulas de Lógica de Primer Orden (FOL) del dataset FOLIO, que incluye:
- Construcción de condicionales globales por registro
- Parsing de fórmulas FOL preservando nombres exactos
- Cálculo de métricas guiadas por Gamut
- Serialización y visualización de resultados

## Arquitectura del Sistema

### Módulos Principales

1. **`fol_parser.py`** - Parser FOL usando Lark
   - Gramática Lark completa para FOL
   - Soporte para operadores: ∧, ∨, →, ↔, ¬, ⊕ (XOR)
   - Soporte para cuantificadores: ∀, ∃
   - Clase `FOLASTNode` para representar el AST
   - Clase `FOLTransformer` para convertir árbol Lark a AST estructurado

2. **`build_conditionals.py`** - Construcción de condicionales globales
   - `build_global_conditional()`: Construye string del condicional
   - `parse_global_conditional()`: **SOLUCIÓN ROBUSTA** - Parsea cada premisa individualmente y combina ASTs manualmente
   - Evita problemas con AND muy largos en el parser

3. **`metrics.py`** - Cálculo de métricas
   - Profundidad total y de operador
   - Scope de cuantificadores y conectivas
   - Ligadura de variables
   - Conteos (subfórmulas, cuantificadores, distribución de conectivas)

4. **`serialize.py`** - Exportación
   - JSON: AST + métricas
   - SVG: Visualización del árbol (requiere Graphviz)

5. **`download_folio.py`** - Descarga del dataset
   - Autenticación con HuggingFace
   - Carga desde `.env`

## Decisiones de Diseño Clave

### 1. Elección de Parser: Lark

**Decisión:** Usar Lark en lugar de otras alternativas (NLTK, pyparsing, PLY)

**Razones:**
- Gramática declarativa clara
- Buen soporte de comunidad
- Maneja recursión bien
- Ya implementado y funcionando para casos simples

**Problema Encontrado:**
- Problemas con repeticiones largas (`*`) en estructuras complejas
- Perdía algunas premisas en AND muy largos (5+ elementos)

**Solución Implementada:**
- Parsear cada premisa individualmente
- Combinar ASTs manualmente en lugar de parsear el string completo
- Esto evita el problema y funciona con cualquier número de premisas

### 2. Estructura del AST

**Decisión:** Crear clase `FOLASTNode` personalizada

**Estructura:**
```python
class FOLASTNode:
    - node_type: str (AND, OR, XOR, IMPLIES, NOT, FORALL, EXISTS, PREDICATE, ATOM, etc.)
    - value: Any (nombre de predicado, variable, etc.)
    - children: List[FOLASTNode]
```

**Ventajas:**
- Control total sobre la estructura
- Fácil serialización a JSON
- Preserva nombres exactos de FOLIO

### 3. Manejo de Repeticiones

**Problema:** Lark tenía dificultades con `A ∧ B ∧ C ∧ D ∧ E` cuando se parseaba como string completo.

**Solución:** 
- Parsear individualmente: `A`, `B`, `C`, `D`, `E`
- Combinar manualmente: `AND(AND(AND(AND(A, B), C), D), E)`
- Esto garantiza que todas las premisas se preserven correctamente

## Problemas Encontrados y Soluciones

### Problema 1: Reglas Duplicadas en Gramática Lark

**Síntoma:** Error "Rules defined twice: <biconditional : implication>"

**Causa:** Alternativas redundantes en la gramática creaban reglas duplicadas

**Solución:** Eliminar alternativas redundantes, usar solo repeticiones opcionales `*`

### Problema 2: Objetos Tree de Lark sin Transformar

**Síntoma:** `AttributeError: 'Tree' object has no attribute 'node_type'`

**Causa:** Algunos nodos Tree no se transformaban completamente a FOLASTNode

**Solución:** Implementar `_ensure_fol_node()` que transforma recursivamente cualquier Tree restante

### Problema 3: Wrappers OR/AND Innecesarios

**Síntoma:** AST con estructura `OR(AND(PREDICATE(...)))` cuando debería ser solo `PREDICATE(...)`

**Causa:** Repeticiones con un solo elemento creaban wrappers innecesarios

**Solución:** 
- Detectar operadores lógicos importantes y no desenrollarlos
- Si un operador binario tiene un solo hijo, retornar ese hijo directamente
- Preservar NOT, FORALL, EXISTS siempre

### Problema 4: Pérdida de Premisas en AND Largos

**Síntoma:** En condicionales con 5+ premisas, algunas se perdían

**Causa:** Lark tenía problemas parseando strings muy largos con muchos ANDs

**Solución:** Cambiar `parse_global_conditional()` para parsear individualmente y combinar ASTs

### Problema 5: Graphviz No Instalado

**Síntoma:** Error al exportar SVG

**Solución:** Hacer exportación SVG opcional con manejo de errores graceful

## Estado Actual del Código

### Funcionalidades Completadas ✅

- [x] Parser FOL completo con todos los operadores y cuantificadores
- [x] Construcción de condicionales globales
- [x] Cálculo de todas las métricas requeridas
- [x] Exportación a JSON
- [x] Exportación a SVG (opcional, requiere Graphviz)
- [x] Descarga del dataset FOLIO
- [x] Preservación de nombres exactos de FOLIO
- [x] Manejo robusto de cualquier número de premisas
- [x] Soporte completo para XOR (⊕)

### Archivos Creados

1. `fol_parser.py` - Parser principal (342 líneas)
2. `build_conditionals.py` - Construcción de condicionales (138 líneas)
3. `metrics.py` - Cálculo de métricas (350 líneas)
4. `serialize.py` - Serialización (208 líneas)
5. `download_folio.py` - Descarga de datos (48 líneas)
6. `test_examples.py` - Pruebas (187 líneas)
7. `example_usage.py` - Ejemplos de uso (75 líneas)
8. `__init__.py` - Paquete Python (75 líneas)
9. `requirements.txt` - Dependencias
10. `README.md` - Documentación
11. `.gitignore` - Exclusiones

### Dependencias

- `lark>=1.0.0` - Parser
- `datasets>=2.14.0` - Descarga de HuggingFace
- `python-dotenv>=1.0.0` - Variables de entorno
- `graphviz>=0.20.1` - Visualizaciones (opcional)

## Pruebas Realizadas

### Ejemplo 1: Sin XOR
- ✅ Parseo correcto
- ✅ Métricas calculadas correctamente
- ✅ Exportación JSON/SVG funcionando

### Ejemplo 2: Con XOR (5 premisas)
- ✅ Todas las premisas parseadas correctamente
- ✅ XOR detectado en distribución de conectivas (2 nodos)
- ✅ Métricas completas calculadas
- ✅ Exportación funcionando

### Fórmulas Individuales
- ✅ Predicados simples
- ✅ Negación
- ✅ Cuantificadores
- ✅ XOR
- ✅ NOT XOR

## Consideraciones Futuras

1. **Optimización:** El parser podría optimizarse para fórmulas muy grandes
2. **Validación:** Agregar validación más estricta de fórmulas mal formadas
3. **Métricas Adicionales:** Posibilidad de agregar más métricas según necesidades
4. **Visualización:** Mejorar el formato SVG con colores y mejor layout
5. **Testing:** Agregar tests unitarios más completos

## Notas Técnicas

- El código está completamente parametrizado y modular
- Todos los módulos son exportables e independientes
- La solución de parsear individualmente es robusta y escalable
- El código preserva exactamente los nombres de FOLIO sin modificaciones


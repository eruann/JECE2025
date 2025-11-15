# FOL Parser para Dataset FOLIO

Sistema completo para procesar fórmulas de Lógica de Primer Orden (FOL) del dataset FOLIO, incluyendo parsing, cálculo de métricas y visualización.

## Estructura del Proyecto

```
JECE2025/
├── src/                  # Módulos principales (paquete Python)
├── scripts/              # Scripts ejecutables
│   ├── helpers/         # Scripts auxiliares
│   └── metrics/         # Scripts de métricas
├── pipeline/            # Pipelines de procesamiento
├── tests/               # Tests unitarios
├── memory-bank/         # Documentación y memorias
├── datasets/            # Datasets descargados
└── outputs/             # Resultados generados
```

Ver [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) para más detalles.

## Características

- ✅ Parser FOL completo con soporte para:
  - Operadores: `∧`, `∨`, `→`, `↔`, `¬`, `⊕` (XOR)
  - Cuantificadores: `∀`, `∃`
  - Preservación de nombres exactos de predicados y constantes
- ✅ Construcción de condicionales globales
- ✅ Cálculo de métricas guiadas por Gamut:
  - Profundidad total y de operador
  - Scope de cuantificadores y conectivas
  - Ligadura de variables
  - Conteos (subfórmulas, cuantificadores, distribución de conectivas)
- ✅ Exportación a JSON y SVG
- ✅ Descarga del dataset FOLIO desde HuggingFace

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Instalar Graphviz (para visualizaciones SVG)
# Ubuntu/Debian:
sudo apt-get install graphviz

# O con conda:
conda install -c conda-forge graphviz
```

## Instalación

**NOTA:** Los módulos son archivos simples en `src/`, NO necesitas instalar nada como paquete.

### Usar directamente desde src/

```python
# En cualquier script, agrega estas líneas al inicio:
import sys
from pathlib import Path

# Agregar src/ al path para importar módulos
project_root = Path(__file__).parent.parent  # Ajusta según ubicación del script
sys.path.insert(0, str(project_root / 'src'))

# Ahora puedes importar directamente
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics
from serialize import export_complete_analysis
```

**Ventajas:**
- ✅ No necesitas instalar nada
- ✅ Puedes modificar los archivos en `src/` directamente
- ✅ Cambios se reflejan inmediatamente
- ✅ Fácil de corregir y mejorar

## Uso Básico

### Verificar entorno

```bash
python scripts/helpers/check_environment.py
```

### Importar módulos

### Parsear una fórmula individual

```python
parser = FOLParser()
formula = "GenusBulbophyllum(bulbophyllumAttenuatum)"
ast = parser.parse(formula)
print(ast)  # PREDICATE(GenusBulbophyllum)
```

### Construir y parsear condicional global

```python
premises = [
    "GenusBulbophyllum(bulbophyllumAttenuatum)",
    "∀x (GenusBulbophyllum(x) → Orchid(x))"
]
conclusion = "¬Orchid(bulbophyllumAttenuatum)"

# Parsear condicional global (parsea cada premisa individualmente y combina ASTs)
ast = parse_global_conditional(premises, conclusion)
```

### Calcular métricas

```python
metrics = calculate_all_metrics(ast)
print(f"Profundidad total: {metrics['total_depth']}")
print(f"Número de cuantificadores: {metrics['num_quantifiers']}")
print(f"Distribución de conectivas: {metrics['connective_distribution']}")
```

### Exportar análisis completo

```python
files = export_complete_analysis(
    ast,
    original_formula="(Prem1 ∧ Prem2) → Conclusión",
    output_dir='outputs',
    base_name='analisis_001'
)
# Genera: outputs/analisis_001.json y outputs/analisis_001.svg
```

### Pipeline completo

```bash
# Procesar todo el dataset
python pipeline/process_folio.py

# Procesar solo primeros 10 registros
python pipeline/process_folio.py --max-records 10

# Sin generar SVG (más rápido)
python pipeline/process_folio.py --no-svg
```

## Módulos Exportables

### `fol_parser`
- `FOLParser`: Clase principal del parser
- `FOLASTNode`: Nodo del AST
- `get_parser()`: Obtener instancia singleton del parser

### `build_conditionals`
- `build_global_conditional(premises, conclusion)`: Construye string del condicional
- `parse_global_conditional(premises, conclusion)`: Parsea condicional global (recomendado)
- `needs_parentheses(formula)`: Determina si fórmula necesita paréntesis

### `metrics`
- `calculate_total_depth(ast)`: Profundidad total del árbol
- `calculate_operator_depth(ast)`: Profundidad de operadores
- `calculate_quantifier_scope(ast)`: Scope de cuantificadores
- `calculate_connective_scope(ast)`: Scope de conectivas
- `calculate_variable_binding(ast)`: Ligadura de variables
- `count_subformulas(ast)`: Número de subfórmulas
- `count_quantifiers(ast)`: Número de cuantificadores
- `count_connectives(ast)`: Distribución de conectivas
- `calculate_all_metrics(ast)`: Todas las métricas en un dict

### `serialize`
- `ast_to_json(ast, metrics, filepath)`: Exportar a JSON
- `ast_to_svg(ast, filename, directory)`: Exportar a SVG
- `export_complete_analysis(ast, original_formula, ...)`: Exportar todo

### `download_folio`
- `download_folio_dataset(save_path, split)`: Descargar dataset FOLIO

## Ejemplos

Ver `example_usage.py` para ejemplos completos de uso.

## Notas

- El parser parsea cada premisa individualmente y luego combina los ASTs manualmente para evitar problemas con AND muy largos
- Las visualizaciones SVG requieren Graphviz instalado en el sistema
- El dataset FOLIO requiere autenticación de HuggingFace (token en `.env`)

## Licencia

[Especificar licencia]


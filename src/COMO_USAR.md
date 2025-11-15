# Cómo Usar los Módulos en src/

Los módulos en `src/` son **archivos Python simples** que puedes modificar directamente. NO necesitas instalar nada.

## Método Simple (Recomendado)

En cualquier script, agrega estas líneas al inicio:

```python
import sys
from pathlib import Path

# Agregar src/ al path
project_root = Path(__file__).parent.parent  # Ajusta según tu ubicación
sys.path.insert(0, str(project_root / 'src'))

# Ahora importa directamente
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics
```

## Ejemplos por Ubicación del Script

### Si tu script está en `scripts/`:

```python
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))
```

### Si tu script está en `pipeline/`:

```python
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))
```

### Si tu script está en el root:

```python
import sys
sys.path.insert(0, 'src')
```

### Si ejecutas desde cualquier lugar:

```python
import sys
from pathlib import Path

# Encuentra el proyecto (ajusta la ruta según necesites)
project_root = Path('/home/matu/data-science/projects/JECE2025')
sys.path.insert(0, str(project_root / 'src'))
```

## Ventajas de Este Enfoque

✅ **Edición directa** - Abre `src/fol_parser.py` y edita directamente
✅ **Sin instalación** - No necesitas `pip install`
✅ **Cambios inmediatos** - Los cambios se reflejan al ejecutar
✅ **Fácil debugging** - Puedes agregar prints, breakpoints, etc.
✅ **Control total** - Modifica cualquier módulo cuando quieras

## Estructura de los Módulos

```
src/
├── fol_parser.py          # ← Edita este archivo directamente
├── build_conditionals.py  # ← O este
├── metrics.py             # ← O este
├── serialize.py           # ← O este
└── download_folio.py      # ← O este
```

Todos son archivos `.py` normales que puedes abrir y modificar en cualquier editor.

## Ejemplo Completo

```python
#!/usr/bin/env python3
"""
Mi script personalizado
"""

# 1. Configurar imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# 2. Importar módulos
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics

# 3. Usar
parser = FOLParser()
ast = parser.parse("MiFormula(a)")
metrics = calculate_all_metrics(ast)
print(metrics)
```

## ¿Necesitas Corregir Algo?

1. Abre el archivo en `src/` que necesitas modificar
2. Haz tus cambios
3. Guarda
4. Ejecuta tu script - los cambios ya están aplicados

**No necesitas reinstalar nada.**


# Módulos en src/

Estos son **archivos Python simples** en una carpeta, NO un paquete instalable.

## Cómo Usar

### Opción 1: Desde scripts (recomendado)

```python
import sys
from pathlib import Path

# Agregar src/ al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Ahora puedes importar directamente
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics
```

### Opción 2: Usar helper

```python
from scripts._import_helper import setup_imports
setup_imports()

from fol_parser import FOLParser
```

### Opción 3: Importar desde src directamente

Si ejecutas desde el root del proyecto:
```python
import sys
sys.path.insert(0, 'src')

from fol_parser import FOLParser
```

## Ventajas de Este Enfoque

✅ **Fácil de modificar** - Solo edita los archivos .py directamente
✅ **Sin instalación** - No necesitas `pip install`
✅ **Desarrollo rápido** - Cambios se reflejan inmediatamente
✅ **Control total** - Puedes modificar cualquier módulo cuando quieras

## Estructura

- `fol_parser.py` - Parser FOL con Lark
- `build_conditionals.py` - Construcción de condicionales
- `metrics.py` - Cálculo de métricas
- `serialize.py` - Exportación JSON/SVG
- `download_folio.py` - Descarga del dataset
- `_path_helper.py` - Helper interno para path
- `__init__.py` - Exports principales (opcional)

## Nota

Los módulos usan imports relativos cuando se importan como paquete, pero fallback a absolutos cuando se ejecutan directamente. Esto permite máxima flexibilidad.


# Estructura de Módulos - Archivos Simples

## Decisión de Diseño

Los módulos en `src/` son **archivos Python simples** en una carpeta, NO un paquete instalable.

## Razones

1. **Desarrollo rápido** - Puedes editar directamente sin reinstalar
2. **Fácil corrección** - Abres el archivo, corriges, guardas, listo
3. **Sin overhead** - No necesitas setup.py ni instalación
4. **Control total** - Modificas cuando quieras, como quieras

## Cómo Funciona

### Los módulos se cargan manualmente:

```python
# En cualquier script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from fol_parser import FOLParser  # ← Importa directamente
```

### Los módulos internos usan imports compatibles:

```python
# En src/build_conditionals.py
try:
    from .fol_parser import FOLParser  # Si se importa como paquete
except ImportError:
    from fol_parser import FOLParser    # Si se ejecuta directamente
```

Esto permite:
- ✅ Importar desde scripts externos
- ✅ Ejecutar módulos directamente para testing
- ✅ Máxima flexibilidad

## Estructura

```
src/
├── fol_parser.py          # Archivo Python simple
├── build_conditionals.py  # Archivo Python simple
├── metrics.py             # Archivo Python simple
├── serialize.py           # Archivo Python simple
├── download_folio.py      # Archivo Python simple
├── _path_helper.py        # Helper interno
├── __init__.py            # Opcional, para exports
└── README.md              # Documentación
```

## Ventajas vs Paquete Instalable

| Aspecto | Archivos Simples (Actual) | Paquete Instalable |
|---------|---------------------------|-------------------|
| Edición | ✅ Directa, inmediata | ❌ Requiere reinstalar |
| Correcciones | ✅ Abrir y editar | ❌ Más pasos |
| Desarrollo | ✅ Rápido | ⚠️ Más lento |
| Testing | ✅ Cambios inmediatos | ❌ Reinstalar cada vez |
| Distribución | ⚠️ Menos estándar | ✅ Más estándar |
| Uso en otros proyectos | ⚠️ Copiar archivos | ✅ pip install |

**Para desarrollo y correcciones frecuentes, archivos simples son mejores.**

## Cuándo Considerar Paquete Instalable

Solo si:
- El código está muy estable y no necesita cambios
- Quieres distribuir a otros proyectos fácilmente
- Necesitas versionado estricto

Para este proyecto (desarrollo activo con correcciones), archivos simples son la mejor opción.


# Memoria de Reorganización del Proyecto

## Fecha
Noviembre 2025

## Objetivo
Reorganizar el proyecto siguiendo mejores prácticas de data science, separando código, scripts, documentación y datos.

## Estructura Anterior

```
JECE2025/
├── fol_parser.py
├── build_conditionals.py
├── metrics.py
├── serialize.py
├── download_folio.py
├── test_examples.py
├── example_usage.py
├── MEMORIA_*.md
├── __init__.py
└── ... (todo en root)
```

**Problemas:**
- Todo mezclado en el root
- Difícil de navegar
- No sigue convenciones de data science
- Difícil de escalar

## Estructura Nueva

```
JECE2025/
├── src/                      # Módulos principales (paquete Python)
│   ├── __init__.py
│   ├── fol_parser.py
│   ├── build_conditionals.py
│   ├── metrics.py
│   ├── serialize.py
│   └── download_folio.py
│
├── scripts/                  # Scripts ejecutables
│   ├── helpers/
│   │   └── check_environment.py
│   ├── metrics/
│   └── example_usage.py
│
├── pipeline/                 # Pipelines de procesamiento
│   └── process_folio.py
│
├── tests/                    # Tests
│   └── test_examples.py
│
├── memory-bank/              # Documentación
│   ├── MEMORIA_TECNICA.md
│   ├── MEMORIA_DECISIONES.md
│   ├── MEMORIA_PROBLEMAS_RESUELTOS.md
│   ├── INDICE_MEMORIAS.md
│   └── ALTERNATIVAS_PARSER.md
│
├── datasets/                 # Datasets
├── outputs/                  # Resultados
├── setup.py                  # Instalación del paquete
├── requirements.txt
└── README.md
```

## Cambios Realizados

### 1. Módulos → `src/`
- Movidos todos los módulos principales a `src/`
- Actualizados imports para usar imports relativos cuando es posible
- Creado `src/__init__.py` con exports principales
- Creado `setup.py` para instalar como paquete

### 2. Scripts → `scripts/`
- `test_examples.py` → `tests/test_examples.py`
- `example_usage.py` → `scripts/example_usage.py`
- Creado `scripts/helpers/check_environment.py` para verificar entorno

### 3. Pipelines → `pipeline/`
- Creado `pipeline/process_folio.py` para procesamiento completo del dataset

### 4. Documentación → `memory-bank/`
- Todas las memorias movidas a `memory-bank/`
- Archivos de documentación técnica organizados

### 5. Archivos de Configuración
- Creado `setup.py` para instalación del paquete
- Actualizado `.gitignore` con exclusiones apropiadas
- Actualizado `README.md` con nueva estructura

## Imports Actualizados

### Antes:
```python
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
```

### Después (Opción 1 - Instalado como paquete):
```python
from src import FOLParser, parse_global_conditional
```

### Después (Opción 2 - Desde scripts):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
```

## Solución de Imports Relativos

Los módulos en `src/` usan imports relativos cuando se importan como paquete, pero fallback a absolutos cuando se ejecutan directamente:

```python
try:
    from .fol_parser import FOLParser, FOLASTNode
except ImportError:
    from fol_parser import FOLParser, FOLASTNode
```

Esto permite:
- ✅ Importar como paquete: `from src import ...`
- ✅ Ejecutar scripts directamente: `python scripts/example_usage.py`
- ✅ Ejecutar módulos directamente: `python src/metrics.py`

## Beneficios de la Nueva Estructura

1. **Separación clara de responsabilidades**
   - Código reutilizable → `src/`
   - Scripts ejecutables → `scripts/`
   - Pipelines → `pipeline/`
   - Documentación → `memory-bank/`

2. **Escalabilidad**
   - Fácil agregar nuevos módulos en `src/`
   - Fácil agregar nuevos scripts en `scripts/`
   - Fácil agregar nuevos pipelines

3. **Mantenibilidad**
   - Estructura estándar de data science
   - Fácil de navegar
   - Fácil de entender para nuevos desarrolladores

4. **Instalación como paquete**
   - `pip install -e .` instala el paquete
   - Puede ser usado en otros proyectos
   - Versionado claro

## Verificación

Ejecutar:
```bash
python scripts/helpers/check_environment.py
```

Debería mostrar:
- ✓ Estructura del proyecto OK
- ✓ Módulos encontrados
- ✓ Dependencias instaladas

## Próximos Pasos Sugeridos

1. Agregar más tests en `tests/`
2. Crear más scripts helpers según necesidad
3. Agregar más pipelines según casos de uso
4. Considerar agregar `notebooks/` para análisis exploratorios
5. Considerar agregar `config/` para archivos de configuración

## Notas

- Los archivos `.gitkeep` se pueden crear en directorios vacíos para asegurar que se versionen
- El directorio `outputs/` está en `.gitignore` (no versionar resultados)
- El directorio `datasets/` puede tener `.gitkeep` pero los datos grandes no se versionan


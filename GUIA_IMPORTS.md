# Guía Rápida: Cómo Cargar los Módulos

## Método Simple (Copia y Pega)

Al inicio de cualquier script Python, agrega estas 3 líneas:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
```

Luego importa normalmente:

```python
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics
```

## Ejemplos por Ubicación

### Si tu script está en `scripts/`:

```python
import sys
from pathlib import Path

# Estas 2 líneas siempre iguales
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Ahora importa
from fol_parser import FOLParser
```

### Si tu script está en `pipeline/`:

```python
import sys
from pathlib import Path

# Mismas líneas
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Importa
from fol_parser import FOLParser
```

### Si tu script está en el root del proyecto:

```python
import sys
sys.path.insert(0, 'src')  # Más simple

from fol_parser import FOLParser
```

### Si ejecutas desde cualquier lugar (ruta absoluta):

```python
import sys
from pathlib import Path

# Ajusta esta ruta a tu proyecto
project_root = Path('/home/matu/data-science/projects/JECE2025')
sys.path.insert(0, str(project_root / 'src'))

from fol_parser import FOLParser
```

## Ejemplo Completo Funcional

```python
#!/usr/bin/env python3
"""
Mi script que usa los módulos FOL
"""

# PASO 1: Configurar el path (siempre igual)
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# PASO 2: Importar los módulos que necesites
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics
from serialize import export_complete_analysis

# PASO 3: Usar
def main():
    parser = FOLParser()
    
    # Parsear una fórmula
    ast = parser.parse("GenusBulbophyllum(bulbophyllumAttenuatum)")
    print(f"AST: {ast}")
    
    # Condicional global
    premises = ["P(a)", "Q(b)"]
    conclusion = "R(c)"
    ast = parse_global_conditional(premises, conclusion)
    
    # Métricas
    metrics = calculate_all_metrics(ast)
    print(f"Métricas: {metrics}")

if __name__ == '__main__':
    main()
```

## Template para Nuevos Scripts

Copia este template cuando crees un nuevo script:

```python
"""
Descripción de tu script
"""

# ===== CONFIGURACIÓN DE IMPORTS =====
import sys
from pathlib import Path

# Agregar src/ al path para importar módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# ===== IMPORTS DE MÓDULOS =====
from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics
# Agrega otros imports según necesites

# ===== TU CÓDIGO AQUÍ =====
def main():
    # Tu código aquí
    pass

if __name__ == '__main__':
    main()
```

## Verificar que Funciona

Ejecuta este comando para verificar:

```bash
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.').absolute() / 'src')); from fol_parser import FOLParser; print('✓ Imports funcionan')"
```

O simplemente ejecuta uno de los scripts existentes:

```bash
python scripts/example_usage.py
python tests/test_examples.py
```

## Resumen

**Siempre agrega estas 3 líneas al inicio:**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
```

**Luego importa normalmente:**

```python
from fol_parser import FOLParser
```

¡Eso es todo! No necesitas instalar nada.


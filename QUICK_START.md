# Quick Start Guide

## Estructura del Proyecto

```
JECE2025/
├── src/              # Módulos principales
├── scripts/          # Scripts ejecutables  
├── pipeline/         # Pipelines completos
├── tests/            # Tests
├── memory-bank/      # Documentación
├── datasets/         # Datos
└── outputs/          # Resultados
```

## Setup Rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Instalar Graphviz (opcional, para SVG)
sudo apt-get install graphviz

# 3. Configurar .env con tu token de HuggingFace
echo "HF_TOKEN=tu_token_aqui" > .env

# 4. Verificar entorno
python scripts/helpers/check_environment.py

# 5. (Opcional) Instalar como paquete
pip install -e .
```

## Uso Rápido

### Ejemplo Básico

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fol_parser import FOLParser
from build_conditionals import parse_global_conditional
from metrics import calculate_all_metrics

# Parsear fórmula
parser = FOLParser()
ast = parser.parse("GenusBulbophyllum(bulbophyllumAttenuatum)")

# Condicional global
premises = ["P(a)", "Q(b)"]
conclusion = "R(c)"
ast = parse_global_conditional(premises, conclusion)

# Métricas
metrics = calculate_all_metrics(ast)
```

### Ejecutar Tests

```bash
python tests/test_examples.py
```

### Ejecutar Pipeline Completo

```bash
# Procesar primeros 10 registros
python pipeline/process_folio.py --max-records 10
```

## Documentación

- **README.md** - Documentación completa
- **memory-bank/** - Memorias técnicas y decisiones
- **PROJECT_STRUCTURE.md** - Estructura detallada del proyecto


# Estructura del Proyecto

```
JECE2025/
├── memory-bank/              # Documentación y memorias del proyecto
│   ├── MEMORIA_TECNICA.md
│   ├── MEMORIA_DECISIONES.md
│   ├── MEMORIA_PROBLEMAS_RESUELTOS.md
│   └── INDICE_MEMORIAS.md
│
├── datasets/                 # Datasets descargados y procesados
│   └── .gitkeep
│
├── src/                      # Módulos principales del proyecto (paquete Python)
│   ├── __init__.py
│   ├── fol_parser.py         # Parser FOL
│   ├── build_conditionals.py # Construcción de condicionales
│   ├── metrics.py            # Cálculo de métricas
│   ├── serialize.py          # Exportación JSON/SVG
│   └── download_folio.py     # Descarga del dataset
│
├── scripts/                  # Scripts ejecutables
│   ├── helpers/              # Scripts auxiliares
│   │   └── .gitkeep
│   │
│   └── metrics/              # Scripts específicos de métricas
│       └── .gitkeep
│
├── pipeline/                 # Pipelines de procesamiento
│   └── .gitkeep
│
├── tests/                    # Tests unitarios
│   └── .gitkeep
│
├── outputs/                  # Resultados generados (JSON, SVG, etc.)
│   └── .gitkeep
│
├── .env                      # Variables de entorno (no versionado)
├── .gitignore
├── requirements.txt
├── README.md
├── setup.py                  # Para instalar el paquete
└── example_usage.py          # Ejemplos de uso
```

## Descripción de Directorios

### `memory-bank/`
Documentación técnica, decisiones de diseño, problemas resueltos y memorias del proyecto.

### `datasets/`
Almacena datasets descargados (FOLIO) y datos procesados. No versionar archivos grandes.

### `src/`
Módulos principales del proyecto. Este es el paquete Python principal que puede instalarse.

### `scripts/`
Scripts ejecutables:
- `helpers/`: Utilidades y scripts auxiliares
- `metrics/`: Scripts específicos para cálculo/análisis de métricas

### `pipeline/`
Pipelines que ejecutan múltiples tareas en secuencia (ETL, procesamiento completo, etc.)

### `tests/`
Tests unitarios y de integración.

### `outputs/`
Resultados generados: JSON, SVG, reportes, etc. No versionar (agregar a .gitignore).

## Convenciones

- **Módulos reutilizables** → `src/`
- **Scripts ejecutables** → `scripts/`
- **Pipelines complejos** → `pipeline/`
- **Documentación** → `memory-bank/`
- **Datos** → `datasets/`
- **Resultados** → `outputs/`


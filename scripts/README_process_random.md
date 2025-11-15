# Script: Procesar Muestras Aleatorias

Este script descarga el dataset FOLIO, selecciona registros aleatorios y genera análisis completos.

## Uso

```bash
# Procesar 3 registros aleatorios (default)
python scripts/process_random_samples.py

# Procesar 5 registros
python scripts/process_random_samples.py --num-samples 5

# Especificar directorio de salida
python scripts/process_random_samples.py --output-dir resultados

# Usar seed para reproducibilidad
python scripts/process_random_samples.py --seed 42
```

## Qué Hace

1. **Descarga** el dataset FOLIO desde HuggingFace
2. **Selecciona** N registros aleatorios (default: 3)
3. **Para cada registro:**
   - Parsea las premisas y conclusión usando el módulo Lark
   - Calcula métricas del AST
   - Genera archivos JSON y SVG
   - Crea un PDF con toda la información

## Archivos Generados

Para cada registro `{id_registro}`:

- `registro_{id_registro}.json` - AST y métricas en JSON
- `registro_{id_registro}.svg` - Visualización del árbol AST
- `{id_registro}.pdf` - **Reporte completo** con:
  - ID del registro
  - Premisas (lista numerada)
  - Conclusión
  - Imagen del árbol AST (SVG convertido)
  - JSON completo con métricas

## Requisitos

```bash
pip install reportlab pillow cairosvg
```

O instalar todas las dependencias:

```bash
pip install -r requirements.txt
```

## Ejemplo de Salida

```
================================================================================
Procesamiento de Muestras Aleatorias - Dataset FOLIO
================================================================================

1. Descargando dataset FOLIO...
✓ Dataset descargado: 1001 registros

2. Seleccionando 3 registros aleatorios...
✓ Registros seleccionados: [42, 156, 789]

3. Procesando registros...
============================================================
Procesando registro 42 (ID: 1126)
============================================================
Premisas: 3
Conclusión: ¬WantToBeAddictedTo(rina, caffeine)...
Parseando fórmula...
✓ AST creado: IMPLIES
Calculando métricas...
✓ Métricas calculadas
  - Profundidad: 6
  - Subfórmulas: 9
  - Cuantificadores: 2
Exportando JSON y SVG...
✓ JSON: outputs/registro_1126.json
✓ SVG: outputs/registro_1126.svg
Generando PDF...
✓ PDF generado: outputs/1126.pdf
```

## Notas

- El script usa `premises-FOL` y `conclusion-FOL` del dataset
- Si no están disponibles, intenta con `premises` y `conclusion`
- El ID del registro se toma de `example_id` o `story_id`
- Los PDFs incluyen toda la información para investigación


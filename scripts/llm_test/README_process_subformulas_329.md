# Procesamiento Completo de Subfórmulas - Ejemplo 329

Este script procesa **TODAS** las subfórmulas del ejemplo 329, las alinea con texto natural usando LLM, y genera un PDF completo con el análisis.

## Características

- ✅ Procesa **TODAS** las subfórmulas (no solo una muestra)
- ✅ Genera PDF con estructura ordenada:
  1. Forma natural
  2. Forma FOL
  3. Imagen del árbol AST
  4. Análisis de LLM por subfórmula (FOL, texto natural, razonamiento)
- ✅ Guarda resultados en JSON para análisis posterior
- ✅ Soporta modelos gratuitos (DeepSeek-R1, Qwen)

## Uso

### Con modelo GRATUITO (recomendado)
```bash
# Usar DeepSeek-R1 (GRATIS)
python scripts/process_subformulas_329.py --model deepseek-r1

# Usar Qwen (GRATIS)
python scripts/process_subformulas_329.py --model qwen

# Usar GLM-4.5-air con thinking habilitado (GRATIS)
python scripts/process_subformulas_329.py --model glm-4.5-air
```

### Con modelo de pago
```bash
# OpenRouter con modelo específico
python scripts/process_subformulas_329.py --model "openai/gpt-4o-mini"

# OpenAI directo
python scripts/process_subformulas_329.py --provider openai --model "gpt-4o-mini"
```

## Estructura del PDF Generado

El PDF sigue este orden:

### 1. Forma Natural
- Premisas en texto natural
- Conclusión en texto natural

### 2. Forma FOL
- Premisas en formato FOL
- Conclusión en formato FOL

### 3. Árbol Sintáctico (AST)
- Visualización del árbol completo
- Generado desde SVG/PNG

### 4. Análisis de LLM por Subfórmula
Para cada subfórmula muestra:
- **Subfórmula FOL**: La fórmula en formato FOL
- **Subfórmula en Texto Natural**: El span encontrado en el texto
- **Razonamiento de la LLM**: Explicación de por qué ese span corresponde

## Archivos Generados

```
outputs/random_test/329/
├── registro_329_subformulas_complete.pdf  # PDF con análisis completo
├── subformula_alignment_complete.json     # JSON con todos los resultados
├── registro_329_complete.json             # JSON con AST y métricas
└── registro_329_complete.svg              # SVG del árbol AST
```

## Tiempo de Ejecución

- **Con modelo gratuito**: ~5-15 minutos (depende del número de subfórmulas)
- **Con modelo de pago**: ~2-5 minutos (más rápido)

El ejemplo 329 tiene aproximadamente **20 subfórmulas**, así que el procesamiento completo puede tomar varios minutos.

## Ejemplo de Salida

```
PROCESAMIENTO COMPLETO DE SUBFÓRMULAS - Ejemplo 329
================================================================================
Proveedor: openrouter
Modelo: deepseek-r1 (GRATIS ✅)

1. Cargando dataset FOLIO...
✓ Dataset descargado: 1000 registros

2. Parseando fórmulas FOL...
✓ AST parseado correctamente

3. Extrayendo TODAS las subfórmulas del AST...
✓ Encontradas 20 subfórmulas

4. Generando archivos de análisis (SVG, JSON)...
✓ Archivos generados

5. Procesando alineación con LLM para TODAS las subfórmulas...
   [1/20] Procesando subfórmula tipo IMPLIES... ✓ Encontrado
   [2/20] Procesando subfórmula tipo AND... ⚠ No encontrado
   ...

6. Guardando resultados JSON...
✓ Resultados guardados

7. Generando PDF con análisis completo...
✓ PDF generado

RESUMEN
================================================================================
Total de subfórmulas procesadas: 20
✓ Exitosas: 18
✓ Con span encontrado: 15
❌ Fallidas: 2
Confianza promedio: 0.87
```

## Notas

- El script requiere que tengas configurada la API key en `.env`
- Si no tienes API key, el PDF se generará sin análisis de LLM
- Los resultados se guardan incrementalmente en JSON
- El PDF puede ser grande si hay muchas subfórmulas

## Próximos Pasos

1. Ejecutar el script con modelo gratuito para validar
2. Revisar el PDF generado
3. Si los resultados son buenos, escalar a más ejemplos
4. Analizar el JSON para métricas agregadas


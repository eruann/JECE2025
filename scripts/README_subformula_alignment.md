# Alineación de Subfórmulas FOL con Texto Natural

Este módulo permite identificar qué segmentos del texto natural corresponden a subfórmulas específicas del AST FOL usando LLMs.

## Instalación

```bash
pip install openai requests
```

## Configuración

### 1. Verificar configuración (recomendado primero)
```bash
python scripts/check_llm_setup.py
```

Este script te mostrará:
- Si tienes las API keys configuradas
- Qué modelos gratuitos están disponibles
- Ejemplos de uso

### 2. Agregar API key al archivo `.env`:

**Opción 1: OpenRouter (Recomendado - modelos GRATUITOS disponibles)**
```bash
OPENROUTER_API_KEY=tu_api_key_aqui
```
Obtén tu key gratis en: https://openrouter.ai/keys

**Opción 2: OpenAI Directo**
```bash
OPENAI_API_KEY=tu_api_key_aqui
```

## Uso Rápido - Ejemplo 329

### Paso 1: Verificar configuración
```bash
python scripts/check_llm_setup.py
```

### Paso 2: Ejecutar prueba con modelo GRATUITO (recomendado)
```bash
# Usar DeepSeek-R1 (GRATIS)
python scripts/test_subformula_alignment_329.py --model deepseek-r1

# O usar Qwen (GRATIS)
python scripts/test_subformula_alignment_329.py --model qwen
```

### Con OpenRouter (default, modelo de pago)
```bash
python scripts/test_subformula_alignment_329.py
```

### Con OpenAI
```bash
python scripts/test_subformula_alignment_329.py --provider openai
```

### Especificar modelo específico
```bash
# Modelos GRATUITOS en OpenRouter (recomendado para empezar)
python scripts/test_subformula_alignment_329.py --model deepseek-r1
python scripts/test_subformula_alignment_329.py --model qwen

# OpenRouter con modelo de pago
python scripts/test_subformula_alignment_329.py --model "anthropic/claude-3-haiku"

# OpenAI con modelo específico
python scripts/test_subformula_alignment_329.py --provider openai --model "gpt-4"
```

### Limitar número de subfórmulas a probar (para ahorrar costos)
```bash
python scripts/test_subformula_alignment_329.py --max-subformulas 3
```

## Modelos Disponibles

### OpenRouter - Modelos GRATUITOS (Recomendado para pruebas)
- `deepseek-r1` o `deepseek/deepseek-r1` - **GRATIS** ✅ (reasoning integrado por defecto)
- `qwen` o `qwen/qwen-2.5-72b-instruct` - **GRATIS** ✅
- `deepseek-chat` o `deepseek/deepseek-chat` - **GRATIS** ✅
- `glm-4.5-air` o `z-ai/glm-4.5-air:free` - **GRATIS** ✅ (con thinking.type=enabled habilitado automáticamente)

**Uso de modelos gratuitos:**
```bash
# Usar DeepSeek-R1 (gratis)
python scripts/test_subformula_alignment_329.py --model deepseek-r1

# Usar Qwen (gratis)
python scripts/test_subformula_alignment_329.py --model qwen

# Usar GLM-4.5-air con thinking habilitado (gratis)
python scripts/test_subformula_alignment_329.py --model glm-4.5-air
```

### OpenRouter - Modelos de Pago (más precisos pero con costo)
- `openai/gpt-4o-mini` (default, ~$0.15 por 1000 subfórmulas)
- `openai/gpt-4o`
- `openai/gpt-4-turbo`
- `anthropic/claude-3-haiku` (muy económico, ~$0.08 por 1000)
- `anthropic/claude-3-sonnet`
- `anthropic/claude-3-opus`
- Ver más en: https://openrouter.ai/models

### OpenAI Directo
- `gpt-4o-mini` (default)
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-4`

## Resultados

Los resultados se guardan en:
```
outputs/random_test/329/subformula_alignment_test.json
```

El archivo contiene:
- Información del ejemplo (premisas y conclusiones en texto natural y FOL)
- Todas las subfórmulas extraídas del AST
- Resultados de alineación para cada subfórmula probada
- Spans identificados en el texto natural
- Niveles de confianza

## Estructura del Código

- `src/subformula_alignment.py`: Módulo principal con funciones de alineación
- `scripts/test_subformula_alignment_329.py`: Script de prueba con ejemplo 329

## Funciones Principales

### `extract_all_subformulas(ast)`
Extrae todas las subfórmulas del AST y las convierte a strings FOL.

### `align_subformula(subformula_fol, natural_premises, natural_conclusion, provider, model)`
Usa una LLM para encontrar el span correspondiente en el texto natural.

## Costos Estimados

### Modelos GRATUITOS ✅
- `deepseek-r1`: **$0.00** - Gratis para uso razonable (reasoning integrado por defecto, no requiere parámetro adicional)
- `qwen`: **$0.00** - Gratis para uso razonable
- `deepseek-chat`: **$0.00** - Gratis para uso razonable
- `glm-4.5-air`: **$0.00** - Gratis para uso razonable (con `thinking.type=enabled` habilitado automáticamente)

**Nota:** DeepSeek-R1 tiene reasoning integrado por defecto y no requiere el parámetro `thinking`. GLM-4.5-air requiere `thinking.type=enabled` que se agrega automáticamente.

**Recomendación:** Empieza con estos modelos gratuitos para validar el concepto antes de usar modelos de pago. Ambos modelos con reasoning (`deepseek-r1` y `glm-4.5-air`) pueden mejorar la calidad del razonamiento.

### Modelos de Pago

### OpenRouter (gpt-4o-mini)
- ~$0.15 por 1000 subfórmulas
- ~$0.00015 por subfórmula

### OpenAI (gpt-4o-mini)
- Similar a OpenRouter

### OpenRouter (claude-3-haiku)
- ~$0.08 por 1000 subfórmulas
- Más económico pero ligeramente menos preciso

## Próximos Pasos

1. Probar con ejemplo 329 (5 subfórmulas)
2. Validar resultados manualmente
3. Escalar a más ejemplos si los resultados son buenos
4. Crear script batch para procesar todo el dataset


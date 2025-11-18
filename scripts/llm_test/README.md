# LLM Test - Alineación de Subfórmulas FOL

Esta carpeta contiene todos los scripts y documentación relacionados con el uso de LLMs para alinear subfórmulas FOL con texto natural.

## Archivos

- **`test_subformula_alignment_329.py`** - Prueba rápida con el ejemplo 329 (primeras N subfórmulas)
- **`process_subformulas_329.py`** - Procesamiento completo de TODAS las subfórmulas del ejemplo 329 y generación de PDF
- **`check_llm_setup.py`** - Script de verificación de configuración de LLMs
- **`README_subformula_alignment.md`** - Documentación detallada de alineación de subfórmulas
- **`README_process_subformulas_329.md`** - Documentación del procesamiento completo

## Uso Rápido

### Verificar configuración
```bash
python scripts/llm_test/check_llm_setup.py
```

### Probar con ejemplo 329 (primeras 5 subfórmulas)
```bash
python scripts/llm_test/test_subformula_alignment_329.py --model deepseek-r1
```

### Procesar TODAS las subfórmulas del 329
```bash
python scripts/llm_test/process_subformulas_329.py --model deepseek-r1 --reasoning-effort medium
```

## Modelos Disponibles

### Modelos GRATUITOS con reasoning
- `deepseek-r1` - Reasoning integrado
- `glm-4.5-air` - Con reasoning habilitado automáticamente
- `kimi-vl-a3b-thinking` - Con reasoning habilitado automáticamente

### Otros modelos gratuitos
- `qwen` - Qwen 2.5 72B
- `deepseek-chat` - DeepSeek Chat

## Módulo Principal

El módulo principal `subformula_alignment.py` está en `src/` y puede ser importado desde cualquier script:

```python
from subformula_alignment import align_subformula, extract_all_subformulas
```

## Ver Documentación Completa

- [README_subformula_alignment.md](README_subformula_alignment.md) - Guía completa de uso
- [README_process_subformulas_329.md](README_process_subformulas_329.md) - Procesamiento completo


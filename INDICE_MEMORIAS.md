# Índice de Memorias del Proyecto

Este documento sirve como índice y guía de navegación para todas las memorias del proyecto.

## Archivos de Memoria Creados

### 1. [MEMORIA_TECNICA.md](MEMORIA_TECNICA.md)
**Contenido:** Documentación técnica completa del proyecto
- Arquitectura del sistema
- Módulos principales y sus responsabilidades
- Decisiones de diseño clave
- Estado actual del código
- Funcionalidades completadas
- Consideraciones futuras

**Útil para:** Entender la estructura técnica del proyecto

---

### 2. [MEMORIA_DECISIONES.md](MEMORIA_DECISIONES.md)
**Contenido:** Registro de decisiones importantes tomadas durante el desarrollo
- Elección del parser (Lark vs alternativas)
- Solución para AND largos
- Estructura del AST
- Manejo de XOR
- Exportación SVG opcional
- Modularidad del código

**Útil para:** Entender por qué se tomaron ciertas decisiones y qué alternativas se consideraron

---

### 3. [MEMORIA_PROBLEMAS_RESUELTOS.md](MEMORIA_PROBLEMAS_RESUELTOS.md)
**Contenido:** Documentación detallada de problemas encontrados y sus soluciones
- Reglas duplicadas en gramática Lark
- Objetos Tree sin transformar
- Wrappers OR/AND innecesarios
- Pérdida de premisas en AND largos
- Graphviz no instalado
- Preservación de NOT y FORALL

**Útil para:** Entender problemas técnicos específicos y cómo se resolvieron

---

## Documentación Adicional

### [README.md](README.md)
Guía de usuario con ejemplos de uso y documentación de la API.

### [ALTERNATIVAS_PARSER.md](ALTERNATIVAS_PARSER.md)
Análisis de alternativas a Lark consideradas durante el desarrollo.

### [example_usage.py](example_usage.py)
Ejemplos prácticos de código mostrando cómo usar los módulos.

---

## Navegación Rápida

### ¿Quieres entender la arquitectura?
→ Lee [MEMORIA_TECNICA.md](MEMORIA_TECNICA.md)

### ¿Quieres saber por qué se hizo algo de cierta manera?
→ Lee [MEMORIA_DECISIONES.md](MEMORIA_DECISIONES.md)

### ¿Encontraste un problema similar a uno ya resuelto?
→ Lee [MEMORIA_PROBLEMAS_RESUELTOS.md](MEMORIA_PROBLEMAS_RESUELTOS.md)

### ¿Quieres usar el código?
→ Lee [README.md](README.md) y [example_usage.py](example_usage.py)

### ¿Estás considerando cambiar el parser?
→ Lee [ALTERNATIVAS_PARSER.md](ALTERNATIVAS_PARSER.md)

---

## Resumen Ejecutivo

**Proyecto:** Parser FOL para Dataset FOLIO

**Estado:** ✅ Completado y funcional

**Tecnologías Principales:**
- Lark (parser)
- Python 3.11+
- Graphviz (opcional, para visualizaciones)

**Solución Clave:** Parsear premisas individualmente y combinar ASTs manualmente para evitar problemas con AND largos.

**Archivos Principales:**
- `fol_parser.py` - Parser FOL
- `build_conditionals.py` - Construcción de condicionales
- `metrics.py` - Cálculo de métricas
- `serialize.py` - Exportación

**Próximos Pasos Sugeridos:**
1. Probar con dataset completo de FOLIO
2. Optimizar para datasets grandes si es necesario
3. Agregar más validación según necesidades
4. Mejorar visualizaciones SVG

---

**Última Actualización:** Noviembre 2025


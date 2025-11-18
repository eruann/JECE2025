"""
Script de ayuda para verificar la configuración de LLMs y mostrar modelos disponibles.
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("VERIFICACIÓN DE CONFIGURACIÓN LLM")
print("=" * 80)

# Verificar OpenRouter
print("\n1. OpenRouter:")
openrouter_key = os.getenv('OPENROUTER_API_KEY')
if openrouter_key:
    print("   ✓ OPENROUTER_API_KEY configurada")
    if openrouter_key.startswith('sk-'):
        print(f"   ✓ Formato de key válido (longitud: {len(openrouter_key)})")
    else:
        print("   ⚠ Formato de key puede ser incorrecto (debería empezar con 'sk-')")
else:
    print("   ❌ OPENROUTER_API_KEY NO configurada")
    print("   📝 Agrega a .env: OPENROUTER_API_KEY=tu_key_aqui")
    print("   📝 Obtén tu key en: https://openrouter.ai/keys")

# Verificar OpenAI
print("\n2. OpenAI:")
openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    print("   ✓ OPENAI_API_KEY configurada")
    if openai_key.startswith('sk-'):
        print(f"   ✓ Formato de key válido (longitud: {len(openai_key)})")
    else:
        print("   ⚠ Formato de key puede ser incorrecto")
else:
    print("   ⚠ OPENAI_API_KEY NO configurada (opcional si usas OpenRouter)")

# Modelos gratuitos disponibles
print("\n3. Modelos GRATUITOS disponibles en OpenRouter:")
print("   ✓ deepseek-r1 (deepseek/deepseek-r1)")
print("   ✓ qwen (qwen/qwen-2.5-72b-instruct)")
print("   ✓ deepseek-chat (deepseek/deepseek-chat)")
print("\n   💡 Estos modelos son GRATIS para uso razonable")
print("   💡 Úsalos con: --model deepseek-r1 o --model qwen")

# Ejemplos de uso
print("\n4. Ejemplos de uso:")
print("\n   # Probar con modelo GRATUITO (DeepSeek-R1):")
print("   python scripts/llm_test/test_subformula_alignment_329.py --model deepseek-r1")
print("\n   # Probar con modelo GRATUITO (Qwen):")
print("   python scripts/llm_test/test_subformula_alignment_329.py --model qwen")
print("\n   # Probar con modelo de pago (gpt-4o-mini):")
print("   python scripts/llm_test/test_subformula_alignment_329.py --model openai/gpt-4o-mini")

# Verificar dependencias
print("\n5. Dependencias Python:")
try:
    import requests
    print("   ✓ requests instalado")
except ImportError:
    print("   ❌ requests NO instalado")
    print("   📝 Instala con: pip install requests")

try:
    import openai
    print("   ✓ openai instalado")
except ImportError:
    print("   ⚠ openai NO instalado (opcional si solo usas OpenRouter)")
    print("   📝 Instala con: pip install openai")

print("\n" + "=" * 80)
print("RECOMENDACIÓN:")
if openrouter_key:
    print("✅ Todo listo! Puedes ejecutar la prueba con modelos gratuitos:")
    print("   python scripts/llm_test/test_subformula_alignment_329.py --model deepseek-r1")
else:
    print("⚠ Configura OPENROUTER_API_KEY en .env para empezar")
    print("   Obtén tu key gratis en: https://openrouter.ai/keys")
print("=" * 80)


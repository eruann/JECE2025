"""
Script helper para verificar que el entorno está configurado correctamente.
"""

import sys
from pathlib import Path

def check_environment():
    """Verifica que todas las dependencias y configuraciones estén correctas."""
    print("Verificando entorno...")
    print("=" * 60)
    
    issues = []
    
    # 1. Verificar Python
    print(f"Python: {sys.version}")
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ requerido")
    else:
        print("✓ Versión de Python OK")
    
    # 2. Verificar dependencias
    print("\nVerificando dependencias:")
    dependencies = {
        'lark': 'Lark parser',
        'datasets': 'HuggingFace datasets',
        'dotenv': 'python-dotenv',
        'graphviz': 'Graphviz (opcional)'
    }
    
    for module, name in dependencies.items():
        try:
            if module == 'dotenv':
                import dotenv
            elif module == 'graphviz':
                import graphviz
                # Verificar que el ejecutable esté disponible
                try:
                    import subprocess
                    subprocess.run(['dot', '-V'], capture_output=True, check=True)
                    print(f"  ✓ {name}: Instalado y disponible")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print(f"  ⚠ {name}: Instalado pero ejecutable 'dot' no encontrado")
                    print("     Instalar con: sudo apt-get install graphviz")
            else:
                __import__(module)
                print(f"  ✓ {name}: Instalado")
        except ImportError:
            print(f"  ✗ {name}: NO instalado")
            issues.append(f"Instalar {name}: pip install {module}")
    
    # 3. Verificar estructura del proyecto
    print("\nVerificando estructura del proyecto:")
    project_root = Path(__file__).parent.parent.parent
    required_dirs = ['src', 'scripts', 'tests', 'pipeline', 'memory-bank']
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/ existe")
        else:
            print(f"  ✗ {dir_name}/ NO existe")
            issues.append(f"Crear directorio {dir_name}/")
    
    # 4. Verificar módulos src
    print("\nVerificando módulos en src/:")
    src_path = project_root / 'src'
    required_modules = [
        'fol_parser.py',
        'build_conditionals.py',
        'metrics.py',
        'serialize.py',
        'download_folio.py'
    ]
    
    for module in required_modules:
        module_path = src_path / module
        if module_path.exists():
            print(f"  ✓ {module}")
        else:
            print(f"  ✗ {module} NO encontrado")
            issues.append(f"Módulo {module} faltante")
    
    # 5. Verificar .env
    print("\nVerificando configuración:")
    env_path = project_root / '.env'
    if env_path.exists():
        print("  ✓ .env existe")
        # Verificar que tenga HF_TOKEN
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv(env_path)
            token = os.getenv('HF_TOKEN')
            if token and token != 'your_huggingface_token_here':
                print("  ✓ HF_TOKEN configurado")
            else:
                print("  ⚠ HF_TOKEN no configurado o es placeholder")
                issues.append("Configurar HF_TOKEN en .env")
        except Exception as e:
            print(f"  ⚠ Error leyendo .env: {e}")
    else:
        print("  ⚠ .env NO existe (crear con HF_TOKEN)")
        issues.append("Crear archivo .env con HF_TOKEN")
    
    # Resumen
    print("\n" + "=" * 60)
    if issues:
        print("⚠ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ Entorno verificado correctamente")
        return True


if __name__ == '__main__':
    success = check_environment()
    sys.exit(0 if success else 1)


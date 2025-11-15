"""
Setup script OPCIONAL para instalar los módulos como paquete Python.

NOTA: Los módulos en src/ son archivos simples que se pueden usar directamente
sin instalación. Este setup.py es opcional y solo útil si quieres instalar
el paquete en otros proyectos.

Si prefieres usar los módulos directamente (recomendado para desarrollo):
    - Simplemente agrega src/ al path en tus scripts
    - No necesitas ejecutar pip install

Instalación opcional:
    pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Leer requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = [
        'lark>=1.0.0',
        'datasets>=2.14.0',
        'python-dotenv>=1.0.0',
        'graphviz>=0.20.1',
    ]

setup(
    name="folio-fol-parser",
    version="0.1.0",
    description="Parser de fórmulas de Lógica de Primer Orden (FOL) para el dataset FOLIO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matias Rodriguez",
    author_email="",
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="first-order-logic fol parser folio dataset",
)


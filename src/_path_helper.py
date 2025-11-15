"""
Helper para agregar src/ al path de Python.

Útil para scripts que necesitan importar módulos desde src/ sin instalar el paquete.
"""

import sys
from pathlib import Path


def add_src_to_path():
    """
    Agrega el directorio src/ al sys.path para permitir imports directos.
    
    Uso:
        from src._path_helper import add_src_to_path
        add_src_to_path()
        
        from fol_parser import FOLParser
    """
    # Obtener el directorio src/ (donde está este archivo)
    src_dir = Path(__file__).parent
    
    # Agregar al path si no está ya
    src_dir_str = str(src_dir)
    if src_dir_str not in sys.path:
        sys.path.insert(0, src_dir_str)
    
    return src_dir_str


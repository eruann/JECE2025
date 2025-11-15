"""
Helper común para importar módulos desde src/.

Úsalo al inicio de cualquier script para importar los módulos fácilmente.
"""

import sys
from pathlib import Path


def setup_imports():
    """
    Configura el path para importar módulos desde src/.
    
    Uso en scripts:
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / 'src'))
        
        from fol_parser import FOLParser
        from build_conditionals import parse_global_conditional
    
    O simplemente copia estas líneas al inicio de tu script:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
    """
    # Obtener el directorio raíz del proyecto
    # Este archivo está en scripts/, así que subimos dos niveles
    script_dir = Path(__file__).parent.parent
    src_dir = script_dir / 'src'
    
    # Agregar src/ al path si no está ya
    src_dir_str = str(src_dir)
    if src_dir_str not in sys.path:
        sys.path.insert(0, src_dir_str)
    
    return src_dir


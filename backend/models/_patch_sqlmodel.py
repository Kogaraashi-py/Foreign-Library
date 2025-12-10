"""
Parche para SQLModel: corrige la extracción del argumento de relaciones.
Este parche limpia comillas extra y corrige List["Model"] -> "Model"
"""
import sqlmodel
from sqlalchemy.orm import relationship as sa_relationship
import re

_original_get_relationship_to = sqlmodel.main.get_relationship_to

def _patched_get_relationship_to(name: str, rel_info, annotation) -> str:
    """Parche para extraer correctamente el argumento de relaciones"""
    result = _original_get_relationship_to(name, rel_info, annotation)
    
    if isinstance(result, str):
        # Limpiar comillas extra: "'Novel'" -> "Novel"
        result = result.strip("'\"")
        
        # Si es "List['Model']" o similar, extraer solo "Model"
        match = re.search(r"List\[['\"]?([^'\"]+)['\"]?\]", result)
        if match:
            return match.group(1).strip("'\"")
    
    return result

sqlmodel.main.get_relationship_to = _patched_get_relationship_to


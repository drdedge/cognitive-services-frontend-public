# backend/services/shared/field_accessor.py
"""
Universal Field Accessor
========================

Provides a simple way to access fields from objects that might be either
object attributes or dictionary keys, reducing repetitive code.
"""


def get_field(obj, field, default=None):
    """
    Universal field accessor - handles both object attributes and dict keys.
    
    Args:
        obj: The object or dict to access
        field: The field name to retrieve
        default: Default value if field not found
        
    Returns:
        The field value or default
    """
    if hasattr(obj, field):
        return getattr(obj, field, default)
    elif isinstance(obj, dict):
        return obj.get(field, default)
    return default


def get_nested_field(obj, path, default=None):
    """
    Access nested fields using dot notation.
    
    Args:
        obj: The object or dict to access
        path: Dot-separated path (e.g., "result.pages.0.words")
        default: Default value if path not found
        
    Returns:
        The nested value or default
    """
    try:
        parts = path.split('.')
        current = obj
        
        for part in parts:
            # Handle list indices
            if part.isdigit():
                current = current[int(part)]
            else:
                current = get_field(current, part)
                
            if current is None:
                return default
                
        return current
    except (KeyError, IndexError, AttributeError, TypeError):
        return default


def has_field(obj, field):
    """
    Check if an object has a field (either as attribute or dict key).
    
    Args:
        obj: The object or dict to check
        field: The field name to check
        
    Returns:
        bool: True if field exists
    """
    if hasattr(obj, field):
        return True
    elif isinstance(obj, dict):
        return field in obj
    return False
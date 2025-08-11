"""Utility functions

This module provides essential helper functions for:
- Generating visual elements (colors)
- Safe conversion of user input to physical parameters
- Data validation for physics simulation
"""

import random


def random_color():
    """Generate a visually distinct RGB color for celestial objects"""
    return (random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255))


def safe_float_convert(text, default, min_val, max_val):
    """Safely convert user input to validated float within physical bounds
    
    Args:
        text (str): Input string to convert (typically from UI elements)
        default (float): Fallback value if conversion fails
        min_val (float): Minimum allowed value (physics boundary)
        max_val (float): Maximum allowed value (physics boundary)
    
    Returns:
        float: Validated float value within [min_val, max_val] range
    
    Example:
        >>> safe_float_convert("100", 10, 1, 1000)
        100.0
        >>> safe_float_convert("abc", 10, 1, 1000)
        10.0
        >>> safe_float_convert("5000", 10, 1, 1000)
        1000.0
    """
    try:
        value = float(text) if text else default
        return max(min_val, min(max_val, value))
    except ValueError:
        return default

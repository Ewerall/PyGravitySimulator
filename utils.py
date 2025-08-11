"""Utility functions for gravitational physics simulation

This module provides essential helper functions for:
- Generating visual elements (colors)
- Safe conversion of user input to physical parameters
- Data validation for physics simulation

These utilities bridge the gap between UI components and physical models,
ensuring robust handling of user input and visual representation of celestial bodies.

Note: All functions are designed to be physics-aware with appropriate
bounds checking and error handling.
"""

import random


def random_color():
    """Generate a visually distinct RGB color for celestial bodies
    
    Returns a random color tuple with values starting from 50 to ensure
    sufficient brightness for visibility against dark background.
    
    The color generation avoids:
    - Very dark colors (which would blend with space background)
    - Pure black/white (for better visual distinction)
    
    Returns:
        tuple: RGB color values (r, g, b) where each is between 50-255
        
    Physics relevance:
        Used to visually differentiate celestial bodies in the simulation
        while maintaining good contrast against the space-like background.
    """
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
    
    Physics relevance:
        Critical for converting user input (mass, radius) to valid physical
        parameters with appropriate bounds checking to prevent simulation instability.
    """
    try:
        value = float(text) if text else default
        return max(min_val, min(max_val, value))
    except ValueError:
        return default

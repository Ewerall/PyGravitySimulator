import random
from config import *

def random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def safe_float_convert(text, default, min_val, max_val):
    try:
        value = float(text) if text else default
        return max(min_val, min(max_val, value))
    except ValueError:
        return default
"""Celestial objects module for N-body gravitational simulation

This module defines the core class for celestial bodies in a 2D gravitational simulation.
Each object follows Newtonian physics with position, velocity, and mass properties.

Key physics concepts:
- Position (x, y): Screen coordinates in pixels
- Velocity (vx, vy): Pixels per second
- Mass: Arbitrary units (affects gravitational pull)
- Radius: Visual representation size (not used in physics calculations)

Note: Forces (fx, fy) are calculated dynamically during simulation and not stored.
"""

import uuid
from typing import Optional, Tuple, List, Any

import pygame
from gravity_simulator.utils import random_color


class Object():
    """Represents a celestial body in 2D gravitational simulation
    
    Physics model:
        Position: (x, y) in screen coordinates (pixels)
        Velocity: (vx, vy) in pixels/second
        Mass: Arbitrary units affecting gravitational force (F = G·m₁·m₂/r²)
        Radius: Visual size (does not affect physics)
    
    Attributes:
        x, y: Current position
        vx, vy: Current velocity components
        mass: Gravitational mass
        radius: Visual radius in pixels
        color: RGB tuple for rendering
        active: Whether the body is participating in simulation
        id: Unique identifier (UUID)
    
    Note: Forces are calculated dynamically during physics updates
    """
    def __init__(self, x: float, y: float, mass: float, radius: float, **kwargs: Any) -> None:
        self.x: float = x
        self.y: float = y
        self.mass: float = mass
        self.radius: float = radius
        self.vx: float = kwargs.get('vx', 0)
        self.vy: float = kwargs.get('vy', 0)
        self.color: Tuple[int, int, int] = kwargs.get('color') or random_color()
        self.active: bool = True
        self.id: uuid.UUID = uuid.uuid4()
        self.trail: List[Tuple[float, float]] = []
        self.max_trail_length: int = kwargs.get('max_trail_length', 100)
        self.base_image: Optional[pygame.Surface] = kwargs.get('base_image', None)

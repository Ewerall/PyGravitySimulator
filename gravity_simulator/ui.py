"""UI components for the gravity simulator.

This module contains user interface elements including:
- Mouse interaction utilities
- Grid drawing functions
- Input box widget for parameter editing
"""

import math
from typing import List, Tuple, Optional, Any

import pygame


def find_object_under_mouse(mouse_x: float, mouse_y: float, particles: List[Any],
                            detection_radius: float = 20) -> Optional[Any]:
    """Find the particle under the mouse cursor.
    
    Args:
        mouse_x: X coordinate of mouse position
        mouse_y: Y coordinate of mouse position
        particles: List of particles to check
        detection_radius: Additional radius for detection sensitivity
        
    Returns:
        Particle object if found under mouse, None otherwise
    """
    for particle in particles:
        if particle.active:
            dx = particle.x - mouse_x
            dy = particle.y - mouse_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= particle.radius + detection_radius:
                return particle
    return None


def draw_grid(screen: pygame.Surface, grid_size: int = 50,
              grid_color: Tuple[int, int, int] = (50, 50, 50)) -> None:
    """Draw a grid on the screen"""
    width, height = screen.get_size()

    for x in range(0, width, grid_size):
        pygame.draw.line(screen, grid_color, (x, 0), (x, height))

    for y in range(0, height, grid_size):
        pygame.draw.line(screen, grid_color, (0, y), (width, y))


class InputBox:
    """Input box widget for text input in pygame applications"""

    def __init__(self, position: Tuple[int, int], size: Tuple[int, int], **kwargs: Any) -> None:
        """Create an input box for physics parameters
        
        Args:
            position: (x, y) tuple for screen position
            size: (width, height) tuple for dimensions
            text: Initial text value (default: '')
            font: Custom font (uses default if None)
            color_active: Color when active (default: 'green')
            color_inactive: Color when inactive (default: 'white')
        """
        x, y = position
        width, height = size
        self.rect = pygame.Rect(x, y, width, height)
        self.text: str = kwargs.get('text', '')
        self.font: pygame.font.Font = kwargs.get('font', pygame.font.Font(None, 32))
        self.color_active: pygame.Color = pygame.Color(kwargs.get('color_active', 'green'))
        self.color_inactive: pygame.Color = pygame.Color(kwargs.get('color_inactive', 'white'))
        self.active: bool = False
        self.color: pygame.Color = self.color_inactive
        self.txt_surface: pygame.Surface = self.font.render(self.text, True, self.color)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events for the input box"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('green') if self.active else pygame.Color('white')

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = pygame.Color('white')
                    self.update()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self) -> None:
        """Update the input box dimensions based on text content"""
        width = max(100, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the input box on the screen"""
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def is_hovered(self, pos: Tuple[int, int]) -> bool:
        """Check if the input box is hovered by mouse"""
        return self.rect.collidepoint(pos)

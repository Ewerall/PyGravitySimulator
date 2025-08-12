"""UI components for the gravity simulator.

This module contains user interface elements including:
- Mouse interaction utilities
- Grid drawing functions
- Input box widget for parameter editing
- UI renderer for drawing various interface elements
"""

import math
from typing import List, Tuple, Optional, Any

import pygame

from gravity_simulator.objects import Object


def find_object_under_mouse(mouse_x: float, mouse_y: float, particles: List[Any],
                            detection_radius: float = 20) -> Optional[Any]:
    """Find the particle under the mouse cursor.
    
    This function checks if any active particle is within a certain distance
    from the mouse cursor position. The detection area is the particle's
    radius plus an additional detection radius.
    """
    for particle in particles:
        if particle.active:
            # Calculate Euclidean distance between mouse and particle center
            dx = particle.x - mouse_x
            dy = particle.y - mouse_y
            distance = math.sqrt(dx * dx + dy * dy)

            # Check if mouse is within particle's influence area
            if distance <= particle.radius + detection_radius:
                return particle
    return None


def draw_grid(screen: pygame.Surface, grid_size: int = 50,
              grid_color: Tuple[int, int, int] = (50, 50, 50)) -> None:
    """Draw a grid on the screen for visual reference"""
    width, height = screen.get_size()

    # Draw vertical grid lines
    for x in range(0, width, grid_size):
        pygame.draw.line(screen, grid_color, (x, 0), (x, height))

    # Draw horizontal grid lines
    for y in range(0, height, grid_size):
        pygame.draw.line(screen, grid_color, (0, y), (width, y))


def draw_background(surface: pygame.Surface, background: Optional[pygame.Surface],
                    background_offset_x: int, background_offset_y: int) -> None:
    """Draw background image centered on the screen"""
    if background:
        # Draw background image at calculated offset position
        surface.blit(background, (background_offset_x, background_offset_y))
    else:
        # Fill with black if no background image is available
        surface.fill((0, 0, 0))


class UIRenderer:
    """Handles rendering of all UI elements for the gravity simulator.
    
    This class encapsulates all the drawing logic for UI components
    like information panels, labels, and hotkey guides. It uses
    screen dimensions to properly position elements.
    """

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """Initialize the UI renderer with screen dimensions"""
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw_object_info(self, surface: pygame.Surface, hovered: Optional[Object],
                         text_font: pygame.font.Font) -> None:
        """Render information panel for the hovered celestial body"""
        if hovered:
            # Prepare information text lines
            info_text = [
                f"Mass: {hovered.mass:.1f}",
                f"Radius: {hovered.radius:.1f}",
                f"Pos: ({hovered.x:.1f}, {hovered.y:.1f})",
                f"Speed(X,Y): ({hovered.vx:.1f}, {hovered.vy:.1f})",
                f"Speed: {math.sqrt(hovered.vx**2 + hovered.vy**2):.1f}",
                f"ID: {str(hovered.id)[:8]}..."
            ]

            # Calculate panel dimensions based on text content
            text_height = len(info_text) * 25 + 10

            # Draw panel background and border
            pygame.draw.rect(surface, (0, 0, 0), (10, 10, 300, text_height))
            pygame.draw.rect(surface, (100, 100, 100),
                             (10, 10, 300, text_height), 2)

            # Render each line of text
            for i, text in enumerate(info_text):
                text_surface = text_font.render(text, True, (255, 255, 255))
                surface.blit(text_surface, (20, 20 + i * 25))

    def draw_ui_labels(self, surface: pygame.Surface, text_font: pygame.font.Font) -> None:
        """Draw UI labels for all input boxes"""
        # Create label surfaces for each input parameter
        mass_label = text_font.render("Mass:", True, (255, 255, 255))
        radius_label = text_font.render("Radius:", True, (255, 255, 255))
        g_label = text_font.render("G:", True, (255, 255, 255))
        dt_label = text_font.render("dt:", True, (255, 255, 255))

        # Position labels relative to screen edges and input boxes
        surface.blit(mass_label, (self.screen_width - 200, 15))
        surface.blit(radius_label, (self.screen_width - 211, 55))
        surface.blit(g_label, (self.screen_width - 170, 95))
        surface.blit(dt_label, (self.screen_width - 175, 135))

    def draw_hotkey_info(self, surface: pygame.Surface, text_font: pygame.font.Font) -> None:
        """Draw hotkey information panel"""
        # Define hotkey reference information
        hotkey_text = [
            "Hotkeys:",
            "Num/* : G ±10",
            "Num-/+: dt ±0.01",
            "Space: Pause",
            "Delete: Delete Object"
        ]

        # Calculate panel dimensions based on text content
        text_height = len(hotkey_text) * 20 + 10

        # Position panel at bottom-left of screen
        panel_x = 10
        panel_y = self.screen_height - 120

        # Draw panel background and border
        pygame.draw.rect(surface, (0, 0, 0), (panel_x, panel_y, 220, text_height))
        pygame.draw.rect(surface, (100, 100, 100), (panel_x, panel_y, 220, text_height), 1)

        # Render each hotkey instruction
        for i, text in enumerate(hotkey_text):
            text_surface = text_font.render(text, True, (200, 200, 200))
            surface.blit(text_surface, (15, self.screen_height - 112 + i * 20))


class InputBox:
    """Input box widget for text input in pygame applications.
    
    This class provides a reusable text input component with
    visual feedback for active/inactive states and automatic
    sizing based on content.
    """

    def __init__(self, position: Tuple[int, int], size: Tuple[int, int], **kwargs: Any) -> None:
        """Create an input box for physics parameters.
        
        Args:
            position: (x, y) tuple for screen position in pixels.
            size: (width, height) tuple for initial dimensions.
            text: Initial text value (default: '').
            font: Custom font (uses default if None).
            color_active: Color when active (default: 'green').
            color_inactive: Color when inactive (default: 'white').
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
        # Handle mouse click events for focus
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('green') if self.active else pygame.Color('white')

        # Handle keyboard events when active
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

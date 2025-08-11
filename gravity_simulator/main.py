"""Gravity Simulator - N-body physics simulation using Newtonian mechanics

This module implements a 2D gravitational simulation where celestial bodies
interact according to Newton's law of universal gravitation (F = G·m₁·m₂/r²).

Key features:
- Real-time simulation of multiple celestial bodies with gravitational interactions
- Mouse interaction to create new bodies with configurable properties
- Dynamic UI for adjusting mass and radius of new objects
- Visual trails showing object movement history
- Information panel displaying physical properties of selected objects

Physics model:
- Integration method: Euler-Cromer (semi-implicit)
- Gravitational constant: Configurable (default G=100.0)
- Time step: Configurable (default dt=0.05)
- Boundary collision handling with energy damping
- Inelastic merging of colliding bodies

Usage:
    python main.py

Controls:
    • Left click: Create a new celestial body at mouse position
    • Mass/Radius inputs: Configure properties for new bodies
    • Hover over object: View detailed physical properties
"""

import math
import random

import pygame

from gravity_simulator.physics import PhysicsEngine
from gravity_simulator.objects import Object
from gravity_simulator.ui import InputBox, draw_grid, find_object_under_mouse
from gravity_simulator.config import (SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_MASS,
                    DEFAULT_RADIUS, GRID_SIZE, GRID_COLOR)
from gravity_simulator.utils import random_color, safe_float_convert

pygame.init()

try:
    import os
    icon_path = os.path.join("resources", "icons", "gravity.png")
    if os.path.exists(icon_path):
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
except pygame.error as e:
    print(f"Failed to load icon: {e}")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Physics Simulation")
clock = pygame.time.Clock()
running = True
font = pygame.font.Font(None, 24)
input_font = pygame.font.Font(None, 32)

engine = PhysicsEngine(G=100.0, dt=0.05)

mass_input = InputBox(
    position=(SCREEN_WIDTH - 130, 10),
    size=(140, 32),
    text=str(DEFAULT_MASS)
)
radius_input = InputBox(
    position=(SCREEN_WIDTH - 130, 50),
    size=(140, 32),
    text=str(DEFAULT_RADIUS)
)


def create_object(x, y):
    """Create a new celestial body at the specified position

    Args:
        x: X coordinate in screen space
        y: Y coordinate in screen space
    """
    mass = safe_float_convert(mass_input.text, DEFAULT_MASS, 1, 10000)
    radius = safe_float_convert(radius_input.text, DEFAULT_RADIUS, 1, 100)

    new_object = Object(
        x=x,
        y=y,
        mass=mass,
        radius=radius,
        vx=random.uniform(-10, 10),
        vy=random.uniform(-10, 10)
    )

    new_object.color = random_color()

    engine.add_particle(new_object)


def draw_object_info(surface, hovered, text_font):
    """Render information panel for the hovered celestial body

    Args:
        surface: Pygame surface to draw on
        hovered: Currently hovered celestial body (or None)
        text_font: Font for rendering text
    """
    if hovered_object:
        info_text = [
            f"Mass: {hovered.mass:.1f}",
            f"Radius: {hovered.radius:.1f}",
            f"Pos: ({hovered.x:.1f}, {hovered.y:.1f})",
            f"Speed(X,Y): ({hovered.vx:.1f}, {hovered.vy:.1f})",
            f"Speed: {math.sqrt(hovered.vx**2 + hovered.vy**2):.1f}",
            f"ID: {str(hovered.id)[:8]}..."
        ]

        text_height = len(info_text) * 25 + 10
        pygame.draw.rect(surface, (0, 0, 0), (10, 10, 300, text_height))
        pygame.draw.rect(surface, (100, 100, 100),
                         (10, 10, 300, text_height), 2)

        for i, text in enumerate(info_text):
            text_surface = text_font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, (20, 20 + i * 25))


def draw_ui_labels(surface, text_font):
    """Draw UI labels for mass and radius inputs

    Args:
        surface: Pygame surface to draw on
        text_font: Font for rendering text
    """
    mass_label = text_font.render("Mass:", True, (255, 255, 255))
    radius_label = text_font.render("Radius:", True, (255, 255, 255))
    surface.blit(mass_label, (SCREEN_WIDTH - 200, 15))
    surface.blit(radius_label, (SCREEN_WIDTH - 211, 55))


while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()

    hovered_object = find_object_under_mouse(mouse_x, mouse_y,
                                             engine.particles,
                                             detection_radius=20)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        mass_input.handle_event(event)
        radius_input.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left button
                if not mass_input.is_hovered(event.pos) and not radius_input.is_hovered(event.pos):
                    create_object(mouse_x, mouse_y)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE:
                if hovered_object:
                    engine.remove_particle(hovered_object)

    engine.update()

    mass_input.update()
    radius_input.update()

    screen.fill((0, 0, 0))

    draw_grid(screen, grid_size=GRID_SIZE, grid_color=GRID_COLOR)

    for particle in engine.particles:
        if particle.active:
            pygame.draw.circle(
                screen,
                particle.color,
                (int(particle.x), int(particle.y)),
                int(particle.radius)
            )

            if hasattr(particle, 'trail') and len(particle.trail) > 1:
                pygame.draw.lines(
                    screen,
                    particle.color,
                    False,
                    [(int(x), int(y)) for x, y in particle.trail],
                    1
                )

    draw_object_info(screen, hovered_object, font)

    mass_input.draw(screen)
    radius_input.draw(screen)

    draw_ui_labels(screen, font)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

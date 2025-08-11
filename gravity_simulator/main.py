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

Controls:
    • Left click: Create a new celestial body at mouse position
    • Mass/Radius inputs: Configure properties for new bodies
    • Hover over object: View detailed physical properties
    • Hover over object + "Delete": Delete celestial body
    • Num/*: Decrease G by 10, Num/*: Increase G by 10
    • Num-: Decrease dt by 0.01, Num+: Increase dt by 0.01
    • Spacebar: Pause simulation (dt = 0)
"""

import math
import random
import os

from typing import Optional, List
import pygame

from gravity_simulator.physics import PhysicsEngine
from gravity_simulator.objects import Object
from gravity_simulator.ui import InputBox, find_object_under_mouse
from gravity_simulator.config import (SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_MASS,
                                      DEFAULT_RADIUS)
from gravity_simulator.utils import apply_color_tint, safe_float_convert


pygame.init()

icon: Optional[pygame.Surface] = None
try:
    icon_path = os.path.join("resources", "icons", "gravity.png")
    if os.path.exists(icon_path):
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
except pygame.error as e:
    print(f"Failed to load icon: {e}")


background: Optional[pygame.Surface] = None
background_offset_x: int = 0
background_offset_y: int = 0

try:
    background_path = os.path.join("resources", "background", "back1.png")
    if os.path.exists(background_path):
        background = pygame.image.load(background_path)
        bg_width, bg_height = background.get_size()
        scale_factor = max(SCREEN_WIDTH / bg_width, SCREEN_HEIGHT / bg_height)
        new_width = int(bg_width * scale_factor)
        new_height = int(bg_height * scale_factor)
        background = pygame.transform.smoothscale(background, (new_width, new_height))
        background_offset_x = (SCREEN_WIDTH - new_width) // 2
        background_offset_y = (SCREEN_HEIGHT - new_height) // 2
    else:
        print(f"Background image not found at: {background_path}")
except pygame.error as e:
    print(f"Failed to load background: {e}")


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Physics Simulation")
clock = pygame.time.Clock()
running: bool = True
font = pygame.font.Font(None, 24)
input_font = pygame.font.Font(None, 32)

engine = PhysicsEngine(G=100.0, dt=0.05)

planet_textures: List[pygame.Surface] = []
texture_names = ["ice.png", "lava.png", "moon.png", "terran.png"]

for texture_name in texture_names:
    try:
        texture_path = os.path.join("resources", "objects", texture_name)
        if os.path.exists(texture_path):
            texture = pygame.image.load(texture_path)
            texture = texture.convert_alpha()
            planet_textures.append(texture)
            print(f"Loaded texture: {texture_name}")
        else:
            print(f"Texture not found: {texture_path}")
    except pygame.error as e:
        print(f"Failed to load texture {texture_name}: {e}")

print(f"Successfully loaded {len(planet_textures)} textures")


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
g_input = InputBox(
    position=(SCREEN_WIDTH - 130, 90),
    size=(140, 32),
    text="100.0"
)
dt_input = InputBox(
    position=(SCREEN_WIDTH - 130, 130),
    size=(140, 32),
    text="0.05"
)

original_dt: float = engine.dt
is_paused: bool = False


def draw_background(surface: pygame.Surface) -> None:
    """Draw background image"""
    if background:
        surface.blit(background, (background_offset_x, background_offset_y))
    else:
        surface.fill((0, 0, 0))


def create_object(x: float, y: float) -> None:
    """Create a new celestial body at the specified position

    Args:
        x: X coordinate in screen space
        y: Y coordinate in screen space
    """
    mass = safe_float_convert(mass_input.text, DEFAULT_MASS, 1, 10000)
    radius = safe_float_convert(radius_input.text, DEFAULT_RADIUS, 1, 100)

    base_image = random.choice(planet_textures) if planet_textures else None

    new_object = Object(
        x=x,
        y=y,
        mass=mass,
        radius=radius,
        vx=random.uniform(-10, 10),
        vy=random.uniform(-10, 10),
        base_image=base_image
    )

    new_object.color = (
        random.randint(100, 255),
        random.randint(100, 255),
        random.randint(100, 255)
    )

    engine.add_particle(new_object)


def update_physics_parameters() -> None:
    """Update physics engine parameters from input boxes"""
    new_g = safe_float_convert(g_input.text, 100.0, 0.1, 10000.0)
    engine.G = new_g

    new_dt = safe_float_convert(dt_input.text, 0.05, 0.0, 1.0)
    engine.dt = new_dt


def adjust_physics_parameters(g_delta: float = 0, dt_delta: float = 0) -> None:
    """Adjust physics parameters by delta values and update input boxes
    
    Args:
        g_delta: Change in G value
        dt_delta: Change in dt value
    """
    global is_paused, original_dt

    if is_paused and dt_delta != 0:
        is_paused = False
        original_dt = engine.dt

    new_g = max(0.1, engine.G + g_delta)
    engine.G = new_g
    g_input.text = str(round(new_g, 1))

    new_dt = max(0.0, engine.dt + dt_delta)
    engine.dt = new_dt
    dt_input.text = str(round(new_dt, 3))
    if new_dt == 0.0:
        is_paused = True


def toggle_pause() -> None:
    """Toggle simulation pause state"""
    global is_paused, original_dt

    if is_paused:
        engine.dt = original_dt
        dt_input.text = str(round(original_dt, 3))
        is_paused = False
    else:
        original_dt = engine.dt
        engine.dt = 0.0
        dt_input.text = "0.0"
        is_paused = True


def draw_object_info(surface: pygame.Surface, hovered: Optional[Object],
                     text_font: pygame.font.Font) -> None:
    """Render information panel for the hovered celestial body

    Args:
        surface: Pygame surface to draw on
        hovered: Currently hovered celestial body (or None)
        text_font: Font for rendering text
    """
    if hovered:
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


def draw_ui_labels(surface: pygame.Surface, text_font: pygame.font.Font) -> None:
    """Draw UI labels for all input boxes

    Args:
        surface: Pygame surface to draw on
        text_font: Font for rendering text
    """
    mass_label = text_font.render("Mass:", True, (255, 255, 255))
    radius_label = text_font.render("Radius:", True, (255, 255, 255))
    g_label = text_font.render("G:", True, (255, 255, 255))
    dt_label = text_font.render("dt:", True, (255, 255, 255))

    surface.blit(mass_label, (SCREEN_WIDTH - 200, 15))
    surface.blit(radius_label, (SCREEN_WIDTH - 211, 55))
    surface.blit(g_label, (SCREEN_WIDTH - 180, 95))
    surface.blit(dt_label, (SCREEN_WIDTH - 185, 135))


def draw_hotkey_info(surface: pygame.Surface, text_font: pygame.font.Font) -> None:
    """Draw hotkey information panel
    
    Args:
        surface: Pygame surface to draw on
        text_font: Font for rendering text
    """
    hotkey_text = [
        "Hotkeys:",
        "Num/* : G ±10",
        "Num-/+: dt ±0.01", 
        "Space: Pause",
        "Delete: Delete Object"
    ]

    text_height = len(hotkey_text) * 20 + 10
    pygame.draw.rect(surface, (0, 0, 0), (10, SCREEN_HEIGHT - 120, 220, text_height))
    pygame.draw.rect(surface, (100, 100, 100), (10, SCREEN_HEIGHT - 120, 220, text_height), 1)

    for i, text in enumerate(hotkey_text):
        text_surface = text_font.render(text, True, (200, 200, 200))
        surface.blit(text_surface, (15, SCREEN_HEIGHT - 112 + i * 20))


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
        g_input.handle_event(event)
        dt_input.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left button
                input_boxes = [mass_input, radius_input, g_input, dt_input]
                clicked_on_input = any(box.is_hovered(event.pos) for box in input_boxes)

                if not clicked_on_input:
                    create_object(mouse_x, mouse_y)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE:
                if hovered_object:
                    engine.remove_particle(hovered_object)
            elif event.key == pygame.K_RETURN:
                update_physics_parameters()
            elif event.key == pygame.K_SPACE:
                toggle_pause()
            elif event.key == pygame.K_KP_MULTIPLY:
                adjust_physics_parameters(g_delta=10)
            elif event.key == pygame.K_KP_DIVIDE:
                adjust_physics_parameters(g_delta=-10)
            elif event.key == pygame.K_KP_MINUS:
                adjust_physics_parameters(dt_delta=-0.01)
            elif event.key == pygame.K_KP_PLUS:
                adjust_physics_parameters(dt_delta=0.01)

    update_physics_parameters()

    engine.update()

    mass_input.update()
    radius_input.update()
    g_input.update()
    dt_input.update()

    draw_background(screen)

    for particle in engine.particles:
        if particle.active:
            if hasattr(particle, 'base_image') and particle.base_image:
                scaled_size = int(particle.radius * 2)
                if scaled_size > 0:
                    scaled_image = pygame.transform.smoothscale(
                        particle.base_image,
                        (scaled_size, scaled_size)
                    )

                    colored_image = apply_color_tint(scaled_image, particle.color)

                    screen.blit(
                        colored_image,
                        (int(particle.x - particle.radius), int(particle.y - particle.radius))
                    )
            else:
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
    g_input.draw(screen)
    dt_input.draw(screen)

    draw_ui_labels(screen, font)
    draw_hotkey_info(screen, font)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

import pygame
import random
import math
from physics import PhysicsEngine
from objects import Object
from ui import InputBox, draw_grid, find_object_under_mouse
from config import *
from utils import random_color, safe_float_convert

pygame.init()

try:
    import os
    icon_path = os.path.join("resources", "icons", "gravity.png")
    if os.path.exists(icon_path):
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
except:
    pass

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Physics Simulation")
clock = pygame.time.Clock()
running = True
font = pygame.font.Font(None, 24)
input_font = pygame.font.Font(None, 32)

engine = PhysicsEngine(G=100.0, dt=0.05)

mass_input = InputBox(SCREEN_WIDTH - 130, 10, 140, 32, str(DEFAULT_MASS))
radius_input = InputBox(SCREEN_WIDTH - 130, 50, 140, 32, str(DEFAULT_RADIUS))

def create_object(mouse_x, mouse_y): #create new object with new values from input
    mass = safe_float_convert(mass_input.text, DEFAULT_MASS, 1, 10000)
    radius = safe_float_convert(radius_input.text, DEFAULT_RADIUS, 1, 100)
    
    new_object = Object(
        x=mouse_x,
        y=mouse_y,
        mass=mass,
        radius=radius,
        vx=random.uniform(-10, 10),
        vy=random.uniform(-10, 10)
    )
    
    new_object.color = random_color()
    
    engine.add_particle(new_object)

def draw_object_info(screen, hovered_object, font):
    if hovered_object:
        info_text = [
            f"Mass: {hovered_object.mass:.1f}",
            f"Radius: {hovered_object.radius:.1f}",
            f"Pos: ({hovered_object.x:.1f}, {hovered_object.y:.1f})",
            f"Speed(X,Y): ({hovered_object.vx:.1f}, {hovered_object.vy:.1f})",
            f"Speed: {math.sqrt(hovered_object.vx**2 + hovered_object.vy**2):.1f}",
            f"ID: {str(hovered_object.id)[:8]}..."
        ]
        
        text_height = len(info_text) * 25 + 10
        pygame.draw.rect(screen, (0, 0, 0), (10, 10, 300, text_height))
        pygame.draw.rect(screen, (100, 100, 100), (10, 10, 300, text_height), 2)
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (20, 20 + i * 25))

def draw_ui_labels(screen, font):
    mass_label = font.render("Mass:", True, (255, 255, 255))
    radius_label = font.render("Radius:", True, (255, 255, 255))
    screen.blit(mass_label, (SCREEN_WIDTH - 200, 15))
    screen.blit(radius_label, (SCREEN_WIDTH - 211, 55))

while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()

    hovered_object = find_object_under_mouse(mouse_x, mouse_y, engine.particles, detection_radius=20)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        mass_input.handle_event(event)
        radius_input.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #left button
                if not mass_input.is_hovered(event.pos) and not radius_input.is_hovered(event.pos):
                    create_object(mouse_x, mouse_y)

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
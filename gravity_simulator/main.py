"""Gravity Simulator - N-body physics simulation using Newtonian mechanics

This module implements a 2D gravitational simulation where celestial bodies
interact according to Newton's law of universal gravitation (F = G·m₁·m₂/r²).

Key features:
- Real-time simulation of multiple celestial bodies with gravitational interactions
- Mouse interaction to create new bodies with configurable properties
- Dynamic UI for adjusting mass and radius of new objects
- Visual trails showing object movement history
- Information panel displaying physical properties of selected objects

Controls:
    • Left click: Create a new celestial body at mouse position
    • Mass/Radius inputs: Configure properties for new bodies
    • Hover over object: View detailed physical properties
    • Hover over object + "Delete": Delete celestial body
    • Num/*: Decrease G by 10, Num/*: Increase G by 10
    • Num-: Decrease dt by 0.01, Num+: Increase dt by 0.01
    • Spacebar: Pause simulation (dt = 0)
"""

import os
from typing import Optional, List, Tuple, Any
import pygame


from gravity_simulator.objects import Object
from gravity_simulator.controller import SimulationController
from gravity_simulator.physics import PhysicsEngine

from gravity_simulator.ui import (InputBox, find_object_under_mouse, draw_background,
                                  UIRenderer)

from gravity_simulator.config import (SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_MASS,
                                      DEFAULT_RADIUS)

from gravity_simulator.utils import apply_color_tint


class GravitySimulatorApp:
    """Main application class for the Gravity Simulator.

    This class encapsulates the entire application state, including the
    physics engine, UI elements, resources, and the main game loop.
    It handles initialization, event processing, updating, and rendering.
    """

    def __init__(self) -> None:
        """Initialize the Gravity Simulator application."""
        pygame.init()

        # Load graphical resources (icon, background, textures)
        self.icon: Optional[pygame.Surface] = self._load_icon()
        self.background: Optional[pygame.Surface] = self._load_background()

        # Initialize Pygame display and core components
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.icon:
            pygame.display.set_icon(self.icon)
        pygame.display.set_caption("Physics Simulation")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.input_font = pygame.font.Font(None, 32)

        # Initialize the physics simulation engine
        self.engine = PhysicsEngine(G=10.0, dt=0.05)
        # Load textures for planet visualization
        self.planet_textures: List[pygame.Surface] = self._load_textures()

        # Initialize UI input boxes for user configuration
        self.mass_input = InputBox(
            position=(SCREEN_WIDTH - 130, 10),
            size=(140, 32),
            text=str(DEFAULT_MASS)
        )
        self.radius_input = InputBox(
            position=(SCREEN_WIDTH - 130, 50),
            size=(140, 32),
            text=str(DEFAULT_RADIUS)
        )
        self.g_input = InputBox(
            position=(SCREEN_WIDTH - 130, 90),
            size=(140, 32),
            text="10.0"
        )
        self.dt_input = InputBox(
            position=(SCREEN_WIDTH - 130, 130),
            size=(140, 32),
            text="0.05"
        )

        # Initialize dedicated UI renderer for drawing interface elements
        self.ui_renderer = UIRenderer(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Initialize controller to handle user interactions and simulation logic
        self.controller = SimulationController(
            self.engine,
            self.mass_input,
            self.radius_input,
            self.g_input,
            self.dt_input
        )

        # Application state flag
        self.running = True

    def _load_icon(self) -> Optional[pygame.Surface]:
        """Load the application icon from resources"""
        try:
            icon_path = os.path.join("resources", "icons", "gravity.png")
            if os.path.exists(icon_path):
                return pygame.image.load(icon_path)
        except pygame.error as e:
            print(f"Failed to load icon: {e}")
        return None

    def _load_background(self) -> Optional[pygame.Surface]:
        """Load and scale the background image to fit the screen"""
        try:
            background_path = os.path.join("resources", "background", "back1.png")
            if os.path.exists(background_path):
                background = pygame.image.load(background_path)
                bg_width, bg_height = background.get_size()
                # Scale to cover the entire screen while maintaining aspect ratio
                scale_factor = max(SCREEN_WIDTH / bg_width, SCREEN_HEIGHT / bg_height)
                new_width = int(bg_width * scale_factor)
                new_height = int(bg_height * scale_factor)
                return pygame.transform.smoothscale(background, (new_width, new_height))

            print(f"Background image not found at: {background_path}")
        except pygame.error as e:
            print(f"Failed to load background: {e}")
        return None

    def _load_textures(self) -> List[pygame.Surface]:
        """Load planet textures from resources directory"""
        textures: List[pygame.Surface] = []
        texture_names = ["ice.png", "lava.png", "moon.png", "terran.png"]

        for texture_name in texture_names:
            try:
                texture_path = os.path.join("resources", "objects", texture_name)
                if os.path.exists(texture_path):
                    texture = pygame.image.load(texture_path)
                    texture = texture.convert_alpha()
                    textures.append(texture)
                    print(f"Loaded texture: {texture_name}")
                else:
                    print(f"Texture not found: {texture_path}")
            except pygame.error as e:
                print(f"Failed to load texture {texture_name}: {e}")

        print(f"Successfully loaded {len(textures)} textures")
        return textures

    def handle_events(self) -> None:
        """Process pygame events including user input and window events"""
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Handle input box events (typing, focus, etc.)
            self.mass_input.handle_event(event)
            self.radius_input.handle_event(event)
            self.g_input.handle_event(event)
            self.dt_input.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if click was on an input box to avoid creating objects
                    input_boxes = [self.mass_input, self.radius_input,
                                   self.g_input, self.dt_input]
                    clicked_on_input = any(box.is_hovered(event.pos) for box in input_boxes)

                    if not clicked_on_input:
                        # Create a new celestial body at mouse position
                        self.controller.create_object(mouse_x, mouse_y, self.planet_textures)

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event, mouse_x, mouse_y)

    def _handle_keydown(self, event: pygame.event.Event, mouse_x: int, mouse_y: int) -> None:
        """Handle keyboard events for simulation control"""
        # Find object under mouse for context-sensitive actions
        hovered_object = find_object_under_mouse(
            mouse_x, mouse_y, self.engine.particles, detection_radius=20
        )

        # Map keyboard keys to simulation actions
        if event.key == pygame.K_DELETE:
            if hovered_object:
                self.engine.remove_particle(hovered_object)
        elif event.key == pygame.K_RETURN:
            self.controller.update_physics_parameters()
        elif event.key == pygame.K_SPACE:
            self.controller.toggle_pause()
        elif event.key == pygame.K_KP_MULTIPLY:
            self.controller.adjust_physics_parameters(g_delta=10)
        elif event.key == pygame.K_KP_DIVIDE:
            self.controller.adjust_physics_parameters(g_delta=-10)
        elif event.key == pygame.K_KP_MINUS:
            self.controller.adjust_physics_parameters(dt_delta=-0.01)
        elif event.key == pygame.K_KP_PLUS:
            self.controller.adjust_physics_parameters(dt_delta=0.01)

    def update(self) -> None:
        """Update the simulation state for the current frame"""
        # Update physics parameters from UI inputs
        self.controller.update_physics_parameters()

        # Advance physics simulation by one time step
        self.engine.update()

        # Update UI element sizes (e.g., text box width based on content)
        self.mass_input.update()
        self.radius_input.update()
        self.g_input.update()
        self.dt_input.update()

    def render(self) -> None:
        """Render the application frame including background, objects, and UI"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Find object under mouse for displaying information
        hovered_object = find_object_under_mouse(
            mouse_x, mouse_y, self.engine.particles, detection_radius=20
        )

        # Draw background image
        draw_background(self.screen, self.background, 0, 0)

        # Draw all active celestial bodies
        for particle in self.engine.particles:
            if particle.active:
                typed_particle: Object = particle
                self._draw_particle(typed_particle)

        # Draw UI components using dedicated renderer
        self.ui_renderer.draw_object_info(self.screen, hovered_object, self.font)
        self.mass_input.draw(self.screen)
        self.radius_input.draw(self.screen)
        self.g_input.draw(self.screen)
        self.dt_input.draw(self.screen)
        self.ui_renderer.draw_ui_labels(self.screen, self.font)
        self.ui_renderer.draw_hotkey_info(self.screen, self.font)

    def _draw_particle(self, particle: Object) -> None:
        """Draw a single particle with its texture, color, and trail"""
        # Draw textured planet if available, otherwise draw a colored circle
        base_image: Any = getattr(particle, 'base_image', None)
        if base_image:
            scaled_size = int(particle.radius * 2)
            scaled_image = pygame.transform.smoothscale(
                base_image,
                (scaled_size, scaled_size))
            # Apply color tint to the texture
            colored_image = apply_color_tint(scaled_image, particle.color)
            self.screen.blit(
                colored_image,
                (int(particle.x - particle.radius), int(particle.y - particle.radius)))
        else:
            pygame.draw.circle(
                self.screen,
                particle.color,
                (int(particle.x), int(particle.y)),
                int(particle.radius))

        # Draw motion trail if it exists
        trail: List[Tuple[float, float]] = getattr(particle, 'trail', [])
        if len(trail) > 1:
            pygame.draw.lines(
                self.screen,
                particle.color,
                False,
                [(int(x), int(y)) for x, y in trail],
                1
            )

    def run(self) -> None:
        """Run the main application loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


def main() -> None:
    """Entry point for the applicatio"""
    app = GravitySimulatorApp()
    app.run()


if __name__ == "__main__":
    main()

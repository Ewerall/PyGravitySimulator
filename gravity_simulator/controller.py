"""Controller module for the Gravity Simulator.

This module provides the SimulationController class, which acts as the
intermediary between the user interface (UI) and the physics engine. It
handles user input events, manages simulation parameters, and controls
the creation and modification of celestial objects within the simulation.

The controller encapsulates the application's state (like pause status
and original time step) and provides methods that correspond to user
actions (e.g., creating objects, adjusting parameters, pausing).
"""

import random
from typing import List
import pygame
from gravity_simulator.physics import PhysicsEngine
from gravity_simulator.objects import Object
from gravity_simulator.ui import InputBox
from gravity_simulator.utils import safe_float_convert
from gravity_simulator.config import DEFAULT_MASS, DEFAULT_RADIUS


class SimulationController:
    """Manages the state and user interactions for the gravity simulation.

    This controller handles the logic for creating celestial objects,
    adjusting simulation parameters (G, dt), and controlling the
    simulation's run state (pause/resume). It serves as the bridge
    between UI input events and the physics engine.
    """

    def __init__(self, engine: PhysicsEngine,
                 mass_input: InputBox,
                 radius_input: InputBox,
                 g_input: InputBox,
                 dt_input: InputBox) -> None:
        """Initialize the simulation controller.

        Args:
            engine: The physics engine to control.
            mass_input: Input box for default mass of new objects.
            radius_input: Input box for default radius of new objects.
            g_input: Input box for gravitational constant.
            dt_input: Input box for simulation time step.
        """
        self.engine = engine
        self.mass_input = mass_input
        self.radius_input = radius_input
        self.g_input = g_input
        self.dt_input = dt_input
        self.original_dt = engine.dt
        self.is_paused = False

    def create_object(self, x: float, y: float, planet_textures: List[pygame.Surface]) -> None:
        """Create a new celestial body at the specified position.

        Creates a new Object with mass and radius taken from the respective
        input boxes. The object is assigned a random velocity and color.
        If textures are available, a random one is assigned.
        """
        # Get and validate mass/radius from UI inputs
        mass = safe_float_convert(self.mass_input.text, DEFAULT_MASS, 1, 10000)
        radius = safe_float_convert(self.radius_input.text, DEFAULT_RADIUS, 1, 100)

        # Select random texture if available
        base_image = random.choice(planet_textures) if planet_textures else None

        # Create new celestial object with random initial velocity
        new_object = Object(
            x=x,
            y=y,
            mass=mass,
            radius=radius,
            vx=random.uniform(-10, 10),
            vy=random.uniform(-10, 10),
            base_image=base_image
        )

        # Assign random RGB color for visual distinction
        new_object.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )

        self.engine.add_particle(new_object)

    def update_physics_parameters(self) -> None:
        """Update physics engine parameters from UI input boxes.

        Reads the current text values from the G and dt input boxes,
        validates them using safe conversion, and updates the physics
        engine's corresponding attributes.
        """
        # Update gravitational constant with bounds checking
        new_g = safe_float_convert(self.g_input.text, 100.0, 0.1, 10000.0)
        self.engine.G = new_g

        # Update time step with bounds checking
        new_dt = safe_float_convert(self.dt_input.text, 0.05, 0.0, 1.0)
        self.engine.dt = new_dt

    def adjust_physics_parameters(self, g_delta: float = 0, dt_delta: float = 0) -> None:
        """Adjust physics parameters by delta values and update input boxes.
        
        Modifies the current G or dt values by the specified deltas,
        respecting physical boundaries. Updates the corresponding UI
        input boxes to reflect the new values. Handles pause state
        transitions when dt is modified.
        """
        # Resume simulation if paused and dt is being adjusted
        if self.is_paused and dt_delta != 0:
            self.is_paused = False
            self.original_dt = self.engine.dt

        # Adjust gravitational constant with minimum bound
        new_g = max(0.1, self.engine.G + g_delta)
        self.engine.G = new_g
        self.g_input.text = str(round(new_g, 1))

        # Adjust time step with minimum bound
        new_dt = max(0.0, self.engine.dt + dt_delta)
        self.engine.dt = new_dt
        self.dt_input.text = str(round(new_dt, 3))

        # Pause simulation if time step reaches zero
        if new_dt == 0.0:
            self.is_paused = True

    def toggle_pause(self) -> None:
        """Toggle simulation pause state.

        Switches the simulation between running and paused states.
        When pausing, the current dt is saved. When resuming, the
        original dt is restored.
        """
        if self.is_paused:
            self.engine.dt = self.original_dt
            self.dt_input.text = str(round(self.original_dt, 3))
            self.is_paused = False
        else:
            self.original_dt = self.engine.dt
            self.engine.dt = 0.0
            self.dt_input.text = "0.0"
            self.is_paused = True

"""Physics engine for N-body gravitational simulation

This module implements a 2D gravitational physics engine based on Newtonian mechanics.
The simulation handles gravitational interactions, boundary collisions, and inelastic
collisions between celestial bodies.

Key physics concepts:
- Gravitational force: F = G·m₁·m₂/r² (with softening parameter)
- Numerical integration: Euler method with time step control
- Collision handling: Inelastic merging with conservation of momentum
- Boundary conditions: Elastic collisions with energy damping

The engine follows standard N-body simulation practices while optimizing for
real-time visualization in a 2D space.
"""

import math

from typing import List, Tuple, Set, Any


class PhysicsEngine:
    """Core physics engine for simulating gravitational interactions in 2D space

    This class implements an N-body simulation using Newtonian gravity with:
    - Gravitational force calculation with softening parameter
    - Velocity Verlet integration (semi-implicit Euler)
    - Inelastic collision handling with momentum conservation
    - Boundary collision with energy damping

    Attributes:
        particles: List of active celestial bodies in the simulation
        G: Gravitational constant (scaling factor for simulation)
        dt: Time step for numerical integration (seconds)
        softening: Softening parameter to prevent singularities at small distances

    Physics model:
        F = G · m₁ · m₂ · (r₂ - r₁) / (|r₂ - r₁|² + ε²)^(3/2)
        a = F/m
        v(t+dt) = v(t) + a(t)·dt
        r(t+dt) = r(t) + v(t+dt)·dt

    Where:
        • F: Force vector (px/s²)
        • G: Gravitational constant
        • m: Mass (arbitrary units)
        • r: Position vector (px)
        • ε: Softening parameter
    """
    def __init__(self, G: float = 10.0, dt: float = 0.1,
                 screen_width: int = 1280, screen_height: int = 720) -> None:
        """Initialize the physics engine with simulation parameters

        Args:
            G: Gravitational constant (default: 1.0)
                Higher values increase gravitational attraction
            dt: Time step for numerical integration (default: 0.1)
                Smaller values increase accuracy but decrease performance
            screen_width: Width of simulation screen
            screen_height: Height of simulation screen
        """

        self.particles: List[Any] = []
        self.G: float = G
        self.dt: float = dt
        self.softening: float = 0.1
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height

    def remove_particle(self, particle: Any) -> None:
        """Remove a particle from the simulation"""
        if particle in self.particles:
            self.particles.remove(particle)

    def add_particle(self, particle: Any) -> None:
        """Add a celestial body to the simulation"""
        self.particles.append(particle)

    def calc_force_beetween_particle(self, p1: Any, p2: Any) -> Tuple[float, float]:
        """Calculate gravitational force between two particle"""
        # Calculate distance vector
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        # Distance squared
        r_sq = dx ** 2 + dy ** 2

        # Regularized distance
        r = math.sqrt(r_sq + self.softening**2)

        # Calculate force magnitude component
        force_over_r_cubed = self.G * p1.mass * p2.mass / (r_sq * r)

        # Decompose force into components
        fx = force_over_r_cubed * dx
        fy = force_over_r_cubed * dy

        return fx, fy

    def calculate_total_force_for_particle(self, target_particle: Any) -> Tuple[float, float]:
        """Calculate total gravitational force on a particle from all other particles.
        
        This method sums up the individual gravitational forces exerted by all other
        active particles in the simulation on the target particle.
        
        Args:
            target_particle: The particle for which to calculate the total force.
            
        Returns:
            A tuple (fx_total, fy_total) representing the total force components
            acting on the target particle.
        """
        fx_total = 0.0
        fy_total = 0.0

        # Iterate through all particles in the simulation
        for other_particle in self.particles:
            # Skip the target particle itself and any inactive particles
            if other_particle is target_particle and other_particle.active:
                continue

            if not other_particle.active:
                continue

            # Calculate force between target and current particle
            fx, fy = self.calc_force_beetween_particle(target_particle, other_particle)
            # Accumulate the force components
            fx_total += fx
            fy_total += fy

        return fx_total, fy_total

    def merge_particles(self, p1: Any, p2: Any) -> None:
        """Merge two colliding particles using conservation laws.
        
        This method handles inelastic collisions by combining two particles into one,
        conserving mass and momentum while positioning the new particle at the
        center of mass. The radius is calculated to conserve volume assuming
        spherical particles.
        
        Physics implemented:
        - Conservation of mass: m_total = m1 + m2
        - Conservation of momentum: v_new = (m1·v1 + m2·v2) / m_total
        - Center of mass position: r_new = (m1·r1 + m2·r2) / m_total
        - Volume conservation: r_new = (r1³ + r2³)^(1/3) assuming spherical particles
        
        Args:
            p1: First particle (will absorb p2 and remain active).
            p2: Second particle (will be deactivated after merging).
        """
        # Ensure both particles are active before merging
        if not p1.active or not p2.active:
            return

        # Conservation of mass - total mass is sum of individual masses
        total_mass = p1.mass + p2.mass

        # Conservation of momentum - calculate new velocity components
        # Formula: v_new = (m1*v1 + m2*v2) / (m1 + m2)
        vx_new = (p1.mass * p1.vx + p2.mass * p2.vx) / total_mass
        vy_new = (p1.mass * p1.vy + p2.mass * p2.vy) / total_mass

        # Center of mass position - weighted average of positions
        # Formula: r_new = (m1*r1 + m2*r2) / (m1 + m2)
        x_new = (p1.mass * p1.x + p2.mass * p2.x) / total_mass
        y_new = (p1.mass * p1.y + p2.mass * p2.y) / total_mass

        # Volume conservation for spherical particles
        # Volume of sphere = (4/3)*π*r³, so r_new = (r1³ + r2³)^(1/3)
        r_new = (p1.radius**3 + p2.radius**3)**(1 / 3)

        # Update first particle with merged properties
        p1.mass = total_mass
        p1.radius = r_new
        p1.vx, p1.vy = vx_new, vy_new
        p1.x, p1.y = x_new, y_new

        # Deactivate second particle as it has been absorbed
        p2.active = False

    def handle_collision(self) -> None:
        """Detect and process inelastic collisions between particles.
        
        This method performs collision detection and handling in three steps:
        1. Creates a list of currently active particles
        2. Checks all unique pairs of active particles for overlap
        3. Processes overlapping pairs through the merge_particles method
        
        Collision detection uses:
        - Distance-based approach (distance < sum of radii)
        - Pair tracking to avoid duplicate processing
        
        The method:
        1. Creates a list of active particles
        2. Checks all unique pairs for overlap
        3. Processes valid collisions through merge_particles()
        """
        # Create list of active particles to avoid modifying list during iteration
        active_particles = [p for p in self.particles if p.active]
        n = len(active_particles)
        # Use set to track processed pairs and avoid duplicate collision handling
        collided_pairs: Set[Tuple[int, int]] = set()

        # Check all unique pairs of active particles for collisions
        for i in range(n):
            p1 = active_particles[i]
            # Skip inactive particles
            if not p1.active:
                continue

            for j in range(i + 1, n):
                p2 = active_particles[j]
                # Skip inactive particles
                if not p2.active:
                    continue

                # Calculate squared distance between particle centers
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                distance_sq = dx ** 2 + dy ** 2
                # Minimum distance for collision is sum of radii
                min_distance = p1.radius + p2.radius

                # Check for collision using squared distances to avoid sqrt
                if distance_sq < min_distance ** 2:
                    # Create unique pair identifier to prevent duplicate processing
                    id1 = id(p1)
                    id2 = id(p2)
                    # Order IDs to ensure consistent pair key regardless of order
                    pair_key: Tuple[int, int] = (min(id1, id2), max(id1, id2))

                    # Process collision only if this pair hasn't been handled yet
                    if pair_key not in collided_pairs:
                        collided_pairs.add(pair_key)
                        # Merge the colliding particles
                        self.merge_particles(p1, p2)

    def update(self) -> None:
        """Update simulation state for current time step

        This method performs the physics integration in the following order:
        1. Calculate gravitational forces between all particles (dynamically)
        2. Update velocities using acceleration (v = v₀ + a·dt)
        3. Update positions using new velocities (x = x₀ + v·dt)
        4. Handle boundary conditions with wrap-around (teleportation)
        5. Update motion trails for visualization
        6. Process particle collisions and merging
        """
        # Update velocity and position using Newton's second law
        for p in self.particles:
            if not p.active:
                continue

            # Calculate total force dynamically
            fx_total, fy_total = self.calculate_total_force_for_particle(p)

            # Calculate acceleration: a = F/m
            ax = fx_total / p.mass
            ay = fy_total / p.mass

            # Update velocity: v = v₀ + a·dt
            p.vx += ax * self.dt
            p.vy += ay * self.dt

            # Update position: x = x₀ + v·dt
            p.x += p.vx * self.dt
            p.y += p.vy * self.dt

            # Handle boundary conditions with wrap-around (teleportation)
            teleported = False  # teleport flag

            # Left/right boundaries
            if p.x + p.radius < 0:
                p.x = self.screen_width + p.radius
                teleported = True
            elif p.x - p.radius > self.screen_width:
                p.x = -p.radius
                teleported = True

            # Top/bottom boundaries
            if p.y + p.radius < 0:
                p.y = self.screen_height + p.radius
                teleported = True
            elif p.y - p.radius > self.screen_height:
                p.y = -p.radius
                teleported = True

            # Update motion trail from the edge opposite to the direction of movement
            if hasattr(p, 'trail'):
                # if teleport, clear trail
                if teleported:
                    p.trail.clear()

                # Calculate the point on the edge of the circle
                # that is opposite to the direction of movement.
                # Avoid division by zero if velocity is zero.
                speed = math.sqrt(p.vx**2 + p.vy**2)
                if speed > 1e-10:  # A small epsilon to check for non-zero speed
                    # Unit vector in the direction opposite to velocity
                    ux = -p.vx / speed
                    uy = -p.vy / speed
                    # Point on the edge: center + radius * unit_vector_opposite
                    trail_x = p.x + p.radius * ux
                    trail_y = p.y + p.radius * uy
                else:
                    trail_x = p.x
                    trail_y = p.y

                # add new pos
                p.trail.append((trail_x, trail_y))
                if len(p.trail) > p.max_trail_length:
                    p.trail.pop(0)

        self.handle_collision()

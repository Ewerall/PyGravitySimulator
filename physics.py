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

Note: Screen dimensions are currently hardcoded but should be made configurable
in future versions for better flexibility.
"""

import math


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

    def __init__(self, G=1.0, dt=0.1):
        """Initialize the physics engine with simulation parameters

        Args:
            G: Gravitational constant (default: 1.0)
                Higher values increase gravitational attraction
            dt: Time step for numerical integration (default: 0.1)
                Smaller values increase accuracy but decrease performance
        """
        self.particles = []
        self.G = G
        self.dt = dt
        self.softening = 0.1  # Softening parameter to prevent infinite forces

    def add_particle(self, particle):
        """Add a celestial body to the simulation

        Args:
            particle: CelestialBody object to add to the simulation
        """
        self.particles.append(particle)

    def calculate_forces(self):
        """Compute gravitational forces between all particle pairs

        Implementation uses direct summation (O(n²) complexity) with:
        1. Force reset for all particles
        2. Pairwise force calculation with Newton's 3rd law
        3. Softened gravity to prevent singularities

        The gravitational force is calculated as:
            F = G · m₁ · m₂ · (r_vec) / (r² + ε²)^(3/2)

        Where:
            • r_vec: Distance vector between particles
            • r: Euclidean distance
            • ε: Softening parameter (0.1 by default)

        Note: This method modifies the fx, fy attributes of particles.
        """
        # Reset forces for all particles
        for p in self.particles:
            p.fx = 0
            p.fy = 0

        # Iterate through all unique pairs of particles
        n = len(self.particles)
        for i in range(n):
            p1 = self.particles[i]
            if not p1.active:
                continue

            for j in range(i + 1, n):
                p2 = self.particles[j]
                if not p2.active:
                    continue

                # Calculate distance vector
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                r_sq = dx * dx + dy * dy  # Distance squared
                r = math.sqrt(r_sq + self.softening**2)  # Regularized distance

                # Calculate force magnitude component
                force_over_r_cubed = self.G * p1.mass * p2.mass / (r_sq * r)

                # Decompose force into components
                fx = force_over_r_cubed * dx
                fy = force_over_r_cubed * dy

                # Apply equal and opposite forces (Newton's 3rd law)
                p1.fx += fx
                p1.fy += fy
                p2.fx -= fx
                p2.fy -= fy

    def update(self):
        """Update simulation state for current time step

        This method performs the physics integration in the following order:
        1. Calculate gravitational forces between all particles
        2. Update velocities using acceleration (v = v₀ + a·dt)
        3. Update positions using new velocities (x = x₀ + v·dt)
        4. Handle boundary collisions with energy damping
        5. Update motion trails for visualization
        6. Process particle collisions and merging

        Note: Screen dimensions are hardcoded (1280x720) and should be made
        configurable in future versions.
        """
        self.calculate_forces()

        # Update velocity and position using Newton's second law
        for p in self.particles:
            if not p.active:
                continue

            # Calculate acceleration: a = F/m
            ax = p.fx / p.mass
            ay = p.fy / p.mass

            # Update velocity: v = v₀ + a·dt
            p.vx += ax * self.dt
            p.vy += ay * self.dt

            # Update position: x = x₀ + v·dt
            p.x += p.vx * self.dt
            p.y += p.vy * self.dt

            # Boundary collision handling (currently hardcoded dimensions)
            screen_width = 1280
            screen_height = 720

            # Left/right boundaries
            if p.x - p.radius < 0:
                p.x = p.radius
                p.vx = abs(p.vx) * 0.8  # 20% energy loss
            elif p.x + p.radius > screen_width:
                p.x = screen_width - p.radius
                p.vx = -abs(p.vx) * 0.8

            # Top/bottom boundaries
            if p.y - p.radius < 0:
                p.y = p.radius
                p.vy = abs(p.vy) * 0.8
            elif p.y + p.radius > screen_height:
                p.y = screen_height - p.radius
                p.vy = -abs(p.vy) * 0.8

            # Update motion trail
            if hasattr(p, 'trail'):
                p.trail.append((p.x, p.y))
                if len(p.trail) > p.max_trail_length:
                    p.trail.pop(0)

        self.handle_collisions()

    def handle_collisions(self):
        """Detect and process inelastic collisions between particles

        Collision detection uses:
        - Distance-based approach (distance < sum of radii)
        - Pair tracking to avoid duplicate processing

        The method:
        1. Creates a list of active particles
        2. Checks all unique pairs for overlap
        3. Processes valid collisions through merge_particles()

        Note: This method does not modify particle positions during detection
        to avoid chain reactions in a single time step.
        """
        # Create list of active particles
        active_particles = [p for p in self.particles if p.active]
        n = len(active_particles)
        collided_pairs = set()  # Track processed pairs

        for i in range(n):
            p1 = active_particles[i]
            if not p1.active:
                continue

            for j in range(i + 1, n):
                p2 = active_particles[j]
                if not p2.active:
                    continue

                # Check for collision
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                distance_sq = dx * dx + dy * dy
                min_distance = p1.radius + p2.radius

                if distance_sq < min_distance * min_distance:
                    # Track unique pairs to avoid duplicates
                    pair_key = tuple(sorted([id(p1), id(p2)]))
                    if pair_key not in collided_pairs:
                        collided_pairs.add(pair_key)
                        self.merge_particles(p1, p2)

    def merge_particles(self, p1, p2):
        """Merge two colliding particles using conservation laws

        Implements inelastic collision with:
        - Conservation of mass: m_total = m1 + m2
        - Conservation of momentum: v_new = (m1·v1 + m2·v2) / m_total
        - Center of mass position: r_new = (m1·r1 + m2·r2) / m_total
        - Radius scaling: r_new = sqrt(m_total) (visual representation)

        Args:
            p1: First particle (will absorb p2)
            p2: Second particle (will be deactivated)

        Note: p2 is deactivated rather than removed to maintain stable
        particle indexing during simulation.
        """
        if not p1.active or not p2.active:
            return

        # Conservation of mass
        total_mass = p1.mass + p2.mass

        # Conservation of momentum
        vx_new = (p1.mass * p1.vx + p2.mass * p2.vx) / total_mass
        vy_new = (p1.mass * p1.vy + p2.mass * p2.vy) / total_mass

        # Center of mass position
        x_new = (p1.mass * p1.x + p2.mass * p2.x) / total_mass
        y_new = (p1.mass * p1.y + p2.mass * p2.y) / total_mass

        # Update first particle
        p1.mass = total_mass
        p1.radius = math.sqrt(total_mass)  # Radius proportional to mass^0.5
        p1.vx, p1.vy = vx_new, vy_new
        p1.x, p1.y = x_new, y_new

        # Deactivate second particle
        p2.active = False

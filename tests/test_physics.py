"""Physics engine tests for N-body gravitational simulation

This test suite verifies the correctness of the gravitational physics engine
by testing:
- Initialization and basic properties
- Force calculation between particles
- Position and velocity updates
- Boundary collision handling
- Particle merging with conservation laws
"""

from typing import Generator

import pytest

from gravity_simulator.physics import PhysicsEngine


class MockParticle:
    """Mock object representing a celestial body for physics testing"""

    def __init__(self, x: float = 0, y: float = 0, vx: float = 0, vy: float = 0,
                 mass: float = 1, radius: float = 1) -> None:
        """Initialize mock particle with position, velocity, mass and radius"""
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        self.mass: float = mass
        self.radius: float = radius
        self.active: bool = True


class TestPhysicsEngine:
    """Test suite for PhysicsEngine class"""

    @pytest.fixture
    def engine(self) -> Generator[PhysicsEngine, None, None]:
        """Create physics engine with test parameters"""
        engine = PhysicsEngine(G=1.0, dt=0.1)
        engine.softening = 0.0
        yield engine

    @pytest.fixture
    def particle(self) -> Generator[MockParticle, None, None]:
        """Create a mock particle"""
        particle = MockParticle()
        yield particle

    def test_initialization(self, engine: PhysicsEngine) -> None:
        """Test physics engine initialization"""
        assert len(engine.particles) == 0
        assert engine.G == 1.0
        assert engine.dt == 0.1
        assert engine.softening == 0.0

    def test_add_particle(self, engine: PhysicsEngine, particle: MockParticle) -> None:
        """Test adding particle to engine"""
        engine.add_particle(particle)
        assert len(engine.particles) == 1
        assert particle in engine.particles

    def test_calculate_force_between_particles(self, engine: PhysicsEngine) -> None:
        """Test force calculation between two particles"""
        p1 = MockParticle(x=0, y=0, mass=1)
        p2 = MockParticle(x=1, y=0, mass=1)

        fx, fy = engine.calc_force_beetween_particle(p1, p2)

        # Particles should attract each other
        assert fx > 0  # p1 should be pulled towards p2 (positive x direction)
        assert fy == 0  # Same y coordinate, no y force

        # Newton's third law: forces should be equal and opposite
        fx2, fy2 = engine.calc_force_beetween_particle(p2, p1)
        assert fx == -fx2
        assert fy == -fy2

    def test_calculate_total_force_on_particle(self, engine: PhysicsEngine) -> None:
        """Test total force calculation on a particle"""
        p1 = MockParticle(x=0, y=0, mass=1)
        p2 = MockParticle(x=1, y=0, mass=1)
        p3 = MockParticle(x=0, y=1, mass=1)

        engine.add_particle(p1)
        engine.add_particle(p2)
        engine.add_particle(p3)

        fx_total, fy_total = engine.calculate_total_force_for_particle(p1)

        # Should have forces from both p2 and p3
        assert fx_total != 0
        assert fy_total != 0

    @pytest.mark.parametrize("x1,y1,x2,y2,expected_fx_sign", [
        (0, 0, 1, 0, 1),   # p1 at origin, p2 to the right, p1 pulled right (positive)
        (1, 0, 0, 0, -1),  # p1 to the right, p2 at origin, p1 pulled left (negative)
    ])
    def test_calculate_force_between_particles_direction(self, engine: PhysicsEngine,
                                                         x1: float, y1: float, x2: float,
                                                         y2: float, expected_fx_sign: int) -> None:
        """Test force direction calculation between two particles"""
        p1 = MockParticle(x=x1, y=y1, mass=1)
        p2 = MockParticle(x=x2, y=y2, mass=1)

        fx, fy = engine.calc_force_beetween_particle(p1, p2)  # type: ignore

        # Check force direction
        assert fx * expected_fx_sign > 0

    def test_update_no_particles(self, engine: PhysicsEngine) -> None:
        """Test update with no particles"""
        engine.update()

    def test_update_single_particle(self, engine: PhysicsEngine) -> None:
        """Test particle update with zero forces (no other particles)"""
        particle = MockParticle(x=640, y=360, vx=1, vy=1, mass=1)
        engine.add_particle(particle)

        initial_x = particle.x
        initial_y = particle.y
        initial_vx = particle.vx
        initial_vy = particle.vy

        engine.update()

        # With no other particles, no forces should act, so velocity stays constant
        assert particle.x == pytest.approx(initial_x + initial_vx * engine.dt)  # type: ignore
        assert particle.y == pytest.approx(initial_y + initial_vy * engine.dt)  # type: ignore
        assert particle.vx == initial_vx
        assert particle.vy == initial_vy

    def test_update_two_particles_gravitational_attraction(self, engine: PhysicsEngine) -> None:
        """Test that particles attract each other due to gravity"""
        p1 = MockParticle(x=0, y=0, vx=0, vy=0, mass=1)
        p2 = MockParticle(x=10, y=0, vx=0, vy=0, mass=1)

        engine.add_particle(p1)
        engine.add_particle(p2)

        initial_p1_x = p1.x
        initial_p2_x = p2.x

        # Run several updates to see the effect
        for _ in range(10):
            engine.update()

        # Particles should move towards each other
        assert p1.x > initial_p1_x  # p1 should move right
        assert p2.x < initial_p2_x  # p2 should move left

    #No more bounce!
    #Need more tests

    #def test_boundary_collision_left(self, engine: PhysicsEngine) -> None:
        #particle = MockParticle(x=0.5, y=100, vx=-1, vy=0, mass=1, radius=1)
        #engine.add_particle(particle)

        #engine.update()

        #assert particle.x == 1
        #assert particle.vx > 0
        #assert particle.vx == pytest.approx(1 * 0.8)  # type: ignore

    #@pytest.mark.parametrize("initial_x,expected_x,initial_vx,expected_vx", [
        #(0.5, 1, -1, 0.8),
        #(1279.5, 1279, 1, -0.8),
    #])
    #def test_boundary_collision_horizontal(self, engine: PhysicsEngine, initial_x: float,
                                           #expected_x: float, initial_vx: float,
                                           #expected_vx: float) -> None:
        #particle = MockParticle(x=initial_x, y=100, vx=initial_vx, vy=0, mass=1, radius=1)
        #engine.add_particle(particle)

        #engine.update()

        #assert particle.x == expected_x
        #assert particle.vx == pytest.approx(expected_vx)  # type: ignore

    def test_merge_particles_conservation_of_momentum(self, engine: PhysicsEngine) -> None:
        """Test momentum conservation during particle merging"""
        p1 = MockParticle(x=0, y=0, vx=2, vy=0, mass=1, radius=1)
        p2 = MockParticle(x=0.5, y=0, vx=0, vy=0, mass=3, radius=1)
        engine.add_particle(p1)
        engine.add_particle(p2)

        initial_momentum_x = p1.mass * p1.vx + p2.mass * p2.vx
        initial_momentum_y = p1.mass * p1.vy + p2.mass * p2.vy

        engine.handle_collision()

        active_particle = p1 if p1.active else p2
        final_momentum_x = active_particle.mass * active_particle.vx
        final_momentum_y = active_particle.mass * active_particle.vy

        assert final_momentum_x == pytest.approx(initial_momentum_x, rel=1e-10)  # type: ignore
        assert final_momentum_y == pytest.approx(initial_momentum_y, rel=1e-10)  # type: ignore

    def test_inactive_particle_not_processed(self, engine: PhysicsEngine) -> None:
        """Test that inactive particles are not processed"""
        active_particle = MockParticle(x=10, y=10, mass=1, radius=1)
        inactive_particle = MockParticle(x=10.5, y=10, mass=1, radius=1)
        inactive_particle.active = False

        engine.add_particle(active_particle)
        engine.add_particle(inactive_particle)

        # Before collision handling, check active states
        assert active_particle.active is True
        assert inactive_particle.active is False

        engine.handle_collision()

        # After collision handling, inactive particle should remain inactive
        # and not affect the active one
        assert inactive_particle.active is False

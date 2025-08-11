"""Physics engine tests for N-body gravitational simulation

This test suite verifies the correctness of the gravitational physics engine
by testing:
- Initialization and basic properties
- Force calculation between particles
- Position and velocity updates
- Boundary collision handling
- Particle merging with conservation laws
"""

import pytest

from gravity_simulator.physics import PhysicsEngine


class MockParticle:
    """Mock object representing a celestial body for physics testing"""

    def __init__(self, x=0, y=0, vx=0, vy=0, mass=1, radius=1):
        """Initialize mock particle with position, velocity, mass and radius"""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = radius
        self.active = True


class TestPhysicsEngine:
    """Test suite for PhysicsEngine class"""

    @pytest.fixture
    def engine(self):
        """Create physics engine with test parameters"""
        engine = PhysicsEngine(G=1.0, dt=0.1)
        engine.softening = 0.0
        return engine

    @pytest.fixture
    def particle(self):
        """Create a mock particle"""
        return MockParticle()

    def test_initialization(self, engine):
        """Test physics engine initialization"""
        assert len(engine.particles) == 0
        assert engine.G == 1.0
        assert engine.dt == 0.1
        assert engine.softening == 0.0

    def test_add_particle(self, engine, particle):
        """Test adding particle to engine"""
        engine.add_particle(particle)
        assert len(engine.particles) == 1
        assert particle in engine.particles

    def test_calculate_forces_no_particles(self, engine):
        """Test force calculation with no particles"""
        engine.calculate_forces()

    def test_calculate_forces_single_particle(self, engine):
        """Test force calculation with single particle"""
        particle = MockParticle(x=0, y=0, mass=1)
        engine.add_particle(particle)
        engine.calculate_forces()
        assert hasattr(particle, 'fx')
        assert hasattr(particle, 'fy')
        assert particle.fx == 0
        assert particle.fy == 0

    @pytest.mark.parametrize("x1,y1,x2,y2,expected_fx_sign", [
        (0, 0, 1, 0, 1),
        (1, 0, 0, 0, -1),
    ])
    def test_calculate_forces_two_particles_attractive(
        self, engine, x1, y1, x2, y2, expected_fx_sign
    ):
        """Test force calculation between two particles"""
        p1 = MockParticle(x=x1, y=y1, mass=1)
        p2 = MockParticle(x=x2, y=y2, mass=1)
        engine.add_particle(p1)
        engine.add_particle(p2)

        engine.calculate_forces()

        assert hasattr(p1, 'fx')
        assert hasattr(p1, 'fy')
        assert hasattr(p2, 'fx')
        assert hasattr(p2, 'fy')

        assert p1.fx == -p2.fx
        assert p1.fy == -p2.fy

        assert p1.fx * expected_fx_sign > 0

    def test_update_no_particles(self, engine):
        """Test update with no particles"""
        engine.update()

    def test_update_single_particle(self, engine):
        """Test particle update with zero forces"""
        particle = MockParticle(x=640, y=360, vx=1, vy=1, mass=1)
        engine.add_particle(particle)

        particle.fx = 0
        particle.fy = 0

        initial_x = particle.x
        initial_y = particle.y
        initial_vx = particle.vx
        initial_vy = particle.vy

        engine.update()

        assert particle.x == pytest.approx(initial_x + initial_vx * engine.dt)
        assert particle.y == pytest.approx(initial_y + initial_vy * engine.dt)

        assert particle.vx == initial_vx
        assert particle.vy == initial_vy

    def test_boundary_collision_left(self, engine):
        """Test left boundary collision handling"""
        particle = MockParticle(x=0.5, y=100, vx=-1, vy=0, mass=1, radius=1)
        engine.add_particle(particle)

        engine.update()

        assert particle.x == 1
        assert particle.vx > 0
        assert particle.vx == pytest.approx(1 * 0.8)

    @pytest.mark.parametrize("initial_x,expected_x,initial_vx,expected_vx", [
        (0.5, 1, -1, 0.8),
        (1279.5, 1279, 1, -0.8),
    ])
    def test_boundary_collision_horizontal(
        self, engine, initial_x, expected_x, initial_vx, expected_vx
    ):
        """Test horizontal boundary collision handling"""
        particle = MockParticle(x=initial_x, y=100, vx=initial_vx, vy=0, mass=1, radius=1)
        engine.add_particle(particle)

        engine.update()

        assert particle.x == expected_x
        assert particle.vx == pytest.approx(expected_vx)

    def test_merge_particles_conservation_of_momentum(self, engine):
        """Test momentum conservation during particle merging"""
        p1 = MockParticle(x=0, y=0, vx=2, vy=0, mass=1, radius=1)
        p2 = MockParticle(x=0.5, y=0, vx=0, vy=0, mass=3, radius=1)
        engine.add_particle(p1)
        engine.add_particle(p2)

        initial_momentum_x = p1.mass * p1.vx + p2.mass * p2.vx
        initial_momentum_y = p1.mass * p1.vy + p2.mass * p2.vy

        engine.handle_collisions()

        active_particle = p1 if p1.active else p2
        final_momentum_x = active_particle.mass * active_particle.vx
        final_momentum_y = active_particle.mass * active_particle.vy

        assert final_momentum_x == pytest.approx(initial_momentum_x, rel=1e-10)
        assert final_momentum_y == pytest.approx(initial_momentum_y, rel=1e-10)

    def test_inactive_particle_not_processed(self, engine):
        """Test that inactive particles are not processed"""
        active_particle = MockParticle(x=10, y=0, mass=1, radius=1)
        inactive_particle = MockParticle(x=0, y=0, mass=1, radius=1)
        inactive_particle.active = False

        engine.add_particle(active_particle)
        engine.add_particle(inactive_particle)

        engine.calculate_forces()
        engine.update()

        if hasattr(active_particle, 'fx'):
            assert active_particle.fx == 0
            assert active_particle.fy == 0

        if hasattr(inactive_particle, 'fx'):
            assert inactive_particle.fx == 0
            assert inactive_particle.fy == 0

class PhysicsEngine:
     
    def __init__(self, G = 1.0, dt = 0.1):
        self.particles = []
        self.G = G
        self.dt = dt
        self.softening = 0.1  # softening parameter to prevent infinite forces at small distances


    def add_particle(self, particle):
        self.particles.append(particle)


    def calculate_forces(self):

        # reset forces for all particles
        for p in self.particles:
            p.fx = 0
            p.fy = 0

        # iterate through ALL pairs of particles (avoiding duplicates)
        n = len(self.particles)
        for i in range(n):
            p1 = self.particles[i]
            if not p1.active:
                continue
            
            for j in range(i + 1, n):
                p2 = self.particles[j]
                if not p2.active:
                    continue
                
                # calculate distance vector between p1 and p2
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                r_sq = dx*dx + dy*dy  # distance squared
                r = (r_sq + self.softening**2)**0.5  # regularized distance to prevent division by zero
                
                # newton's law of universal gravitation: F = G * (m1 * m2) / r²
                # we use (r² + ε²)^(3/2) in denominator for better numerical stability
                force_over_r_cubed = self.G * p1.mass * p2.mass / (r_sq * r)
                
                # decompose force into x and y components
                fx = force_over_r_cubed * dx
                fy = force_over_r_cubed * dy
                
                # apply equal and opposite forces to BOTH objects (Newton's 3rd law)
                p1.fx += fx
                p1.fy += fy
                p2.fx -= fx
                p2.fy -= fy


    def update(self):
        self.calculate_forces()
        
        # update velocity and position using Newton's second law
        for p in self.particles:
            if not p.active:
                continue
            
            # acceleration: a = F / m
            ax = p.fx / p.mass
            ay = p.fy / p.mass
            
            # update velocity: v = v + a * dt (Euler integration)
            p.vx += ax * self.dt
            p.vy += ay * self.dt
            
            # update position: x = x + v * dt
            p.x += p.vx * self.dt
            p.y += p.vy * self.dt

            screen_width = 1280
            screen_height = 720
            
            # boundary collision - bounce off left and right edges
            if p.x - p.radius < 0:
                p.x = p.radius  # prevent object from going outside boundary
                p.vx = abs(p.vx) * 0.8  # energy loss on bounce (damping factor)
            elif p.x + p.radius > screen_width:
                p.x = screen_width - p.radius
                p.vx = -abs(p.vx) * 0.8  # reverse velocity with energy loss
            
            # boundary collision - bounce off top and bottom edges
            if p.y - p.radius < 0:
                p.y = p.radius
                p.vy = abs(p.vy) * 0.8  # energy loss on bounce
            elif p.y + p.radius > screen_height:
                p.y = screen_height - p.radius
                p.vy = -abs(p.vy) * 0.8  # reverse velocity with energy loss
            
            # update particle trail for visualization
            if hasattr(p, 'trail'):
                p.trail.append((p.x, p.y))
                if len(p.trail) > p.max_trail_length:
                    p.trail.pop(0)  # remove oldest point to maintain trail length
        
        self.handle_collisions()


    def handle_collisions(self):
        # create list of active particles to avoid modification issues during iteration
        active_particles = [p for p in self.particles if p.active]
        n = len(active_particles)
        
        collided_pairs = set()  # track processed pairs to avoid double handling
        
        for i in range(n):
            p1 = active_particles[i]
            if not p1.active:
                continue
            
            for j in range(i + 1, n):
                p2 = active_particles[j]
                if not p2.active:
                    continue
                
                # check if particles are overlapping/colliding
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                distance_sq = dx*dx + dy*dy  # distance squared for efficiency
                min_distance = p1.radius + p2.radius  # sum of radii
                
                # collision detected when distance < sum of radii
                if distance_sq < min_distance * min_distance:
                    # check if we've already processed this pair
                    pair_key = tuple(sorted([id(p1), id(p2)]))
                    if pair_key not in collided_pairs:
                        collided_pairs.add(pair_key)
                        self.merge_particles(p1, p2)


    def merge_particles(self, p1, p2):
        if not p1.active or not p2.active:
            return
        
        # conservation of mass
        total_mass = p1.mass + p2.mass
        
        # conservation of momentum - calculate new velocity
        vx_new = (p1.mass * p1.vx + p2.mass * p2.vx) / total_mass
        vy_new = (p1.mass * p1.vy + p2.mass * p2.vy) / total_mass
        
        # center of mass position
        x_new = (p1.mass * p1.x + p2.mass * p2.x) / total_mass
        y_new = (p1.mass * p1.y + p2.mass * p2.y) / total_mass
        
        # update first particle with merged properties
        p1.mass = total_mass
        p1.radius = total_mass ** 0.5  # Radius proportional to square root of mass
        p1.vx, p1.vy = vx_new, vy_new
        p1.x, p1.y = x_new, y_new
        
        # deactivate second particle (effectively remove it from simulation)
        p2.active = False
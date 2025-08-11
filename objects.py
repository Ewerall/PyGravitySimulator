import uuid

class Object():
    def __init__(self, x, y, mass, radius, vx=0, vy=0):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.vx = vx  # speed x
        self.vy = vy  # speed y
        self.color = (255, 255, 255)
        self.trail = [] 
        self.max_trail_length = 100
        self.active = True
        self.id = uuid.uuid4()
        
        # init forse
        self.fx = 0
        self.fy = 0
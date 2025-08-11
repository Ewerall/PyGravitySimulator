
# PyGravitySimulator

[![RU](https://img.shields.io/badge/RU-русский-0066CC?logo=russia&logoColor=white)](https://github.com/Ewerall/PyGravitySimulator/blob/main/readme.ru.md)

This is an interactive 2D simulation of gravitational interaction between objects with adjustable parameters.

![ezgif-6e618860b49857](https://github.com/user-attachments/assets/0e81918f-3970-4724-9d22-79e03b83e526)


## Project structure
```
PyGravitySimulator
├── tests/            # Tests
├── resources/        # Project resources
├── main.py           # Entry point
├── objects.py        # Object class (physical entities)
├── physics.py        # Physics engine
├── config.py         # Configuration constants (screen dimensions, etc.)
├── ui.py             # User interface (input fields, grid)
├── utils.py          # Utilities and helper functions (colors, conversions)
└── README.md         # This file
```

### Installation and Launch

```bash
pip install pygame
git clone https://github.com/Ewerall/PyGravitySimulator.git
python main.py
```

## Mathematics

### 1. Gravitational Interaction

The simulator uses Newton's classical law of universal gravitation with regularization to prevent numerical instability:

**Basic formulas:**
```
dx = p₂.x - p₁.x

dy = p₂.y - p₁.y

r² = dx² + dy²

r = √(r² + ε²)
```

Where:

-   `dx`, `dy` - components of the distance between objects
-   `r` - regularized distance
-   `ε` -  softening parameter, preventing infinite forces at small distances

**Gravitational force:**

```
F = G·(m₁·m₂)/(r² + ε²)^(3/2)·(dx, dy)
```

**Or in component form:**

```
Fₓ = G·m₁·m₂·dx/(r²·r)

Fᵧ = G·m₁·m₂·dy/(r²·r)
```
Where:

-   `G` - gravitational constant
-   `m₁`, `m₂` - masses of objects
-   `Fₓ`, `Fᵧ` - force components

##

### 2. Particle Motion

Particle motion is calculated using the Euler method:

**Acceleration:**

```
aₓ = Fₓ/m

aᵧ = Fᵧ/m
```

**Velocity:**

```
vₓ(t+dt) = vₓ(t) + aₓ·dt

vᵧ(t+dt) = vᵧ(t) + aᵧ·dt
```

**Position:**

```
x(t+dt) = x(t) + vₓ(t+dt)·dt

y(t+dt) = y(t) + vᵧ(t+dt)·dt
```

Where:

-   `dt` - time step
-   `a` - acceleration
-   `v` - velocity
-   `x`, `y` - coordinates

##

### 3. Collision Handling

**Collision detection**

```
dx = p₂.x - p₁.x

dy = p₂.y - p₁.y

r² = dx² + dy²

r = √r²

if r < (R₁ + R₂), a collision has occurred
```

Where:

-   `R₁`, `R₂` - radii of objects

##

### 4. Particle Merging

When particles collide, they merge while conserving momentum and recalculating the center of mass:

**Total mass:**

```
M = m₁ + m₂
```

**Velocity after merging (momentum conservation):**
```
vₓ = (m₁·v₁ₓ + m₂·v₂ₓ)/M

vᵧ = (m₁·v₁ᵧ + m₂·v₂ᵧ)/M
```

**Position after merging (center of mass):**

```
x = (m₁·x₁ + m₂·x₂)/M

y = (m₁·y₁ + m₂·y₂)/M
```

**Radius of the resulting object (for 2D):**

```
R = √M
```
This follows from the fact that in 2D, mass is proportional to the area of a circle: M ∝ πR² ⇒ R ∝ √M

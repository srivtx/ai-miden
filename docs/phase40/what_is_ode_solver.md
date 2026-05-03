## What Is an ODE Solver for Sampling?

---

### The Problem

Flow matching gives us a velocity field: `dx/dt = v(x_t, t)`. To generate a sample, we need to start from noise (t=1) and follow the velocity field back to data (t=0). How do we numerically integrate this differential equation? A naive approach with fixed step size is either too slow (many steps) or inaccurate (few steps).

---

### Definition

An **ODE solver** numerically integrates the ordinary differential equation that defines the flow. Common methods include:

1. **Euler method (fixed step):**
   ```
   x_{t-dt} = x_t - v(x_t, t) × dt
   ```
   Simple but needs many steps for accuracy.

2. **Midpoint method:**
   ```
   k1 = v(x_t, t)
   k2 = v(x_t - 0.5×dt×k1, t - 0.5×dt)
   x_{t-dt} = x_t - dt × k2
   ```
   More accurate than Euler with the same number of steps.

3. **RK4 (Runge-Kutta 4th order):**
   Evaluates the velocity field 4 times per step for high accuracy.

4. **Adaptive step size (Dormand-Prince):**
   Adjusts `dt` based on local error estimates. Takes small steps where the velocity changes rapidly and large steps where it is smooth.

**Key advantage:** Adaptive solvers might need only 10–50 steps to achieve the same accuracy as 1000 fixed Euler steps.

---

### Real-Life Analogy

Navigating a river back to its source.
- **Fixed small steps (Euler):** You check your compass every meter. Very accurate but takes forever.
- **Fixed large steps (Euler with big dt):** You check every kilometer. Fast but you might miss turns and get lost.
- **Adaptive steps:** You check more frequently near rapids and waterfalls (where the current changes rapidly) and less frequently in calm straight stretches. You reach the source quickly without getting lost.

---

### Tiny Numeric Example

**Velocity field:** v(x, t) = -x (pulls toward zero)

**Start:** x = 2.0 at t = 1.0

**Euler method (dt = 0.5):**
```
Step 1 (t=1.0): v = -2.0, x = 2.0 - 0.5 × (-2.0) = 3.0
Step 2 (t=0.5): v = -3.0, x = 3.0 - 0.5 × (-3.0) = 4.5
```
Diverges! The step size is too large for this velocity field.

**Euler method (dt = 0.1):**
```
After 10 steps: x ≈ 0.78
Exact solution: x = 2.0 × e^(-1) ≈ 0.736
Error: 6%
```

**Midpoint method (dt = 0.5, only 2 steps):**
```
Step 1 (t=1.0):
  k1 = -2.0
  k2 = -(2.0 - 0.25 × (-2.0)) = -2.5
  x = 2.0 - 0.5 × (-2.5) = 3.25 → wait, this is wrong direction
```
Actually for reverse time (t going from 1 to 0), the update should be:
```
x_{t-dt} = x_t + dt × v(x_t, t)   (if v points toward data)
```
Let me recalculate with correct sign convention.

**Corrected — velocity pulls toward data at t=0:**
```
dx/dt = (data - x) / t
```
At t=1, x=2, data=0:
```
v = (0 - 2) / 1 = -2
```

**Euler (dt=0.5):**
```
x(0.5) = 2.0 + 0.5 × (-2.0) = 1.0
x(0.0) = 1.0 + 0.5 × (-1.0/0.5) = 1.0 - 1.0 = 0.0
```
Exact in 2 steps for this simple case!

---

### Common Confusion

1. **"ODE solvers are only for flow matching."** No. They are general numerical methods used in physics, engineering, and any field with differential equations.

2. **"More steps always means better quality."** Diminishing returns apply. Going from 10 to 50 steps might help. Going from 50 to 1000 rarely does.

3. **"Adaptive solvers are slower per step."** Yes, because they evaluate the model multiple times per step to estimate error. But they need far fewer steps, so overall they are faster.

4. **"ODE solvers guarantee exact samples."** No. They are numerical approximations. The error depends on step size and solver order.

5. **"All flow matching uses the same solver."** No. Different applications use different trade-offs. Image generation often uses Euler or Heun. Scientific applications might use RK4 or implicit methods.

---

### Where It Is Used in Our Code

`src/phase40/phase40_flow_matching.py` — Implements Euler and midpoint ODE solvers for 2D flow sampling. Compares accuracy vs. number of steps.

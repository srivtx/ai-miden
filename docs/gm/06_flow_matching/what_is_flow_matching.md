## Why it exists (THE PROBLEM)

DDPM takes 1000 steps to generate one image. Each step is a full U-Net forward pass. For a 35M-parameter U-Net generating 4 logos, that's 35 billion operations, ~30 seconds on a T4. For production (video, interactive UI, real-time generation), this is unusable. You can't wait 30 seconds to see if a logo looks good then tweak the prompt and wait another 30 seconds.

The underlying problem is that DDPM follows a *curved* path through pixel space — a Brownian random walk from noise to data. Curved paths need many small steps because the direction changes at every point. A straight line only needs a few steps because the direction never changes.

**Flow matching** (Lipman et al., 2023) changes one assumption: instead of Brownian motion, the path from noise to data is a straight line. The model learns to predict the *velocity* along this line, not the *noise* at each timestep. Sampling becomes a simple Euler integration along a straight path — 20 steps instead of 1000.

## Definition (very simple)

A **flow** is a deterministic path from a noise distribution to the data distribution. Every noise sample $z \sim \mathcal{N}(0, I)$ has exactly one corresponding data point $x$ that it flows to. The flow is a time-dependent vector field $v(x, t)$ that tells us which direction to move at each point. The model learns $v_\theta(x_t, t)$ and then integrates it from $t=0$ to $t=1$ to go from noise to data.

In DDPM, the path is stochastic: $x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon$. In flow matching, the path is deterministic: $x_t = (1 - t) x_0 + t \epsilon$ (a straight-line interpolation from data to noise). At $t=0$, we're at the data. At $t=1$, we're at noise. During training, we sample $t$ and predict the velocity. During sampling, we start at noise ($t=1$) and move toward data ($t=0$) by following the predicted velocity.

The loss changes subtly: DDPM predicts $\epsilon$ (the noise added at step $t$). Flow matching predicts $v = \epsilon - x_0$ (the velocity from data to noise). Both use MSE: $\mathbb{E}[||v_\theta(x_t, t) - v||^2]$. The difference is what the model learns to output.

## Real-life analogy

**DDPM is navigating a dark room by touch.** You're blindfolded. You take 1000 tiny steps, feeling the walls, adjusting direction after each step. You eventually reach the door, but it takes forever. Every step is a guess corrected by the next step.

**Flow matching is walking a straight line toward a light you can see.** You're told the direction once — "the door is that way" — and you walk straight. You take 20 confident steps instead of 1000 tentative ones.

**DDPM is a drunk person finding their way home** — Brownian motion, random left, random right, slowly drifting toward the destination. **Flow matching is a sober person walking straight** — the direction is known, just follow it.

## Tiny numeric example

Let's generate a 1D point. Target data: $x_0 = 3.0$. Noise: $\epsilon = -1.2$.

**DDPM (1000 steps, T=1000):**
```
Step 0:  x_0 = 3.0 (real data)
Step t:  x_t = sqrt(alpha_bar_t) * 3.0 + sqrt(1 - alpha_bar_t) * (-1.2)
         where alpha_bar follows a cosine schedule from 1.0 to 0.0

At t=500: alpha_bar ≈ 0.5
  x_500 = sqrt(0.5) * 3.0 + sqrt(0.5) * (-1.2)
         = 0.707 * 3.0 + 0.707 * (-1.2)
         = 2.121 - 0.848 = 1.273

The path from x_1000 (pure noise) to x_0 (3.0) is curved in probability space.
```

**Flow matching (20 steps):**
```
x_t = (1 - t) * x_0 + t * epsilon

At t=0:    x_0 = 1.0 * 3.0 + 0.0 * (-1.2) = 3.0
At t=0.5:  x_0.5 = 0.5 * 3.0 + 0.5 * (-1.2) = 1.5 - 0.6 = 0.9
At t=1:    x_1 = 0.0 * 3.0 + 1.0 * (-1.2) = -1.2

The path is a straight line from (t=0, x=3.0) to (t=1, x=-1.2).
Velocity v = dx/dt = epsilon - x_0 = -1.2 - 3.0 = -4.2

Sampling (from noise to data, t=1→0, 20 Euler steps):
  Step size Δt = 1/20 = 0.05
  x_1 = -1.2 (start at noise)
  x_0.95 = x_1 + v_model(x_1, t=1) * (-0.05)     # move toward t=0
  x_0.90 = x_0.95 + v_model(x_0.95, t=0.95) * (-0.05)
  ... 20 steps ...
  x_0 ≈ 2.98 (close to 3.0!)
```

**The gain:** 1000 steps → 20 steps. 50× fewer forward passes. Same generation quality.

## Common confusion (5+ bullet points)

1. **"Flow matching is just DDPM with fewer steps."** No. The PATH is fundamentally different. DDPM follows a stochastic SDE (Brownian). Flow matching follows a deterministic ODE (straight line). You can't "just use fewer steps" in DDPM — the curvature of the path requires many steps. You CAN use DDIM to jump, but DDIM is an approximation that degrades quality. Flow matching is DESIGNED for few steps from the start.

2. **"Flow matching needs a different model architecture than DDPM."** No. The U-Net is identical. Only the loss function and the sampling loop change. You can literally take the same `LogoUNet` from logogen, retrain with velocity prediction instead of noise prediction, and sample with Euler integration. The model learns $v_\theta(x_t, t)$ instead of $\epsilon_\theta(x_t, t)$, but the architecture stays the same.

3. **"Flow matching is always better."** No. At very high step counts (1000+), DDPM and flow matching converge to the same quality. Flow matching wins at LOW step counts (10-50). For interactive generation, flow matching is strictly better. For offline batch generation where you don't care about speed, either works.

4. **"The straight path means the model learns less."** No. The model learns the SAME distribution, just through a different path. The evidence lower bound doesn't change. What changes is the sampling efficiency — the ODE solver needs fewer steps because the path has zero curvature.

5. **"Flow matching is hard to implement."** No. The changes from DDPM to flow matching are ~30 lines of Python. Replace `x_t = sqrt(alpha_bar) * x_0 + sqrt(1-alpha_bar) * noise` with `x_t = (1-t) * x_0 + t * noise`. Replace loss target from `noise` to `noise - x_0`. Replace DDPM reverse sampler with Euler ODE solver.

6. **"Flow matching requires fully-supervised pairs of (x_0, noise)."** No. Training is identical to DDPM: sample a random noise, interpolate to get x_t, predict velocity, MSE loss. The only difference is the interpolation schedule (straight line vs geometric).

## Key properties

| Property | DDPM | Flow Matching |
|---|---|---|
| Path type | Stochastic (SDE) | Deterministic (ODE) |
| Path shape | Curved (Brownian) | Straight line |
| Training loss | E\|\|ε - ε_θ(x_t, t)\|\|² | E\|\|v - v_θ(x_t, t)\|\|² |
| Target | Noise (ε) | Velocity (v = ε - x_0) |
| Sampling steps | 1000 (or 50 with DDIM) | 20 (Euler) or 4 (Heun) |
| Sampling method | Reverse diffusion | ODE integration |
| Quality at 50 steps | Blurry (DDIM) | Sharp |
| Quality at 1000 steps | Sharp | Sharp |
| Training time | Same | Same |
| Inference time at 1000 steps | 30s | 0.6s (at 20 steps) |

## Tech comparison: flow matching vs diffusion

**You use DDPM when:**
- You don't care about generation speed (offline batch)
- You're implementing from scratch and want the simplest possible code
- Quality at 1000 steps is the only metric that matters

**You use flow matching when:**
- Interactive generation (user clicks, sees result in <1s)
- You're building an API (every millisecond matters)
- You have limited compute (fewer forward passes = lower cost)
- You want to iterate fast (tweak model, test, repeat)

**You use consistency models when:**
- You need 1-2 step generation (real-time video, AR)
- Quality at 1 step matters more than quality at 20 steps
- You can afford a more complex training pipeline (distillation)

## Connection to our projects

**logogen:** This is the most immediate win. Replace the DDPM ODE solver in `logogen.py` with flow matching. Same U-Net, same data, same training time. Generation goes from 30s to <1s. The `generate_samples()` function changes from 1000-step reverse diffusion to 20-step Euler integration. ~30 lines of change.

**cortexcode:** Less relevant — cortexcode generates text, not pixels. But the principle (straight line → fewer steps) applies to any sequential generation. Speculative decoding is the LLM equivalent (predict multiple tokens, verify, accept/reject).

**gm/ curriculum:** Flow matching should be taught BEFORE latent diffusion, because it's a simpler change with bigger immediate gains. The progression should be: VAE (compression) → diffusion (DDPM, 1000 steps) → flow matching (straight line, 20 steps) → latent diffusion (VAE + diffusion combined).

**MSPCH (nature/):** The brain's prediction errors propagate in a straight line (feedback connections are direct corticocortical loops, not random walks). Flow matching is closer to how the brain actually does inference — a direct path from noisy sensory data to a clean percept — than DDPM's Brownian approximation.

## Mathematical deep dive

**DDPM forward:**
$$q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar{\alpha}_t} x_0, (1 - \bar{\alpha}_t)I)$$

**Flow matching forward (straight-line interpolation):**
$$x_t = (1 - t) x_0 + t \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$

Note: $t$ is continuous in $[0,1]$, not discrete. At $t=0$, $x_t = x_0$ (data). At $t=1$, $x_t = \epsilon$ (pure noise).

**Flow matching loss:**
$$\mathcal{L}_{FM} = \mathbb{E}_{t, x_0, \epsilon} \left[ \| v_\theta(x_t, t) - (\epsilon - x_0) \|^2 \right]$$

The target $v = \epsilon - x_0$ is the straight-line velocity from data to noise. The model learns to predict this velocity given a noisy point $x_t$ and time $t$.

**Flow matching sampling (ODE integration):**
$$\frac{dx}{dt} = v_\theta(x_t, t)$$
$$x_{t + \Delta t} = x_t + v_\theta(x_t, t) \cdot \Delta t \quad \text{(Euler method)}$$
Start at $x_1 = \epsilon \sim \mathcal{N}(0, I)$, integrate backward to $t=0$ with $N$ steps of size $\Delta t = -1/N$. Output $x_0$.

**Why fewer steps work:**
In DDPM, $x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon$ is a CURVED interpolation in data space. The noise-to-signal ratio changes nonlinearly with $t$. The model has to account for this curvature.

In flow matching, $x_t = (1 - t) x_0 + t \epsilon$ is a LINEAR interpolation. The noise-to-signal ratio changes linearly with $t$. Any deviation from the straight line is just model error. The ODE solver can take large steps because the underlying path has zero curvature.

**Karras et al. (2022) and the importance of scheduling:**
Even in DDPM, the NOISE schedule matters more than the number of steps. Karras showed that a carefully chosen noise schedule can get DDIM to converge in 10-20 steps. Flow matching makes this explicit by DESIGNING the path to be straight, not by tuning the schedule to approximate a straight path.

**Classifier-free guidance with flow matching:**
Same trick as diffusion: train the model both conditionally and unconditionally (by dropping the condition 10% of the time). At sampling:
$$v_{cfg} = (1 + w) \cdot v_\theta(x_t, t, c) - w \cdot v_\theta(x_t, t, \emptyset)$$
where $w$ is the guidance scale (typically 3-7). This sharpens the generation by amplifying the difference between conditional and unconditional velocity.

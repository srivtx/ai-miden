## What Is Dreamer?

---

### The Problem

High-dimensional observations like pixels make long-term planning intractable. A raw image has thousands of dimensions, and predicting future pixels accumulates blur and error over time. Model-based reinforcement learning needs a compact, stable representation where imagination is both cheap and accurate. How do you plan effectively when the world is made of pixels and every imagined frame drifts further from reality?

---

### Definition

**Dreamer** is a model-based RL algorithm that learns a latent dynamics model from high-dimensional observations. It uses a Recurrent State-Space Model (RSSM) to encode observations into a compact latent state, predict future latent states conditioned on actions, and train policy and value functions entirely on imagined latent trajectories.

**How it works:**
```
Pixel observation → Encoder → Latent state z_t
z_t + Action a_t → RSSM → Predicted z_{t+1} + Predicted reward
Policy trained on imagined latent rollouts (no real environment steps)
Value function trained on predicted returns from imagined trajectories
Result: sample-efficient policy learning from pixels
```

**Key techniques:**
- **RSSM:** combines deterministic recurrent memory with stochastic latent states to capture both predictable dynamics and uncertainty
- **Latent imagination:** the policy learns by dreaming in compact latent space without decoding pixels
- **Straight-through gradients:** enables backpropagation through discrete latent variables for end-to-end training

**Why this matters:**
- Achieves strong control performance with 100x fewer environment steps than model-free methods
- Plans in latent space, avoiding the computational cost of decoding and predicting raw pixels
- The latent model can generalize to unseen visual backgrounds and lighting conditions

---

### Real-Life Analogy

Dreamer is like a chess master who thinks several moves ahead in their mind. Instead of physically moving pieces on a board to test every possibility, they maintain a compact mental representation of the game state. They imagine sequences of moves and their consequences without touching the board. The mental model is simpler than the physical board -- it tracks piece positions and threats, not wood grain or lighting -- but it is sufficient for strategy.

The trade-off is that the chess master might miss physical tells or board irregularities because their mental model abstracts them away. If a piece is slightly heavier than usual, the mental model does not capture it. Similarly, Dreamer's latent space discards pixel-level detail that might matter for some tasks. The abstraction enables efficient planning but creates a blind spot for fine-grained visual cues.

---

### Tiny Numeric Example

**Pixel observation:** 64x64x3 = 12,288 dimensions
**RSSM latent state:** 32 dimensions

**Planning cost comparison per imagined step:**
```
Pixel-level model:
  12,288 inputs → predict 12,288 outputs
  ≈ 151,000,000 multiply-adds per step

Latent model:
  32 inputs → predict 32 dimensions + reward
  ≈ 1,024 multiply-adds per step

Speedup: ~150,000x per imagined step
```

**Performance on control task (100 episodes):**
```
Model-free (pixels):
  Reward = 450
  Environment steps = 1,000,000

Dreamer (latent):
  Reward = 520
  Environment steps = 10,000
```

**Sample efficiency:**
```
Dreamer achieves 15% higher reward using 1% of the environment interactions.
```

The compression from 12,288 pixels to 32 latent dimensions makes long-horizon imagination tractable.

---

### Common Confusion

1. **"Dreamer is a generative model for creating random images."** It is a controlled, action-conditioned predictive model used for planning and policy optimization, not an unconditional image generator.

2. **"Dreamer eliminates environment interaction completely."** It drastically reduces it, but still requires real rollouts to train and periodically update the world model.

3. **"The latent space is human-interpretable."** Like most neural latent spaces, RSSM states are distributed and not easily mapped to concrete concepts such as "position" or "velocity."

4. **"Dreamer works only for visual tasks."** While designed for pixels, the RSSM architecture works for any high-dimensional observation, including proprioception vectors, audio spectrograms, and sensor fusion inputs.

5. **"Dreamer and MPC are the same thing."** Dreamer is a full RL algorithm that includes a world model, policy, and value learning trained end-to-end. MPC is a control strategy that can use any model.

6. **"Imagined rollouts are as good as real experience."** They are useful but suffer from model bias; imagined rewards diverge from real rewards over long horizons.

7. **"Dreamer requires a powerful GPU to be useful."** The original implementation used GPUs, but the core idea -- latent imagination -- is hardware-agnostic and has been scaled down to edge devices and microcontroller implementations.

---

### Where It Is Used in Our Code

`src/phase109/phase109_world_models.py` — We simulate the core idea of Dreamer by learning a compact linear dynamics model from raw state observations and training a policy through imagined rollouts in that compressed state space. While our NumPy implementation uses a linear approximation rather than a full RSSM, it demonstrates the same principle: plan in a learned latent model rather than in raw high-dimensional observations.

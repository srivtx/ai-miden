## Phase 40 Summary: Flow Matching & Diffusion Transformers

**The Question:** "DDPM diffusion works but trains indirectly (predict noise) and needs 1000 sampling steps. Is there a more direct, faster way to generate data?"

---

### What We Learned

1. **Flow Matching**
   - Trains a model to predict the velocity field that transforms noise into data
   - Direct objective: `L = ||v_θ(x_t, t) - u_t||²`
   - Rectified flow uses straight-line paths: `x_t = (1-t) × data + t × noise`
   - Target velocity is constant: `u = noise - data`

2. **Diffusion Transformers (DiT)**
   - Replaces U-Net backbone with a Transformer
   - Images are patchified into tokens (like ViT)
   - Global attention enables coherent long-range structure
   - Scales better to large models than convolutional U-Nets

3. **Rectified Flow**
   - Uses straight-line optimal transport paths
   - Simpler to learn and faster to sample than curved paths
   - Reflow iterations can further straighten the flow

4. **ODE Solvers**
   - Euler: simple but needs many steps
   - Midpoint/RK4: higher accuracy with fewer steps
   - Adaptive solvers adjust step size based on local smoothness
   - Flow matching needs ~10–50 steps vs. DDPM's ~1000

---

### Results

- A velocity MLP learned to transform Gaussian noise into a 2D swirl pattern
- Training loss converged to ~0.9 (MSE on velocity predictions)
- Euler 20 steps produced smooth, accurate samples
- RK4 10 steps matched quality with fewer model evaluations
- Flow trajectories visualized the path from noise to data

---

### Phase 40 Files

| File | Purpose |
|---|---|
| `docs/phase40/what_is_flow_matching.md` | Core concept: velocity field for noise-to-data transformation |
| `docs/phase40/what_is_diffusion_transformer.md` | Transformer backbone replacing U-Net in generative models |
| `docs/phase40/what_is_rectified_flow.md` | Straight-line paths and optimal transport |
| `docs/phase40/what_is_ode_solver.md` | Numerical integration methods for sampling |
| `src/phase40/phase40_flow_matching.py` | NumPy 2D flow matching with Euler/Midpoint sampling |
| `src/phase40/phase40_flow_matching_colab.py` | PyTorch flow matching with RK4 and trajectory viz (Colab T4) |

---

### Connects To

- **Phase 31 (Diffusion):** Flow matching is the modern replacement for DDPM training
- **Phase 28 (ViT):** DiT applies Vision Transformer concepts to generative modeling
- **Phase 18 (Transformer):** DiT uses standard Transformer blocks with adaptive conditioning

---

### What You Should Remember

> **Flow matching is like a sculptor with a motorized tool.** Instead of chipping randomly and checking (DDPM), they learn the optimal carving path — which direction to move each point at every moment. The motorized tool adapts its speed to the complexity of each region, finishing in 20 smooth passes instead of 1000 tentative chips.

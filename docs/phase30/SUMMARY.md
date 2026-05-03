## Phase 30 Summary: Generative Models — GANs

**The Question:** "My VAE produces blurry images. How do I generate sharp, realistic ones?"

---

### What We Learned

1. **Generator**
   - Neural network that transforms random noise into fake data
   - Never sees real images directly; only receives gradients from discriminator
   - Goal: produce outputs so realistic the discriminator cannot tell they are fake

2. **Discriminator**
   - Binary classifier: real vs. fake
   - Provides rich, adaptive feedback to the generator
   - Usually discarded after training; only the generator is kept

3. **Minimax Game**
   - Discriminator maximizes accuracy at spotting fakes
   - Generator minimizes discriminator accuracy (tries to fool it)
   - Creates a competitive arms race that pushes both to improve
   - Theoretical goal: Nash equilibrium where D(x) = 0.5 for all samples

4. **Mode Collapse**
   - Generator learns only a small subset of possible outputs
   - Caused by discriminator being too good in local regions
   - Solutions: minibatch discrimination, WGAN, experience replay
   - Diffusion models largely avoid this problem

---

### Results

- Toy GAN learned to generate 2D points matching a target distribution
- Generator and discriminator losses showed adversarial dynamic
- Demonstrated mode collapse: generator converged to single cluster
- Non-saturating loss stabilized training vs. vanilla minimax

---

### Phase 30 Files

| File | Purpose |
|---|---|
| `docs/phase30/what_is_generator.md` | Creating fake data from noise |
| `docs/phase30/what_is_discriminator.md` | Detecting real vs. fake |
| `docs/phase30/what_is_minimax_game.md` | Two networks competing |
| `docs/phase30/what_is_mode_collapse.md` | Generator producing limited variety |
| `src/phase30/phase30_gan.py` | Toy 2D GAN demonstration |
| `src/phase30/phase30_gan_colab.py` | Real GAN on MNIST (Colab T4) |

---

### Connects To

- **Phase 29:** VAEs — We learned to generate blurry data. Now we make it sharp.
- **Phase 31:** Diffusion Models — GANs are unstable. Is there a more reliable way?

### 1. Why it exists (THE PROBLEM first)
We need a way to train generative models without adversarial training (GANs are unstable) and without blurry reconstructions (VAEs average pixels). The breakthrough insight from diffusion models is surprisingly simple: instead of learning to generate images directly, learn the reverse of a destruction process. If we can teach a model to undo noise, we can start from pure noise and iteratively create an image.

### 2. Definition (very simple)
Forward Diffusion is the process of gradually adding Gaussian noise to a clean image across T timesteps until the image becomes indistinguishable from pure random noise. It is a fixed, predefined process — no neural network is involved. The noise is added according to a schedule that controls how much noise is injected at each step.

### 3. Real-life analogy
A photograph left out in the sun. At first, the colors fade slightly. After a week, details blur. After a month, faces are unrecognizable. After a year, it is just a white rectangle. Forward diffusion is this fading process, but mathematically precise and reversible in principle.

### 4. Tiny numeric example
Clean image pixel: x_0 = 0.8

Noise schedule: beta_t = 0.1 for all steps (simplified)

Step 1: x_1 = sqrt(1 - beta) * x_0 + sqrt(beta) * epsilon
       = sqrt(0.9) * 0.8 + sqrt(0.1) * 0.3
       = 0.949 * 0.8 + 0.316 * 0.3
       = 0.759 + 0.095 = 0.854

Step 2: x_2 = sqrt(0.9) * x_1 + sqrt(0.1) * (-0.5)
       = 0.949 * 0.854 + 0.316 * (-0.5)
       = 0.810 - 0.158 = 0.652

Step 10: x_10 ≈ 0.15 (mostly noise, faint trace of original)

Step 100: x_100 ≈ pure noise ~ N(0, 1)

The key property: we can jump directly from x_0 to x_t in ONE step using the closed-form formula:
```
x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon
```
where alpha_bar_t is the cumulative product of (1 - beta) up to step t.

### 5. Common confusion
- **Forward diffusion does not learn anything.** It is a fixed mathematical process. The neural network only learns the REVERSE process.
- **It is not data-dependent.** The same noise schedule is applied to all images. A photo of a cat and a photo of a dog both follow the same diffusion trajectory to noise.
- **The closed-form sampling is crucial.** Without it, we would need T sequential steps just to create a noisy training example. With it, we can sample x_t directly from x_0 in O(1).
- **Beta schedules matter.** A linear schedule (beta grows from 0.0001 to 0.02) is common. Cosine schedules work better for high-resolution images. The schedule controls how "quickly" information is destroyed.
- **Forward diffusion is invertible in theory.** Because each step adds Gaussian noise, the reverse conditional distribution p(x_{t-1} | x_t) is also Gaussian. This is why the reverse process can be learned.

### 6. Where it is used in our code
`src/phase31/phase31_diffusion.py` implements the forward diffusion process on 1D signals, showing how a clean pattern gradually turns into pure noise.

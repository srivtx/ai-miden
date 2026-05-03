### 1. Why it exists (THE PROBLEM first)
If forward diffusion turns an image into noise, the obvious question is: can we run it backward? Start from noise and gradually recover the image? The reverse process is not trivial — we cannot simply subtract the same noise because we do not know what noise was added. But we CAN train a neural network to predict the noise that was added, and then subtract that prediction.

### 2. Definition (very simple)
Reverse Diffusion is the learned process of starting from pure noise and iteratively denoising across T timesteps to produce a clean image. A neural network (typically a U-Net) predicts the noise that was added at each step. By subtracting the predicted noise, we take one step closer to the original image.

### 3. Real-life analogy
A photograph restorer working on a badly damaged photo. The restorer does not know exactly what dust and scratches were added, but after studying thousands of damaged photos, they learn to recognize patterns: "this smudge is probably a fingerprint," "this blur is probably water damage." They remove the damage layer by layer, and after many careful steps, the original photo emerges.

### 4. Tiny numeric example
At step t, we have noisy image x_t. We want to estimate x_{t-1}.

The neural network predicts: noise_pred = epsilon_theta(x_t, t)

Then we compute:
```
x_{t-1} = (x_t - sqrt(1 - alpha_bar_t) * noise_pred) / sqrt(alpha_bar_t)
```

This is the "predicted x_0" formulation. A more common formulation is:
```
x_{t-1} = (x_t - beta_t / sqrt(1 - alpha_bar_t) * noise_pred) / sqrt(alpha_t)
          + sigma_t * random_noise
```

Concrete numbers:
- x_t = 0.5
- t = 50
- Network predicts: noise_pred = 0.3
- alpha_bar_t = 0.6

Predicted clean image:
- x_0_pred = (0.5 - sqrt(0.4) * 0.3) / sqrt(0.6)
- x_0_pred = (0.5 - 0.632 * 0.3) / 0.775
- x_0_pred = (0.5 - 0.190) / 0.775 = 0.400

If the true x_0 was 0.42, our prediction is close! The error (0.02) is what the network learns to minimize.

### 5. Common confusion
- **The network predicts NOISE, not the clean image.** Early diffusion models tried to predict x_0 directly, but predicting noise (epsilon) is more stable and works better.
- **The reverse process is stochastic.** Unlike forward diffusion which is deterministic, reverse diffusion adds a small amount of random noise at each step. This is why running the same prompt twice produces slightly different images.
- **DDPM vs. DDIM.** DDPM (Denoising Diffusion Probabilistic Models) is the original. DDIM (Denoising Diffusion Implicit Models) makes the reverse process deterministic, allowing faster sampling with fewer steps.
- **Classifier guidance.** You can bias the sampling toward a class (like "cat") by adding a gradient from a classifier. This trades diversity for fidelity to the class.
- **Classifier-free guidance.** Instead of a separate classifier, train the diffusion model with and without class labels. At inference, extrapolate between the unconditional and conditional predictions. This is what Stable Diffusion uses.

### 6. Where it is used in our code
`src/phase31/phase31_diffusion.py` implements a toy reverse diffusion process where a simple network learns to predict noise added to 1D signals, then uses those predictions to denoise.

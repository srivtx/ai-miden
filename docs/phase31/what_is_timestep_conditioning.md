### 1. Why it exists (THE PROBLEM first)
A diffusion model processes images at many different noise levels — from almost-clean (t=1) to pure-static (t=1000). The same pixel value means completely different things at different timesteps. At t=1, a value of 0.8 means "bright pixel." At t=1000, a value of 0.8 is just random noise. The network needs to know WHICH timestep it is processing so it can interpret the input correctly.

### 2. Definition (very simple)
Timestep Conditioning is the technique of telling the diffusion network which timestep t it is currently denoising. This is done by embedding the timestep as a vector and injecting it into the network (usually via addition or multiplication with intermediate feature maps). Without this, the network would not know whether to remove a little noise or a lot.

### 3. Real-life analogy
A photo restorer who knows how damaged the photo is before they start working. If the photo is 10% damaged, they use a soft brush and gentle cleaning. If it is 90% damaged, they use aggressive chemical treatments and heavy reconstruction. The restorer's strategy changes dramatically based on the damage level. Timestep conditioning is like handing the restorer a card that says "Damage level: 73%" before each step.

### 4. Tiny numeric example
Timestep t = 50 (out of 1000 total steps)

Step 1: Embed t into a vector
- t_embed = [sin(50 / 100), cos(50 / 100), 50 / 1000] = [0.479, 0.878, 0.05]

Step 2: Inject into the network
- At a hidden layer with features h = [0.3, -0.2, 0.8, 0.1]
- Add t_embed (broadcasted): h' = h + t_embed = [0.779, 0.678, 0.85, 0.1]
- The network now knows it is at an early timestep and should be conservative

At t = 950:
- t_embed = [sin(950 / 100), cos(950 / 100), 950 / 1000] = [-0.926, -0.377, 0.95]
- h' = h + t_embed = [-0.626, -0.577, 1.75, 0.1]
- The network knows it is at a late timestep and should be aggressive

The network learns to associate different t_embed values with different denoising strategies.

### 5. Common confusion
- **Timestep embedding is not just the raw integer t.** Using t=50 directly would not work well because the network needs a smooth, high-dimensional representation. Sinusoidal embeddings (like Transformer positional encodings) are standard.
- **It is not the same as positional encoding in Transformers.** Both use sinusoidal functions, but positional encodings tell the model WHERE in a sequence, while timestep embeddings tell the model HOW NOISY the image is.
- **Different embeddings can be used.** Some models use learned embeddings (trainable vectors for each t). Others use Fourier features. Sinusoidal embeddings are popular because they generalize to timesteps not seen during training.
- **It can be injected at multiple layers.** Not just at the input — timestep embeddings are often added to every residual block in the U-Net so the network can adapt its behavior at all scales.
- **The same U-Net handles all timesteps.** Unlike GANs where the generator is fixed after training, the diffusion U-Net is called T times with different t values during a single generation.

### 6. Where it is used in our code
`src/phase31/phase31_diffusion.py` adds a simple timestep embedding to a toy diffusion model, showing how the network's behavior changes based on the timestep.

### 1. Why it exists (THE PROBLEM first)
Diffusion models need to process images at multiple scales. Early timesteps have almost no structure (pure noise), while late timesteps have fine details that need precise editing. A standard feedforward network processes everything at the same resolution. We need an architecture that can capture both global structure ("there is a face in the center") and local details ("the eye has a glint").

### 2. Definition (very simple)
A U-Net is a convolutional neural network shaped like the letter "U." It has an **encoder** (downsampling path) that compresses the image into a compact representation, and a **decoder** (upsampling path) that expands it back to the original resolution. Skip connections copy features from the encoder directly to the decoder at matching resolutions, preserving fine-grained details.

### 3. Real-life analogy
An architect designing a house. First, they sketch the overall layout at small scale (encoder: "kitchen here, bedroom there"). Then they zoom in and add details to each room (decoder: "this window faces south"). The skip connections are like the architect keeping their rough sketches visible while drawing the detailed plans — they constantly refer back to the big picture so the details align with the overall structure.

### 4. Tiny numeric example
Input image: 8x8 pixels

Encoder path (downsampling):
- 8x8 -> Conv -> 8x8
- MaxPool -> 4x4
- Conv -> 4x4
- MaxPool -> 2x2 (bottleneck)

Bottleneck (most compressed):
- 2x2 representation captures global structure

Decoder path (upsampling):
- UpSample -> 4x4 + skip from encoder 4x4
- Conv -> 4x4
- UpSample -> 8x8 + skip from encoder 8x8
- Conv -> 8x8 (output: predicted noise)

The skip connection at 4x4 copies the encoder's 4x4 features and concatenates them with the decoder's 4x4 features. This preserves local details that would otherwise be lost in the bottleneck.

### 5. Common confusion
- **U-Net is not just for diffusion.** It was originally invented for biomedical image segmentation. It works for any image-to-image task: segmentation, denoising, super-resolution, and diffusion.
- **The bottleneck is NOT the latent space of a VAE.** In a VAE, the bottleneck IS the compressed representation. In a U-Net, the bottleneck is just the narrowest point; the skip connections carry most of the information.
- **Skip connections are essential.** Without them, the U-Net would be a plain autoencoder and would produce blurry outputs. The skip connections are what make U-Net sharp.
- **U-Net can be huge.** Modern diffusion U-Nets have hundreds of millions of parameters with many resolution levels, attention blocks, and residual connections. The basic shape is the same, but the scale is enormous.
- **U-Net predicts noise, not the image.** In diffusion, the input to the U-Net is the noisy image, and the output is the predicted noise. The clean image is recovered by subtraction, not by direct generation.

### 6. Where it is used in our code
`src/phase31/phase31_diffusion.py` implements a tiny U-Net on 1D signals with skip connections, showing how the bottleneck compresses information and the skip connections preserve local detail.

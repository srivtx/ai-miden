### 1. Why it exists (THE PROBLEM first)
Raw data like images or audio is extremely high-dimensional. A 28x28 grayscale MNIST image has 784 numbers, and a color photo has millions. Training models directly on this raw data is slow, expensive, and prone to overfitting. We need a way to compress data into a much smaller, meaningful representation that captures the essence while discarding noise.

### 2. Definition (very simple)
An Autoencoder is a neural network with two parts: an **Encoder** that compresses input into a small vector (the latent code), and a **Decoder** that reconstructs the original input from that code. The network is trained to make the output as similar to the input as possible, forcing it to learn an efficient compression.

### 3. Real-life analogy
A ZIP file. You have a 100-page document (the input). A ZIP program compresses it to 1 MB (the encoder + latent code). Later, you unzip it and get back the original 100-page document (the decoder + reconstruction). The ZIP format does not understand the content, but it finds patterns that allow lossless or near-lossless compression.

### 4. Tiny numeric example
Input image (flattened): [0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6] (8 pixels)

Encoder (2 hidden units):
- Hidden = [0.5, 0.5] (compressed to 2 numbers)

Decoder (reconstructs 8 pixels):
- Output = [0.15, 0.85, 0.25, 0.75, 0.35, 0.65, 0.45, 0.55]

Reconstruction error = mean of (input - output)^2
= (0.05^2 + 0.05^2 + 0.05^2 + 0.05^2 + 0.05^2 + 0.05^2 + 0.05^2 + 0.05^2) / 8 = 0.0025

The autoencoder learned to compress 8 pixels into 2 numbers and almost perfectly reconstruct them.

### 5. Common confusion
- **An autoencoder is not a classifier.** It does not predict labels. It predicts the input itself. The latent code is a byproduct, not the goal.
- **The latent code is not unique.** Many different encodings might reconstruct the same input. The autoencoder does not enforce any structure on the latent space.
- **Perfect reconstruction is easy with a large latent code.** If the latent code is the same size as the input, the network can simply copy. The interesting case is when the code is MUCH smaller — the network must learn what matters.
- **Denoising autoencoders exist.** You can train an autoencoder to reconstruct clean images from noisy inputs. This forces it to learn robust features.
- **Autoencoders alone cannot generate new data.** They can only encode what they have seen. To generate new images, you need a Variational Autoencoder (VAE) or a GAN.

### 6. Where it is used in our code
`src/phase29/phase29_vae.py` implements a simple autoencoder that compresses 8-pixel patterns into 2 latent numbers and reconstructs them, demonstrating the compression-reconstruction cycle.

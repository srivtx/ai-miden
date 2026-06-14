# What Is an Autoencoder?

**The Problem:** You have a 28x28 image (784 dimensions). You want a smaller representation (say, 32 dimensions) that captures the *essential* information. Then you want to reconstruct the original image from this small representation. This is *compression*. If you can compress and decompress well, you have a useful representation. Autoencoders are neural networks trained to do exactly this.

**Definition:** An *autoencoder* is a neural network with two parts:
- An *encoder* $f_\phi: \mathcal{X} \to \mathcal{Z}$ that maps input $x$ to a latent $z = f_\phi(x)$.
- A *decoder* $g_\theta: \mathcal{Z} \to \mathcal{X}$ that maps latent $z$ back to a reconstruction $\hat{x} = g_\theta(z)$.

The network is trained to minimize a *reconstruction loss*:
$$\mathcal{L}(\theta, \phi) = \mathbb{E}_{x \sim p_{\text{data}}}[\| x - g_\theta(f_\phi(x)) \|^2]$$

(or any other distance, like binary cross-entropy for binary images).

**How It Works (Step-by-Step):**

1. **Encoder**: a neural network that takes the input and produces a small vector. For images, this is usually a CNN. The output is the "latent code" or "embedding."
2. **Latent space**: the space of possible latent codes. If the encoder outputs 32-dim vectors, the latent space is $\mathbb{R}^{32}$.
3. **Decoder**: a neural network that takes a latent code and produces a reconstruction. For images, this is usually a "transposed CNN" (also called a deconvolution network).
4. **Reconstruction loss**: how close the reconstruction is to the input. MSE for continuous data, BCE for binary data.
5. **Training**: minimize the reconstruction loss over the training set. Standard backprop.
6. **Inference (encoding)**: pass a new image through the encoder. Get the latent code.
7. **Inference (decoding)**: pass any latent code through the decoder. Get a "reconstruction."

**Key insight**: the autoencoder is forced to *compress* the input into a small latent, then *decompress* it. If the reconstruction is good, the latent must contain the *essential* information about the input. This is *representation learning*.

**Variants**:

- **Vanilla autoencoder**: as above. Reconstructs the input.
- **Denoising autoencoder (Vincent 2008)**: input is corrupted with noise; reconstruction is the clean input. Forces the network to learn robust features.
- **Sparse autoencoder**: add a sparsity penalty on the latent. Forces only a few latent dimensions to be active.
- **Contractive autoencoder**: penalize the Jacobian of the encoder. Forces the latent to be locally smooth.
- **Variational autoencoder (VAE)**: add a KL regularization term. See `what_is_variational_autoencoder.md`.

**Real-life analogy:** An autoencoder is like a *translator* between two languages. The encoder translates from English (high-dimensional) to French (low-dimensional). The decoder translates from French back to English. If the round-trip translation is good, the French version must contain the same meaning. You can use the French version as a compact representation of the English.

**Tiny numeric example:**

```python
import torch
import torch.nn as nn

class Autoencoder(nn.Module):
    def __init__(self, input_dim=784, latent_dim=32):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Linear(256, input_dim),
            nn.Sigmoid()  # For [0, 1] pixel values
        )

    def forward(self, x):
        z = self.encoder(x)
        x_hat = self.decoder(z)
        return x_hat, z

# Train on MNIST
model = Autoencoder()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.BCELoss()

for epoch in range(10):
    for x, _ in train_loader:
        x = x.view(-1, 784)
        x_hat, z = model(x)
        loss = criterion(x_hat, x)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

**Common confusion:**

- "Autoencoders are for compression." Yes, but they are *lossy* and *data-specific*. They are not general-purpose compressors like zip. They only work on data similar to the training set.
- "The latent is interpretable." Sometimes. With a vanilla autoencoder, no. With a sparse or contractive autoencoder, partially. With a VAE with disentangled priors (β-VAE), yes — each latent dimension can correspond to a meaningful factor of variation.
- "Autoencoders are generative." Only if the decoder is *good* outside the training distribution. A vanilla autoencoder trained on faces will give garbage if you sample a random latent. A VAE is a proper generative model because of the KL regularization.
- "Reconstruction loss is MSE." For continuous data in [0, 1], BCE often works better than MSE. For images in [-1, 1], MSE is fine. For text, cross-entropy with a softmax output.
- "Autoencoders always converge." Yes, the trivial solution is to copy the input (latent = identity). But this requires the latent to be at least as large as the input. If the latent is *smaller* (the usual case), the network is forced to learn a meaningful compression.
- "Autoencoders are unsupervised." Yes, mostly. The reconstruction target is the input itself. But you can add supervised losses (e.g., classify the latent).

**Key properties:**

- **Self-supervised**: no labels needed. The training signal is the input itself.
- **Bottleneck**: the latent is smaller than the input. This forces compression.
- **Reconstruction loss**: how close $\hat{x}$ is to $x$.
- **Identity shortcut**: if the latent is large enough, the network can learn the identity function. Make the latent small to force compression.
- **No explicit regularization**: vanilla autoencoders don't have a KL term or sparsity term. The bottleneck is the only regularizer.

**Tech comparison:**

| Method | Latent | Generative? | Use case |
|---|---|---|---|
| PCA | Linear | No | Linear dimensionality reduction |
| Autoencoder | Nonlinear | No | Nonlinear compression |
| Denoising AE | Nonlinear | No | Robust features |
| VAE | Nonlinear | Yes | Generative model |
| Sparse AE | Nonlinear | Partial | Interpretable features |
| Contractive AE | Nonlinear | Partial | Smooth features |

**Connection to generative models:** The autoencoder is the *foundation*. The VAE (next file) is the autoencoder made generative. The encoder of a VAE is the same as a regular autoencoder; the difference is the *training objective* and the *regularization* of the latent space.

# Part 1: Autoencoders and VAEs

> The simplest generative model. A neural network that compresses an image into a small vector, then reconstructs it. By adding noise to the compressed vector, you get a *variational* autoencoder that can sample new images.

---

## The three files in this part

| File | One-line summary |
|---|---|
| `what_is_autoencoder.md` | A neural network that compresses and reconstructs. The encoder-decoder architecture. |
| `what_is_variational_autoencoder.md` | An autoencoder that samples from a continuous latent space. The ELBO objective. The reparameterization trick. |
| `vae_mnist.py` | A runnable VAE on MNIST, implemented in NumPy. |
| `vae_mnist_colab.py` | The same VAE in PyTorch, for Colab. |

## Reading order

1. **`what_is_autoencoder.md`**. The encoder-decoder architecture. Reconstruction loss.
2. **`what_is_variational_autoencoder.md`**. Add a KL term. The reparameterization trick. How to sample.
3. **`vae_mnist.py`**. Run it. See the reconstructions and samples.

## The synthesis

A Variational Autoencoder is two things:
1. An *encoder* $q_\phi(z | x)$ that compresses an image to a small vector.
2. A *decoder* $p_\theta(x | z)$ that reconstructs the image from the vector.

Training maximizes the ELBO:
$$\text{ELBO} = \mathbb{E}_{q_\phi(z | x)}[\log p_\theta(x | z)] - D_{KL}(q_\phi(z | x) \| p(z))$$

The first term says "reconstruct well." The second says "stay close to the prior." Together, they force the encoder to map images to a *structured* latent space — one where nearby points decode to similar images. After training, you can sample by:
1. Sample $z \sim p(z) = \mathcal{N}(0, I)$.
2. Decode: $x = p_\theta(x | z)$.

The result is a *new* image that looks like the training data.

## Why VAEs matter

VAEs are not the best generative model today (diffusion beats them on most benchmarks). But they are:
- The *simplest* modern generative model.
- The *cleanest* theoretical framework (explicit ELBO, principled regularization).
- The *foundation* for understanding diffusion and other models.

If you understand VAEs, you have a head start on understanding everything else.

## Where this leads

After Part 1, you understand *how to train* a generative model with latent variables. Part 2 (Diffusion) drops the explicit encoder/decoder and uses the score instead. Part 3 (Latent Diffusion) combines VAEs and diffusion for state-of-the-art image generation. Part 4 (Video) extends to time.

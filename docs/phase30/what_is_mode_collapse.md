### 1. Why it exists (THE PROBLEM first)
A generator could learn to produce one really good image and repeat it endlessly. The discriminator might classify that single image as real with high confidence, so the generator has no incentive to diversify. The result: the model generates the same output (or a tiny handful of outputs) for every random input. This is catastrophic for a generative model, which should produce diverse, varied outputs.

### 2. Definition (very simple)
Mode Collapse is a training failure in GANs where the generator learns to produce only a small subset of possible outputs, ignoring most of the diversity present in the real data. Instead of modeling the full distribution, the generator finds one or a few "easy wins" that consistently fool the discriminator and stops exploring.

### 3. Real-life analogy
A forger who only knows how to paint one painting really well — say, the Mona Lisa. Every time the inspector visits, the forger shows another Mona Lisa. The inspector eventually recognizes the trick, but by then the forger has already sold a hundred copies. The forger never learned to paint any other masterpiece. The "mode" of the art distribution (all possible paintings) has "collapsed" to a single point.

### 4. Tiny numeric example
Real data distribution: mixture of two Gaussians centered at (-2, 0) and (2, 0).

Good generator: produces points around both centers, matching the real distribution.

Collapsed generator: produces points only around (2, 0). The discriminator eventually learns that anything near (-2, 0) is definitely real (since the generator never goes there), but the generator does not receive strong enough signal to explore the left cluster.

Worse collapse: the generator cycles. For a few batches it produces points near (2, 0). The discriminator adapts. Then it switches to (-2, 0). The discriminator adapts again. It never stably covers both.

### 5. Common confusion
- **Mode collapse is not the same as low quality.** A generator in mode collapse might produce stunningly realistic images — just all of the same person, or the same dog breed. Quality is high; diversity is zero.
- **It is caused by the discriminator being too good too locally.** If the discriminator perfectly rejects everything except one type of fake, the generator has no gradient pointing toward unexplored regions.
- **Solutions exist but are not perfect.** Techniques include: minibatch discrimination (the discriminator sees multiple samples at once and penalizes similarity), WGAN (uses a critic instead of a classifier), unrolled GANs (the generator anticipates the discriminator's update), and experience replay (keeping a buffer of past generated samples).
- **Diffusion models largely avoid mode collapse.** Because diffusion models learn to denoise rather than fool a discriminator, they do not suffer from this adversarial pathology. This is one reason diffusion has largely replaced GANs for image generation.
- **Mode collapse can be subtle.** A generator might produce 100 different faces, but all of them might be young, smiling, and facing forward. The mode has not fully collapsed to one point, but it is still much narrower than the real distribution.

### 6. Where it is used in our code
`src/phase30/phase30_gan.py` demonstrates mode collapse by showing how a toy GAN trained on a mixture of Gaussians sometimes converges to only one cluster, and visualizes the failed diversity.

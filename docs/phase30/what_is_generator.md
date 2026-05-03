### 1. Why it exists (THE PROBLEM first)
VAEs produce blurry images because their loss function (mean squared error) averages over pixel space. The model learns to be "safe" by outputting fuzzy means rather than crisp details. We need a different approach that judges images by how realistic they look, not by pixel-wise similarity. The key insight: instead of measuring reconstruction error, train a second network to tell whether an image is real or fake, and make the generator fool that network.

### 2. Definition (very simple)
A Generator is a neural network that creates fake data from random noise. It takes a random vector z (like rolling dice) and transforms it into an image, audio clip, or text sample. Its goal is to produce outputs so realistic that a human (or another network) cannot tell they are fake.

### 3. Real-life analogy
An art forger who creates fake paintings. The forger starts by randomly splashing paint on canvas (noise). Over time, they learn which brush strokes, colors, and compositions look like a real Monet. They never see an exact target painting; they only know whether the art inspector believes their work is authentic.

### 4. Tiny numeric example
Generator input: z = [0.3, -0.7, 1.2] (3 random numbers)

Generator network (simplified):
- Hidden layer: h = ReLU(W1 @ z + b1) = [0.5, 0.8]
- Output layer (2 pixels): x_fake = sigmoid(W2 @ h + b2) = [0.92, 0.15]

The generator turned 3 random numbers into a 2-pixel "image." There is no target image to compare against. The only feedback comes from the discriminator saying "real" or "fake."

### 5. Common confusion
- **The generator does not see real data during training.** Unlike a VAE decoder, the generator never receives a real image as input. It only receives random noise and gradients from the discriminator.
- **Bigger is not always better.** A generator that is much more powerful than the discriminator will always win, and the discriminator will never learn to give useful feedback. They must be roughly matched in capacity.
- **The input noise matters.** Different random seeds produce different outputs. If the noise distribution is too simple (e.g., uniform instead of Gaussian), the generator may produce lower-quality or less diverse images.
- **Generators can be used standalone after training.** Once trained, you discard the discriminator and use only the generator to create new images from random noise.
- **They are not limited to images.** Generators can create music, 3D models, molecules, and even fake tabular data for privacy-preserving machine learning.

### 6. Where it is used in our code
`src/phase30/phase30_gan.py` implements a toy generator that transforms 2D random noise into 2D points, trying to match the distribution of real data points.

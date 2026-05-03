### 1. Why it exists (THE PROBLEM first)
Traditional training uses a single fixed loss function (like MSE or cross-entropy). But for generation, what "good" means changes as the model improves. Early on, any vaguely structured output is impressive. Later, only photorealistic details count. We need a dynamic training signal that automatically adapts its difficulty as the generator gets better.

### 2. Definition (very simple)
The Minimax Game is the adversarial training objective of GANs. The Discriminator tries to maximize its accuracy at distinguishing real from fake. The Generator tries to minimize the Discriminator's accuracy — or equivalently, maximize the chance that the Discriminator mistakes fakes for real. This creates a competitive arms race where both networks push each other to improve.

### 3. Real-life analogy
A counterfeiter and the police. The counterfeiter makes fake money. The police learn to spot it. The counterfeiter improves their technique. The police upgrade their detection tools. The counterfeiter finds new loopholes. Back and forth, both get better. The counterfeiter does not need to know what "perfect money" looks like mathematically; they only need to know whether the police caught them.

### 4. Tiny numeric example
Discriminator score on a fake sample: D(x_fake) = 0.3 (thinks it is 30% likely real)

Generator's goal (standard formulation):
- Maximize log(D(x_fake)) = log(0.3) = -1.20
- Or equivalently, minimize -log(D(x_fake)) = 1.20

Discriminator's goal:
- For real sample (D(x_real) = 0.9): maximize log(0.9) = -0.105
- For fake sample (D(x_fake) = 0.3): maximize log(1 - 0.3) = log(0.7) = -0.357
- Total: maximize (-0.105) + (-0.357) = -0.462
- Or minimize: 0.462

Mathematically, the value function V(D, G) is:
```
min_G max_D V(D, G) = E[log D(x_real)] + E[log(1 - D(G(z)))]
```

The discriminator maximizes V. The generator minimizes V. They play a zero-sum game.

### 5. Common confusion
- **It is not truly zero-sum in practice.** The generator and discriminator do not share a single loss value. They have separate losses and separate optimizers. The "minimax" is the conceptual framework, not the implementation.
- **The generator loss can be unstable.** Early in training, when the discriminator easily spots fakes, D(G(z)) is near 0, and log(0) explodes to negative infinity. This is why practitioners often use the non-saturating loss: maximize log(D(G(z))) instead of minimize log(1 - D(G(z))).
- **Training does not converge to a fixed point.** Unlike supervised learning where loss goes to zero, GAN training is an equilibrium. The ideal state is when D(x) = 0.5 for all samples — the discriminator is completely confused.
- **Nash equilibrium is the theoretical goal.** In game theory, a Nash equilibrium is when neither player can improve by changing strategy alone. For GANs, this is when the generator perfectly matches the real data distribution.
- **The game can be unfair.** If the discriminator is too strong, the generator gets no gradient signal and stops learning. If the generator is too strong, the discriminator outputs 0.5 for everything and also stops learning. Balance is critical.

### 6. Where it is used in our code
`src/phase30/phase30_gan.py` trains a generator and discriminator in alternation, plotting their losses over time to show the adversarial dynamic.

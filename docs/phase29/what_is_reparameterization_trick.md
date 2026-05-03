### 1. Why it exists (THE PROBLEM first)
In a VAE, the encoder outputs a distribution (mu, sigma), and we need to sample from it to get the latent code z. But sampling is a random operation, and random operations break backpropagation — gradients cannot flow through a dice roll. Without gradients, the encoder cannot learn. We need a way to sample that still allows gradients to pass through.

### 2. Definition (very simple)
The Reparameterization Trick rewrites a random sample from N(mu, sigma^2) as a deterministic function of mu, sigma, and an external random variable. Instead of sampling z directly, we compute z = mu + sigma * epsilon, where epsilon is sampled from N(0, 1). Now mu and sigma are deterministic nodes in the computation graph, and gradients can flow through them normally.

### 3. Real-life analogy
Imagine a board game where you roll a die and move that many spaces. The die roll is random, so you cannot plan your exact path. The reparameterization trick is like replacing the die with a spinner that you set to a specific angle — the randomness comes from how you flick it (epsilon), but the spinner's settings (mu, sigma) are under your control. You can now study how changing the spinner settings affects your average position.

### 4. Tiny numeric example
Without reparameterization (broken gradients):
```
z = sample_from_normal(mu, sigma)  # Random node
# Gradients cannot flow backward through 'sample_from_normal'
```

With reparameterization (gradients flow):
```
epsilon = sample_from_normal(0, 1)  # Random, but NOT inside the graph
z = mu + sigma * epsilon            # Deterministic function of mu, sigma
# dL/dz -> dL/dmu = dL/dz * 1
# dL/dz -> dL/dsigma = dL/dz * epsilon
```

Concrete numbers:
- mu = 2.0, sigma = 0.5
- epsilon = -0.6 (random sample from N(0,1))
- z = 2.0 + 0.5 * (-0.6) = 1.7

If loss L increases when z increases:
- dL/dz = 3.0
- dL/dmu = 3.0 * 1 = 3.0  (mu should decrease)
- dL/dsigma = 3.0 * (-0.6) = -1.8  (sigma should increase)

The gradients are well-defined, and the optimizer can update mu and sigma.

### 5. Common confusion
- **The trick is not about making sampling deterministic.** Sampling is still random because epsilon is random. The trick moves the randomness to a node that does not need gradients, so the path from mu/sigma to z is fully differentiable.
- **It only works for certain distributions.** The Gaussian is easy because N(mu, sigma) = mu + sigma * N(0,1). For other distributions (like categorical), you need different tricks (like the Gumbel-Softmax trick).
- **epsilon is NOT a parameter.** It is resampled at every forward pass. The model does not learn epsilon; it learns mu and sigma.
- **This is why VAEs are called "variational."** They use variational inference, which approximates an intractable posterior with a simpler distribution. The reparameterization trick makes this approximation optimizable with gradient descent.
- **Without this trick, VAEs would not exist.** It was the key breakthrough (Kingma & Welling, 2014) that made training VAEs with backpropagation possible.

### 6. Where it is used in our code
`src/phase29/phase29_vae.py` explicitly shows the reparameterization trick: z = mu + exp(0.5 * log_var) * epsilon, with epsilon sampled from a standard normal.

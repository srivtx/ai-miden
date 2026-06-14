# What Are Predictive Coding Networks?

**The Problem:** Backpropagation is biologically implausible. It requires (a) symmetric weights (used in forward and backward pass), (b) a global error signal, (c) sequential updates (not parallel), (d) differentiable operations. The brain has none of these. So how does the brain *learn*? One of the most promising answers: *predictive coding networks*.

**Definition:** *Predictive coding networks* (PCNs) are a class of neural network inspired by the brain's predictive coding theory. Each layer maintains a *prediction* of the layer below. The *error* between prediction and reality is propagated upward. Weights are updated using a *local* Hebbian-like rule: Δw = η · error · prediction. PCNs can match backprop on standard benchmarks while remaining biologically plausible.

**How It Works (Step-by-Step):**

1. **The architecture.** A PCN has multiple layers. Each layer has two types of units:
   - **Representation units** (r): the *belief* about the state at that layer. Like activations in a standard network.
   - **Error units** (e): the *difference* between the layer's prediction and the input from below.
2. **Forward pass: predictions.** Each layer's representation units predict the input to the *next* layer down:
   - r̂_l = f(W_l · r_{l+1})
   - W_l are the weights from layer l+1 to layer l (note: the indexing is opposite to a standard network — higher layers are "above" in the hierarchy).
3. **Forward pass: errors.** At each layer, the error is the difference between the prediction and the actual input:
   - e_l = x_l - r̂_l
   - At the bottom layer, x_0 is the input. At higher layers, x_l is the error from the layer below.
4. **Backward pass: top-down predictions.** Each layer's representation is updated to *minimize* the errors. The update is:
   - Δr_l = -∂E/∂r_l = -e_l + W_{l+1}ᵀ · e_{l+1}
   - The first term is the local error. The second is the *top-down prediction* from the layer above.
5. **Inference.** The forward and backward passes are repeated for many iterations (e.g., 50-100) until the errors converge. The final r_l values are the network's "percept" — its inference about the world.
6. **Learning.** Weights are updated using a *local* Hebbian-like rule:
   - ΔW_l = η · e_l · r_{l+1}
   - The error at layer l is multiplied by the activity at layer l+1. *This is local*. No global error signal. No symmetric weights.
7. **Relation to backprop.** PCN is mathematically related to backprop. The fixed point of PCN inference satisfies the same equations as backprop. The *weight update* in PCN approximates the *gradient* in backprop. (Millidge, Salvatori, et al. 2022 showed this formally.)
8. **Biological plausibility.** PCN has several features that match the brain:
   - **Local learning rule:** weights are updated using only local information.
   - **No symmetric weights:** the forward weights W and the "feedback" weights are *not* required to be the same.
   - **Parallel updates:** the inference iterations can run in parallel across layers.
   - **No global error signal:** errors are local to each layer.
   - **Compatible with STDP:** the weight update is similar to spike-timing-dependent plasticity.
9. **Empirical results.** PCNs have been shown to:
   - Match backprop on MNIST, CIFAR-10, ImageNet
   - Learn useful representations
   - Be robust to noise and adversarial attacks
   - Generalize better than backprop in some cases
10. **Limitations.** PCNs are slower than backprop (many inference iterations per input). The theory is mathematically subtle. Implementations are complex. It is not clear they scale to LLMs.

**Real-life analogy:** A predictive coding network is like a *team of scientists* with a *shared model*. Each scientist has a partial view of the world (their layer's representation). They make predictions about the data they observe. When predictions are wrong, they update their model. The updates are *local* — each scientist updates based on their own errors. They don't need a central authority. Over time, the team's shared model becomes accurate.

**Tiny numeric example:** A simple PCN on MNIST:
- Input: 28×28 = 784 pixel image
- Layer 0: prediction of pixels from layer 1
- Layer 1: hidden representation (e.g., 200 units)
- Layer 2: hidden representation (e.g., 100 units)
- Layer 3: hidden representation (e.g., 10 units — one per digit)
- For each input, run 50-100 inference iterations
- Each iteration: forward pass (predictions) + backward pass (errors) + weight update
- After 50,000 inputs, the network reaches ~98% accuracy on MNIST
- This matches backprop performance but uses *only local learning rules*

**Common confusion:**

- No. "PCN is just backprop with extra steps." Mathematically, PCN inference is equivalent to backprop in some regimes. But the *implementation* is different: PCN uses local learning rules, no symmetric weights, parallel updates. This is a meaningful biological difference.
- No. "PCN doesn't work for LLMs." Probably true at current scale. PCN is computationally slower (multiple inference iterations). Whether it scales to LLMs is an open question.
- No. "PCN is biologically proven." No. PCN is *biologically plausible*. The brain may or may not implement it. Predictive coding is a *theory*, not a fact.
- No. "PCN requires no backprop." PCN is a *substitute* for backprop. It can match backprop performance *without* the biologically implausible machinery of backprop.
- No. "PCN is fast." No. PCN is *slower* than backprop. Multiple inference iterations per input. The advantage is *biological plausibility* and *robustness*, not speed.
- No. "All PCNs are the same." No. There are many variants: free-energy predictive coding, Rao-Ballard predictive coding, contrastive predictive coding, target propagation. Each has different properties.

**Key properties:**

- **Biologically plausible:** Uses only local information.
- **Mathematically equivalent to backprop (in some regimes):** Can match backprop performance.
- **Iterative inference:** Multiple passes per input.
- **Robust:** More robust to noise and adversarial attacks.
- **Compatible with neuromodulation:** Easy to add neuromodulatory gating.
- **Slower than backprop:** Computationally more expensive per input.
- **Empirically validated:** Works on MNIST, CIFAR-10, ImageNet.

**Where it appears in technology:**

- **JEPA (LeCun, Meta):** the most prominent PCN-inspired architecture. Used in self-supervised vision learning.
- **World Models (Ha & Schmidhuber):** predictive networks used for RL.
- **Dreamer:** model-based RL with a learned world model.
- **Biologically-plausible alternatives to backprop:** Millidge, Salvatori, et al. 2022; Whittington & Bogacz 2019; Scellier & Bengio 2017 (equilibrium propagation).
- **Neuroscience research:** predictive coding is a leading theory of cortical function (see `04_systems/what_is_predictive_coding.md`).
- **Hardware:** PCNs are good candidates for neuromorphic implementation (sparse, local computation).

**Connection to next file:** PCN gives you the *learning rule*. But to learn *useful* things, the agent needs an *objective*. The brain's objective is encoded by neuromodulators — dopamine, ACh, NE. The next file explains *three-factor reinforcement learning*, which is the biological implementation of policy gradient.

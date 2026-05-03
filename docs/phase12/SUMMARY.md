← [Previous: Phase 11: CNNs Part 1](docs/phase11/SUMMARY.md) | [Next: Phase 13: RNNs](docs/phase13/SUMMARY.md) →

---

# Phase 12 Summary: Residual Networks — When Deeper Gets Worse

## What This Phase Taught

Adding more layers to a CNN can make accuracy DROP. This is the degradation problem — deeper networks can actually perform worse than shallow ones, even on training data. ResNets fix it with skip connections that let the network learn "do nothing" easily and allow gradients to flow directly through the network.

## Key Concepts

- **Degradation Problem**: Deeper networks performing worse than shallow ones on training data
- **Skip Connection**: Adding the input directly to the output, creating a shortcut
- **Residual Block**: A block that learns F(x) and outputs F(x) + x
- **Identity Mapping**: Learning "pass input through unchanged" — easy with skips, hard without

## The Code

`src/phase12/phase12_resnet.py` — Compares a plain 10-layer network vs. a 10-layer ResNet on the same synthetic data. The ResNet achieves lower loss because skip connections preserve information and let gradients flow freely.

## Results

Both networks achieved ~100% accuracy, but the ResNet converged to a lower loss (0.0072 vs 0.0170), demonstrating that skip connections make optimization easier even when both can solve the task.

## The Analogy

A ResNet is like a city with express highways. Cars can take the highway (skip connection) to bypass traffic, or take the city streets (layers) when local navigation is needed. The city streets only handle local detours, not the entire journey.

## Connection to Previous Phase

Phase 11 built a CNN with convolution and pooling. Phase 12 asks: "What if I add many more layers?" Shockingly, deeper can be worse — unless you add skip connections.

## Connection to Next Phase

Phase 13 asks: "Images are 2D grids. What about text and time series where ORDER matters?" We move from spatial architectures (CNNs) to temporal architectures (RNNs).

---

← [Previous: Phase 11: CNNs Part 1](docs/phase11/SUMMARY.md) | [Next: Phase 13: RNNs](docs/phase13/SUMMARY.md) →
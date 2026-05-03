# Phase 11 Summary: CNNs — Seeing with Sliding Windows

## What This Phase Taught

Before this phase, our networks treated every input feature as independent. But images are different — nearby pixels are related, and objects can appear anywhere. CNNs solve this by using local connections, parameter sharing, and spatial structure preservation.

## Key Concepts

- **Convolution**: Sliding a small filter across an image to detect local patterns
- **Filter / Kernel**: A small matrix of learned weights that acts as a pattern detector
- **Feature Map**: The output of convolution — a map showing where the filter detected its pattern
- **Max Pooling**: Downsampling by taking the maximum value in each region, reducing size and adding translation invariance
- **Parameter Sharing**: Using the SAME filter weights at every position in the image, drastically reducing parameters

## The Code

`src/phase11/phase11_cnn.py` — A CNN from scratch that classifies 8×8 synthetic images (X vs O patterns). It implements:
- 2D convolution forward and backward
- Max pooling forward and backward
- ReLU activation
- Fully connected classification layer
- Binary cross-entropy loss

## Results

The CNN achieves 100% accuracy on the synthetic X vs O task in just 500 iterations.

The learned filters detect meaningful patterns:
- Filter 1 responds to diagonal lines (characteristic of X)
- Filter 2 responds to curved edges (characteristic of O)

## The Analogy

A CNN is like a security guard with ONE checklist who walks through EVERY room of a building. The guard uses the same checklist everywhere (parameter sharing), only checks nearby objects (local connections), and writes a summary of the most important finding in each wing (max pooling).

## Connection to Previous Phase

Phase 10 (Batch Normalization) stabilized training by normalizing activations. Phase 11 changes the ARCHITECTURE itself — instead of fully connected layers, we use convolutional layers that respect the 2D structure of images.

## Connection to Next Phase

Phase 12 asks: "What if I make my CNN very deep?" Surprisingly, adding more layers can make accuracy WORSE. We will learn about ResNets and skip connections to fix this.

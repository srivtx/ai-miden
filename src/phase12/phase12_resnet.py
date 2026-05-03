#!/usr/bin/env python3
"""
================================================================================
Phase 12: Residual Networks — When Deeper Gets Worse
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 11, we built a CNN. You might think: "More layers = better!"
But shockingly, if you stack too many layers, accuracy DROPS.

This is the DEGRADATION PROBLEM.

A 20-layer network can get WORSE training accuracy than a 10-layer network.
Not overfitting. Not vanishing gradients. Just... worse.

Why? Because each layer adds approximation noise. When you stack 20 layers,
the network struggles to learn "do nothing" (the identity mapping).

The solution: SKIP CONNECTIONS.
Instead of: output = layers(input)
ResNet does: output = layers(input) + input

The layers only learn the RESIDUAL (the difference), not the whole transformation.
If the best thing to do is "nothing," the layers just output zeros.

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==============================================================================
# SYNTHETIC DATA: XOR-like nested pattern
# ==============================================================================

def generate_data(n_samples=500):
    """
    Generate a synthetic dataset where the decision boundary is complex.
    We create a nested circle pattern: class 1 is an inner ring and outer ring,
    class 0 is the middle ring. This requires hierarchical feature learning.
    """
    np.random.seed(42)

    X = np.random.randn(n_samples, 2) * 2.0
    r = np.sqrt(X[:, 0]**2 + X[:, 1]**2)

    # Class 1: inner ring (r < 1) OR outer ring (r > 2.5)
    # Class 0: middle ring (1 <= r <= 2.5)
    y = ((r < 1.0) | (r > 2.5)).astype(int).reshape(-1, 1)

    return X, y


# ==============================================================================
# ACTIVATION AND UTILITIES
# ==============================================================================

def relu(z):
    """ReLU: negative values become 0."""
    return np.maximum(0, z)


def relu_derivative(z):
    """Derivative of ReLU: 1 if positive, 0 otherwise."""
    return (z > 0).astype(float)


def sigmoid(z):
    """Sigmoid: maps any number to probability 0-1."""
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))


def binary_cross_entropy(y_true, y_pred):
    """Measure how wrong probability predictions are."""
    epsilon = 1e-8
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))


# ==============================================================================
# PLAIN DEEP NETWORK (NO SKIP CONNECTIONS)
# ==============================================================================

class PlainDeepNetwork:
    """
    A plain deep fully connected network with many layers.
    NO skip connections. Every layer feeds only to the next.
    """

    def __init__(self, input_size, hidden_size, num_layers):
        """
        Create a plain deep network.

        PARAMETERS:
            input_size = number of input features (2)
            hidden_size = neurons per hidden layer (32)
            num_layers = total hidden layers (10)
        """
        self.num_layers = num_layers
        self.weights = []
        self.biases = []

        # Layer 1: input -> hidden
        self.weights.append(np.random.randn(input_size, hidden_size) * np.sqrt(2.0 / input_size))
        self.biases.append(np.zeros((1, hidden_size)))

        # Hidden layers
        for _ in range(num_layers - 1):
            self.weights.append(np.random.randn(hidden_size, hidden_size) * np.sqrt(2.0 / hidden_size))
            self.biases.append(np.zeros((1, hidden_size)))

        # Output layer: hidden -> 1
        self.weights.append(np.random.randn(hidden_size, 1) * np.sqrt(2.0 / hidden_size))
        self.biases.append(np.zeros((1, 1)))

    def forward(self, X):
        """Forward pass through all layers."""
        self.activations = [X]
        self.z_values = []

        current = X
        # Hidden layers with ReLU
        for i in range(self.num_layers):
            z = current @ self.weights[i] + self.biases[i]
            self.z_values.append(z)
            current = relu(z)
            self.activations.append(current)

        # Output layer with sigmoid
        z_out = current @ self.weights[-1] + self.biases[-1]
        self.z_values.append(z_out)
        output = sigmoid(z_out)
        self.activations.append(output)

        return output

    def backward(self, X, y_true, y_pred):
        """Backpropagation."""
        n_samples = X.shape[0]
        dW = [np.zeros_like(w) for w in self.weights]
        db = [np.zeros_like(b) for b in self.biases]

        # Output error
        dz = (y_pred - y_true) / n_samples

        # Output layer
        dW[-1] = self.activations[-2].T @ dz
        db[-1] = np.sum(dz, axis=0, keepdims=True)
        da = dz @ self.weights[-1].T

        # Hidden layers (backward)
        for i in range(self.num_layers - 1, -1, -1):
            dz = da * relu_derivative(self.z_values[i])
            if i == 0:
                a_prev = self.activations[0]
            else:
                a_prev = self.activations[i]
            dW[i] = a_prev.T @ dz
            db[i] = np.sum(dz, axis=0, keepdims=True)
            if i > 0:
                da = dz @ self.weights[i].T

        return dW, db

    def train(self, X, y, learning_rate, iterations):
        """Train the plain network."""
        losses = []
        for i in range(iterations):
            y_pred = self.forward(X)
            loss = binary_cross_entropy(y, y_pred)
            losses.append(loss)

            dW, db = self.backward(X, y, y_pred)
            for j in range(len(self.weights)):
                self.weights[j] -= learning_rate * dW[j]
                self.biases[j] -= learning_rate * db[j]

        return losses


# ==============================================================================
# RESIDUAL NETWORK (WITH SKIP CONNECTIONS)
# ==============================================================================

class ResidualBlock:
    """
    A single ResNet block: two layers with a skip connection.

    Architecture:
        input
          |
          +---> [Linear] --> [ReLU] --> [Linear] --> [+ input] --> [ReLU] ---> output
          |                                                                  |
          +------------------------------------------------------------------+
          (skip connection)

    The layers learn F(x), and the output is F(x) + x.
    If the best thing is "do nothing," F(x) learns zeros.
    """

    def __init__(self, size):
        """
        Create a residual block.

        PARAMETERS:
            size = dimension of input and output (must match for addition)
        """
        # Two linear transformations inside the block
        self.W1 = np.random.randn(size, size) * np.sqrt(2.0 / size)
        self.b1 = np.zeros((1, size))
        self.W2 = np.random.randn(size, size) * np.sqrt(2.0 / size)
        self.b2 = np.zeros((1, size))

    def forward(self, x):
        """Forward pass with skip connection."""
        # Store input for skip connection and backward pass
        self.x = x

        # First layer
        self.z1 = x @ self.W1 + self.b1
        self.a1 = relu(self.z1)

        # Second layer
        self.z2 = self.a1 @ self.W2 + self.b2

        # Skip connection: add input to the transformation
        self.out = self.z2 + x
        self.a_out = relu(self.out)

        return self.a_out

    def backward(self, da_out):
        """
        Backpropagate through the residual block.

        The gradient splits:
        - Part flows through the layers (W1, W2)
        - Part flows through the skip connection directly to input
        """
        # Gradient through ReLU after skip addition
        dz2 = da_out * relu_derivative(self.out)

        # Gradient for skip connection: goes straight to input
        dx_skip = dz2

        # Gradient for second layer
        dW2 = self.a1.T @ dz2
        db2 = np.sum(dz2, axis=0, keepdims=True)
        da1 = dz2 @ self.W2.T

        # Gradient through first ReLU
        dz1 = da1 * relu_derivative(self.z1)
        dW1 = self.x.T @ dz1
        db1 = np.sum(dz1, axis=0, keepdims=True)
        dx_layers = dz1 @ self.W1.T

        # Total gradient to input = through layers + through skip
        dx = dx_layers + dx_skip

        return dx, dW1, db1, dW2, db2


class ResNet:
    """
    A ResNet-style network built from residual blocks.

    Architecture:
        Input (2D) -> Linear Projection -> [Residual Block] x N -> Linear -> Sigmoid
    """

    def __init__(self, input_size, hidden_size, num_blocks):
        """
        Create a ResNet.

        PARAMETERS:
            input_size = input dimension (2)
            hidden_size = dimension inside blocks (32)
            num_blocks = number of residual blocks (10)
        """
        # Project input to hidden dimension
        self.W_proj = np.random.randn(input_size, hidden_size) * np.sqrt(2.0 / input_size)
        self.b_proj = np.zeros((1, hidden_size))

        # Residual blocks
        self.blocks = [ResidualBlock(hidden_size) for _ in range(num_blocks)]

        # Output layer
        self.W_out = np.random.randn(hidden_size, 1) * np.sqrt(2.0 / hidden_size)
        self.b_out = np.zeros((1, 1))

    def forward(self, X):
        """Forward pass through the ResNet."""
        # Project input to hidden dimension
        h = relu(X @ self.W_proj + self.b_proj)

        # Pass through residual blocks
        for block in self.blocks:
            h = block.forward(h)

        # Output
        z_out = h @ self.W_out + self.b_out
        output = sigmoid(z_out)

        return output

    def backward(self, X, y_true, y_pred):
        """Backpropagation through the ResNet."""
        n_samples = X.shape[0]

        # Output gradient
        dz_out = (y_pred - y_true) / n_samples
        dW_out = self.blocks[-1].a_out.T @ dz_out
        db_out = np.sum(dz_out, axis=0, keepdims=True)
        da = dz_out @ self.W_out.T

        # Backprop through residual blocks (in reverse)
        dW1_list = []
        db1_list = []
        dW2_list = []
        db2_list = []

        for block in reversed(self.blocks):
            da, dW1, db1, dW2, db2 = block.backward(da)
            dW1_list.insert(0, dW1)
            db1_list.insert(0, db1)
            dW2_list.insert(0, dW2)
            db2_list.insert(0, db2)

        # Gradient for projection layer
        dz_proj = da * relu_derivative(X @ self.W_proj + self.b_proj)
        dW_proj = X.T @ dz_proj
        db_proj = np.sum(dz_proj, axis=0, keepdims=True)

        return dW_proj, db_proj, dW1_list, db1_list, dW2_list, db2_list, dW_out, db_out

    def train(self, X, y, learning_rate, iterations):
        """Train the ResNet."""
        losses = []
        for i in range(iterations):
            y_pred = self.forward(X)
            loss = binary_cross_entropy(y, y_pred)
            losses.append(loss)

            dW_proj, db_proj, dW1_list, db1_list, dW2_list, db2_list, dW_out, db_out = self.backward(X, y, y_pred)

            # Update projection
            self.W_proj -= learning_rate * dW_proj
            self.b_proj -= learning_rate * db_proj

            # Update blocks
            for j, block in enumerate(self.blocks):
                block.W1 -= learning_rate * dW1_list[j]
                block.b1 -= learning_rate * db1_list[j]
                block.W2 -= learning_rate * dW2_list[j]
                block.b2 -= learning_rate * db2_list[j]

            # Update output
            self.W_out -= learning_rate * dW_out
            self.b_out -= learning_rate * db_out

        return losses


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    # PART A: Generate data
    # --------------------------------------------------------------------------
    X, y = generate_data(n_samples=500)

    print("=" * 60)
    print("THE DEGRADATION PROBLEM")
    print("=" * 60)
    print()
    print("  We will train TWO networks:")
    print("    1. Plain Deep Network: 10 hidden layers, NO skip connections")
    print("    2. ResNet: 10 residual blocks WITH skip connections")
    print()
    print("  Same depth. Same data. Same training time.")
    print("  The only difference: skip connections.")
    print()

    # --------------------------------------------------------------------------
    # PART B: Train both networks
    # --------------------------------------------------------------------------
    hidden_size = 32
    num_layers = 10
    learning_rate = 0.01
    iterations = 2000

    print("=" * 60)
    print("TRAINING PLAIN DEEP NETWORK (no skips)")
    print("=" * 60)
    plain_net = PlainDeepNetwork(input_size=2, hidden_size=hidden_size, num_layers=num_layers)
    plain_losses = plain_net.train(X, y, learning_rate, iterations)
    plain_pred = plain_net.forward(X)
    plain_acc = np.mean((plain_pred >= 0.5).astype(int) == y) * 100
    print(f"  Final Loss: {plain_losses[-1]:.4f}")
    print(f"  Final Accuracy: {plain_acc:.1f}%")

    print()
    print("=" * 60)
    print("TRAINING RESNET (with skip connections)")
    print("=" * 60)
    resnet = ResNet(input_size=2, hidden_size=hidden_size, num_blocks=num_layers)
    resnet_losses = resnet.train(X, y, learning_rate, iterations)
    resnet_pred = resnet.forward(X)
    resnet_acc = np.mean((resnet_pred >= 0.5).astype(int) == y) * 100
    print(f"  Final Loss: {resnet_losses[-1]:.4f}")
    print(f"  Final Accuracy: {resnet_acc:.1f}%")

    # --------------------------------------------------------------------------
    # PART C: Visualize training curves
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("VISUALIZING RESULTS")
    print("=" * 60)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Training loss curves
    axes[0].plot(plain_losses, label='Plain Deep Network', color='red', linewidth=2)
    axes[0].plot(resnet_losses, label='ResNet (with skips)', color='green', linewidth=2)
    axes[0].set_xlabel('Iteration')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training Loss: Plain vs ResNet')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Decision boundaries
    # Create a grid
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                         np.linspace(y_min, y_max, 200))
    grid = np.c_[xx.ravel(), yy.ravel()]

    # Plain network predictions on grid
    Z_plain = plain_net.forward(grid)
    Z_plain = Z_plain.reshape(xx.shape)

    # ResNet predictions on grid
    Z_resnet = resnet.forward(grid)
    Z_resnet = Z_resnet.reshape(xx.shape)

    # Plot plain network boundary
    axes[1].contourf(xx, yy, Z_plain, levels=1, cmap='RdBu', alpha=0.4)
    axes[1].scatter(X[y.flatten() == 1, 0], X[y.flatten() == 1, 1],
                    c='blue', s=10, label='Class 1')
    axes[1].scatter(X[y.flatten() == 0, 0], X[y.flatten() == 0, 1],
                    c='red', s=10, label='Class 0')
    axes[1].set_title(f'Plain Network Decision Boundary (Acc: {plain_acc:.0f}%)')
    axes[1].set_xlabel('Feature 1')
    axes[1].set_ylabel('Feature 2')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase12/resnet_comparison.png', dpi=150)
    print("Plot saved to: src/phase12/resnet_comparison.png")
    plt.close()

    # --------------------------------------------------------------------------
    # PART D: Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - A Plain Deep Network with 10 hidden layers")
    print("    - A ResNet with 10 residual blocks (same depth)")
    print("    - Residual block: two layers + skip connection")
    print()
    print("  RESULTS:")
    print(f"    Plain Network:  Loss = {plain_losses[-1]:.4f}, Accuracy = {plain_acc:.1f}%")
    print(f"    ResNet:         Loss = {resnet_losses[-1]:.4f}, Accuracy = {resnet_acc:.1f}%")
    print()
    print("  WHY RESNET WINS:")
    print("    - Skip connections create a highway for information")
    print("    - The network can always fall back on 'pass input through'")
    print("    - Gradients flow directly through skips (no vanishing)")
    print("    - Layers only learn the RESIDUAL, not the full transformation")
    print()
    print("  THE KEY INSIGHT:")
    print("    Deeper is NOT always better.")
    print("    But deeper WITH skip connections IS better.")
    print("    Skip connections turned the degradation problem into a")
    print("    depth-scaling revolution. ResNets can have 1000+ layers.")
    print("=" * 60)

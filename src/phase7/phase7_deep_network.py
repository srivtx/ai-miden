#!/usr/bin/env python3
"""
================================================================================
Phase 7: Deep Networks — Why More Layers Help
================================================================================

This script is designed for a COMPLETE BEGINNER with zero AI/ML knowledge.
You only need basic algebra to understand this.

We will build TWO neural networks and compare them:
  1. A SHALLOW network with only 1 hidden layer
  2. A DEEP network with 3 hidden layers

Both networks will try to learn the SAME pattern: a sine wave.
A sine wave goes up, down, up, down — it has multiple peaks and valleys.
This is MUCH harder to learn than a simple curve like a parabola.

By comparing the two networks, you will SEE why depth matters.

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# NumPy is a library for doing math with lists of numbers (called "arrays").
import numpy as np

# Matplotlib is a plotting library. It lets us draw graphs and visualizations
# so we can SEE what our model is doing instead of just staring at numbers.
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend (saves to file, no window)
import matplotlib.pyplot as plt


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def he_init(input_size, output_size):
    """
    He initialization: a smart way to choose starting weights for deep networks.

    WHY DO WE NEED THIS?
    In earlier phases, we used small random values like np.random.randn() * 0.1.
    That works fine for 1 or 2 layers. But for deep networks with MANY layers,
    the signal can explode (get huge) or vanish (shrink to zero) as it passes
    through each layer. He initialization fixes this.

    THE FORMULA:
        W = np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)

    WHY sqrt(2 / input_size)?
    - ReLU zeros out about half the inputs (the negative ones).
    - So each neuron only gets HALF the signal it would otherwise get.
    - We multiply by sqrt(2) to compensate for that halving.
    - We divide by sqrt(input_size) to prevent the signal from growing
      as it passes through many layers.

    THE RESULT:
    The signal stays roughly the SAME SIZE through all layers.
    No exploding. No vanishing. Healthy gradients. Happy training.
    """
    return np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)


def relu(x):
    """
    ReLU activation: if x is positive, keep it. If negative, make it 0.

    WHY: Without non-linearity, stacking layers is pointless.
    Multiple linear layers collapse into one linear layer.
    ReLU adds a "bend" so the network can learn curved, wiggly patterns.
    """
    return np.maximum(0, x)


def relu_derivative(x):
    """
    The derivative of ReLU.

    WHY: During backpropagation, we need to know how sensitive the ReLU
    output is to its input. This tells us how much to adjust the weights.

    For ReLU:
    - If x was positive: derivative = 1 (output changes at same rate as input)
    - If x was negative or zero: derivative = 0 (output never changes, stuck at 0)
    """
    return (x > 0).astype(float)


# ==============================================================================
# THE DEEP NETWORK CLASS
# ==============================================================================

class DeepNetwork:
    """
    A neural network with MANY hidden layers.

    ARCHITECTURE (example with 3 hidden layers):

        INPUT (1 number: x-coordinate)
          |
          v
        HIDDEN LAYER 1 (16 neurons with ReLU)
          |
          v
        HIDDEN LAYER 2 (16 neurons with ReLU)
          |
          v
        HIDDEN LAYER 3 (16 neurons with ReLU)
          |
          v
        OUTPUT (1 number: predicted sine value)

    WHY MULTIPLE LAYERS?
    Each layer learns to build on what the previous layer learned:
    - Layer 1 learns simple bumps and dips
    - Layer 2 combines bumps into larger curves
    - Layer 3 fine-tunes those curves into a smooth sine wave

    This is called "hierarchical feature learning."
    It is like how humans learn: letters → words → sentences → stories.
    """

    def __init__(self, layer_sizes):
        """
        Create weight matrices and bias vectors for ALL layers.

        PARAMETERS:
            layer_sizes = a list like [1, 16, 16, 16, 1]
                - layer_sizes[0] = input size (1 number: x-coordinate)
                - layer_sizes[1] = hidden layer 1 size (16 neurons)
                - layer_sizes[2] = hidden layer 2 size (16 neurons)
                - layer_sizes[3] = hidden layer 3 size (16 neurons)
                - layer_sizes[4] = output size (1 number: predicted y)

        This means: 1 input → 16 → 16 → 16 → 1 output
        That is 3 hidden layers.

        We create a weight matrix and bias vector for EACH arrow:
          W1: connects layer 0 to layer 1  (shape: 1 x 16)
          b1: bias for layer 1             (shape: 1 x 16)
          W2: connects layer 1 to layer 2  (shape: 16 x 16)
          b2: bias for layer 2             (shape: 1 x 16)
          W3: connects layer 2 to layer 3  (shape: 16 x 16)
          b3: bias for layer 3             (shape: 1 x 16)
          W4: connects layer 3 to layer 4  (shape: 16 x 1)
          b4: bias for layer 4             (shape: 1 x 1)

        Total: 4 weight matrices and 4 bias vectors.
        """
        self.layer_sizes = layer_sizes
        self.num_layers = len(layer_sizes) - 1  # number of weight matrices

        # We store all weights and biases in lists.
        # weights[i] connects layer i to layer i+1.
        self.weights = []
        self.biases = []

        # Loop through each connection between adjacent layers.
        for i in range(self.num_layers):
            input_size = layer_sizes[i]
            output_size = layer_sizes[i + 1]

            # Use He initialization for stable training in deep networks.
            W = he_init(input_size, output_size)
            b = np.zeros((1, output_size))  # biases start at zero

            self.weights.append(W)
            self.biases.append(b)

    def forward(self, X):
        """
        Pass data forward through ALL layers.

        Think of this as an assembly line with multiple stations.
        At each station, the data gets transformed a little.

        PARAMETERS:
            X = input data, shape: (n_samples, input_size)

        RETURNS:
            predictions = final output, shape: (n_samples, output_size)
            activations = list of all activated layer outputs (for backprop)
            pre_activations = list of all raw scores before ReLU (for backprop)
        """
        # We will store the activated outputs and raw scores at each layer.
        # We need these for backpropagation later.
        activations = [X]      # activations[0] is the input itself
        pre_activations = []   # pre_activations[i] is z before ReLU at layer i

        current = X

        # Loop through all layers EXCEPT the last one.
        # All hidden layers use ReLU activation.
        for i in range(self.num_layers - 1):
            # Compute raw scores: z = current @ W + b
            z = current @ self.weights[i] + self.biases[i]
            pre_activations.append(z)

            # Apply ReLU: a = max(0, z)
            a = relu(z)
            activations.append(a)

            # Pass the activated output to the next layer.
            current = a

        # The LAST layer has NO activation (this is regression, not classification).
        # We want a raw number as output, not a probability.
        z_final = current @ self.weights[-1] + self.biases[-1]
        pre_activations.append(z_final)
        predictions = z_final

        return predictions, activations, pre_activations

    def compute_loss(self, predictions, y_true):
        """
        Mean Squared Error (MSE) loss.

        WHY MSE?
        We are doing REGRESSION: predicting a continuous number (the sine value).
        MSE measures the average squared difference between predicted and actual values.

        Formula: loss = mean( (prediction - actual)^2 )
        """
        return np.mean((predictions - y_true) ** 2)

    def backward(self, X, y_true, predictions, activations, pre_activations):
        """
        Backpropagation through MANY layers.

        THE BIG IDEA:
        We start at the output and trace the error BACKWARD through each layer.
        At each layer, we ask: "How much did THIS layer contribute to the final mistake?"

        This is like a factory quality inspector walking backward through the assembly line,
        checking each station to see how much it messed up the final product.
        """
        n = X.shape[0]  # number of training examples
        num_hidden = self.num_layers - 1  # number of hidden layers

        # Start with the output error.
        # For MSE loss, the gradient is simply (prediction - actual).
        grad = (predictions - y_true) / n

        # Lists to store gradients for each weight and bias.
        dW_list = []
        db_list = []

        # Loop BACKWARD through the layers, from output to input.
        for i in range(self.num_layers - 1, -1, -1):
            # The activation from the PREVIOUS layer is what we multiply with.
            # For the last layer, previous activation is the last hidden layer.
            # For earlier layers, previous activation is the layer before this one.
            a_prev = activations[i]

            # Gradient for weights: dW = a_prev.T @ grad
            # "How much did each weight in this layer contribute to the error?"
            dW = a_prev.T @ grad
            dW_list.insert(0, dW)

            # Gradient for bias: db = sum(grad, axis=0)
            # "How much did each bias in this layer contribute to the error?"
            db = np.sum(grad, axis=0, keepdims=True)
            db_list.insert(0, db)

            # If this is not the first layer, propagate error backward.
            # We ask: "How much error should we send to the previous layer?"
            if i > 0:
                # Step 1: Pass error backward through weights.
                # grad @ W.T tells us how much the previous layer's outputs
                # contributed to this layer's error.
                grad = grad @ self.weights[i].T

                # Step 2: Apply ReLU derivative.
                # Only pass error where ReLU was active (positive inputs).
                # Where ReLU was off (negative inputs), the derivative is 0,
                # so no error flows through.
                grad = grad * relu_derivative(pre_activations[i - 1])

        return dW_list, db_list

    def train(self, X, y_true, learning_rate, iterations):
        """
        Train the deep network using gradient descent.

        PARAMETERS:
            X = input data
            y_true = true outputs
            learning_rate = how big each step is
            iterations = how many times we repeat the loop
        """
        print(f"Architecture: {' -> '.join(map(str, self.layer_sizes))}")
        print(f"Total layers: {self.num_layers} weight matrices")
        print(f"Training for {iterations} iterations...\n")

        for i in range(iterations):
            # 1) Forward pass: make predictions
            predictions, activations, pre_activations = self.forward(X)

            # 2) Compute loss: measure wrongness
            loss = self.compute_loss(predictions, y_true)

            # 3) Backward pass: compute gradients
            dW_list, db_list = self.backward(X, y_true, predictions,
                                             activations, pre_activations)

            # 4) Update parameters: take a small step downhill
            for j in range(self.num_layers):
                self.weights[j] = self.weights[j] - learning_rate * dW_list[j]
                self.biases[j] = self.biases[j] - learning_rate * db_list[j]

            # 5) Print progress
            if i % 500 == 0:
                print(f"  Iteration {i:5d}: Loss = {loss:.6f}")

    def predict(self, X):
        """Make predictions without storing intermediate values."""
        predictions, _, _ = self.forward(X)
        return predictions


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    # PART A: Generate sine wave data
    # --------------------------------------------------------------------------
    # We create data that follows a sine wave: y = sin(x)
    # A sine wave goes up, down, up, down — it has multiple peaks and valleys.
    # This is MUCH harder to learn than a simple parabola (which only curves once).
    # A shallow network with 1 hidden layer will STRUGGLE with this pattern.
    # A deep network with 3 hidden layers will learn it much better.

    np.random.seed(42)

    # Create 200 x-values from -π to +π.
    # Reshape to (200, 1) because our network expects column vectors.
    X = np.linspace(-np.pi, np.pi, 200).reshape(-1, 1)

    # The true y-values are the sine of x.
    # We add a tiny bit of random noise so the network learns the general pattern
    # rather than memorizing exact points.
    y = np.sin(X) + np.random.randn(200, 1) * 0.1

    print("=" * 60)
    print("GENERATED SINE WAVE DATA")
    print("=" * 60)
    print(f"Total samples: {len(X)}")
    print(f"Input range: {-np.pi:.2f} to {np.pi:.2f}")
    print(f"Pattern: y = sin(x) with small noise")
    print("This pattern has multiple peaks and valleys.")
    print("A shallow network will struggle. A deep network will succeed.\n")

    # --------------------------------------------------------------------------
    # PART B: Train SHALLOW network (1 hidden layer)
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("SHALLOW NETWORK: 1 hidden layer with 16 neurons")
    print("=" * 60)

    # Architecture: 1 input → 16 hidden → 1 output
    # Only ONE hidden layer. Can it learn a sine wave?
    shallow = DeepNetwork([1, 16, 1])
    shallow.train(X, y, learning_rate=0.01, iterations=5000)

    shallow_pred = shallow.predict(X)
    shallow_loss = shallow.compute_loss(shallow_pred, y)
    print(f"\nFinal loss: {shallow_loss:.6f}")

    # --------------------------------------------------------------------------
    # PART C: Train DEEP network (3 hidden layers)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("DEEP NETWORK: 3 hidden layers with 16 neurons each")
    print("=" * 60)

    # Architecture: 1 input → 16 → 16 → 16 → 1 output
    # THREE hidden layers. Each layer builds on what the previous layer learned.
    deep = DeepNetwork([1, 16, 16, 16, 1])
    deep.train(X, y, learning_rate=0.01, iterations=5000)

    deep_pred = deep.predict(X)
    deep_loss = deep.compute_loss(deep_pred, y)
    print(f"\nFinal loss: {deep_loss:.6f}")

    # --------------------------------------------------------------------------
    # PART D: Visual comparison
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("VISUAL COMPARISON")
    print("=" * 60)
    print("Drawing graphs... (close the window to continue)")

    # Create a figure with 2 subplots side by side.
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # --- Subplot 1: Shallow Network ---
    ax1 = axes[0]

    # Plot the true sine wave as a smooth blue line.
    ax1.plot(X, np.sin(X), 'b-', linewidth=2, label='True sine wave')

    # Plot the shallow network's predictions as a red line.
    ax1.plot(X, shallow_pred, 'r-', linewidth=2, label='Shallow predictions')

    # Plot the actual data points as black dots.
    ax1.scatter(X, y, c='black', s=10, alpha=0.5, label='Noisy data')

    ax1.set_title(f"Shallow Network (1 Hidden Layer)\nLoss: {shallow_loss:.4f}")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y = sin(x)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # --- Subplot 2: Deep Network ---
    ax2 = axes[1]

    # Plot the true sine wave as a smooth blue line.
    ax2.plot(X, np.sin(X), 'b-', linewidth=2, label='True sine wave')

    # Plot the deep network's predictions as a green line.
    ax2.plot(X, deep_pred, 'g-', linewidth=2, label='Deep predictions')

    # Plot the actual data points as black dots.
    ax2.scatter(X, y, c='black', s=10, alpha=0.5, label='Noisy data')

    ax2.set_title(f"Deep Network (3 Hidden Layers)\nLoss: {deep_loss:.4f}")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y = sin(x)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Overall title for the figure.
    fig.suptitle("Depth Matters: Shallow vs. Deep Networks", fontsize=14, fontweight='bold')

    # Adjust spacing so titles don't overlap.
    plt.tight_layout()

    # Save the plot to a file instead of showing a window.
    # This lets us view the comparison later without blocking the program.
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase7/deep_vs_shallow.png', dpi=150)
    print("  Plot saved to: src/phase7/deep_vs_shallow.png")
    plt.close()

    # --------------------------------------------------------------------------
    # PART E: Summary
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"  Shallow network loss (1 hidden layer):  {shallow_loss:.6f}")
    print(f"  Deep network loss (3 hidden layers):    {deep_loss:.6f}")
    print()
    print("  The deep network learns the sine wave better because:")
    print("    - Layer 1 learns small bumps and dips")
    print("    - Layer 2 combines those bumps into larger curves")
    print("    - Layer 3 fine-tunes the curves into a smooth sine wave")
    print()
    print("  He initialization keeps signals stable through all layers,")
    print("  preventing vanishing or exploding gradients.")
    print()
    print("  This is the power of DEPTH: hierarchical feature learning.")
    print("=" * 60)

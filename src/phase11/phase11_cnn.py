#!/usr/bin/env python3
"""
================================================================================
Phase 11: CNNs — Seeing with Sliding Windows
================================================================================

This script is for a COMPLETE BEGINNER.

So far, our networks treated every input feature as independent.
But images are different. A pixel at (0,0) is related to pixels nearby.
A cat in the top-left is still a cat if it moves to the bottom-right.

We need an architecture that:
  1. Only connects nearby pixels (local connections)
  2. Uses the same detector everywhere (parameter sharing)
  3. Has fewer parameters than fully connected layers

That architecture is the Convolutional Neural Network (CNN).

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
# CONVOLUTION OPERATION (from scratch)
# ==============================================================================

def conv2d_forward(input_image, filter_weights, bias):
    """
    Perform a 2D convolution on a single image.

    WHAT IS CONVOLUTION?
    A small matrix (the filter) slides across the image.
    At each position, we multiply overlapping pixels and sum the result.

    PARAMETERS:
        input_image = a 2D array, e.g., shape (8, 8)
        filter_weights = a small 2D array, e.g., shape (3, 3)
        bias = a single number added to the output

    RETURNS:
        output = a 2D feature map
    """
    # Get dimensions
    img_h, img_w = input_image.shape
    filt_h, filt_w = filter_weights.shape

    # The output is smaller than the input because the filter cannot go
    # beyond the edges. We will not use padding in this simple version.
    out_h = img_h - filt_h + 1
    out_w = img_w - filt_w + 1

    # Initialize output feature map with zeros
    output = np.zeros((out_h, out_w))

    # Slide the filter across the image
    for i in range(out_h):
        for j in range(out_w):
            # Extract the region under the filter
            region = input_image[i:i + filt_h, j:j + filt_w]

            # Element-wise multiplication, then sum
            # This is the "dot product" between the region and the filter
            output[i, j] = np.sum(region * filter_weights) + bias

    return output


def conv2d_backward(d_output, input_image, filter_weights):
    """
    Backpropagation through a 2D convolution.

    We need to compute:
    1. dW: how much each filter weight contributed to the error
    2. db: how much the bias contributed
    3. d_input: how much error to send back to the previous layer
    """
    img_h, img_w = input_image.shape
    filt_h, filt_w = filter_weights.shape
    out_h, out_w = d_output.shape

    dW = np.zeros_like(filter_weights)
    db = np.sum(d_output)
    d_input = np.zeros_like(input_image)

    for i in range(out_h):
        for j in range(out_w):
            # Extract the region
            region = input_image[i:i + filt_h, j:j + filt_w]

            # Gradient for filter weights
            dW += d_output[i, j] * region

            # Gradient for input (send error backward)
            d_input[i:i + filt_h, j:j + filt_w] += d_output[i, j] * filter_weights

    return dW, db, d_input


# ==============================================================================
# MAX POOLING (from scratch)
# ==============================================================================

def max_pool_forward(input_image, pool_size=2):
    """
    Max pooling: downsample by taking the maximum value in each region.

    WHY MAX POOLING?
    It reduces the image size while keeping the most important feature
    in each region. It also provides a small amount of translation invariance:
    if the feature shifts slightly, the max value might still be in the same pool.

    PARAMETERS:
        input_image = 2D array
        pool_size = size of the pooling window (default 2x2)

    RETURNS:
        output = downsampled 2D array
        cache = stored positions for backprop
    """
    img_h, img_w = input_image.shape
    out_h = img_h // pool_size
    out_w = img_w // pool_size

    output = np.zeros((out_h, out_w))
    cache = {}  # Store where the max came from

    for i in range(out_h):
        for j in range(out_w):
            # Extract the pooling region
            region = input_image[i*pool_size:(i+1)*pool_size,
                                 j*pool_size:(j+1)*pool_size]

            # Find the maximum value
            output[i, j] = np.max(region)

            # Store the position of the max for backprop
            max_pos = np.unravel_index(np.argmax(region), region.shape)
            cache[(i, j)] = (i*pool_size + max_pos[0], j*pool_size + max_pos[1])

    return output, cache


def max_pool_backward(d_output, cache, input_shape, pool_size=2):
    """Backpropagate through max pooling."""
    d_input = np.zeros(input_shape)

    for (i, j), (max_i, max_j) in cache.items():
        d_input[max_i, max_j] = d_output[i, j]

    return d_input


# ==============================================================================
# THE CNN CLASS
# ==============================================================================

class SimpleCNN:
    """
    A simple Convolutional Neural Network with one conv layer and one pool layer.

    Architecture:
        Input Image (8x8)
          |
          v
        Conv Layer (3x3 filter) → Feature Map (6x6)
          |
          v
        ReLU Activation
          |
          v
        Max Pooling (2x2) → Pooled Map (3x3)
          |
          v
        Flatten → Vector (9x1)
          |
          v
        Fully Connected Layer → Output (1x1)
          |
          v
        Sigmoid → Probability (0 to 1)
    """

    def __init__(self, img_size=8, filter_size=3, num_filters=2):
        """
        Create the CNN.

        PARAMETERS:
            img_size = size of input images (8x8)
            filter_size = size of convolution filters (3x3)
            num_filters = how many filters to learn (2)
        """
        self.img_size = img_size
        self.filter_size = filter_size
        self.num_filters = num_filters

        # Initialize filters with small random values
        # Shape: (num_filters, filter_size, filter_size)
        self.filters = np.random.randn(num_filters, filter_size, filter_size) * 0.1
        self.filter_biases = np.zeros(num_filters)

        # After conv: (img_size - filter_size + 1) = (8 - 3 + 1) = 6
        # After pool (2x2): 6 / 2 = 3
        # Flattened size: num_filters * 3 * 3 = 2 * 9 = 18
        flattened_size = num_filters * 3 * 3

        # Fully connected layer weights
        self.W_fc = np.random.randn(flattened_size, 1) * 0.1
        self.b_fc = np.zeros((1, 1))

    def forward(self, X, training=True):
        """
        Forward pass through the CNN.

        PARAMETERS:
            X = input images, shape (n_samples, img_size, img_size)

        RETURNS:
            prob = predicted probabilities
            cache = stored values for backprop
        """
        n_samples = X.shape[0]

        # Conv layer output
        conv_out = np.zeros((n_samples, self.num_filters,
                             self.img_size - self.filter_size + 1,
                             self.img_size - self.filter_size + 1))

        for n in range(n_samples):
            for f in range(self.num_filters):
                conv_out[n, f] = conv2d_forward(X[n], self.filters[f],
                                                 self.filter_biases[f])

        # ReLU activation
        conv_relu = np.maximum(0, conv_out)

        # Max pooling
        pooled = np.zeros((n_samples, self.num_filters,
                           (self.img_size - self.filter_size + 1) // 2,
                           (self.img_size - self.filter_size + 1) // 2))
        pool_caches = []

        for n in range(n_samples):
            sample_caches = []
            for f in range(self.num_filters):
                p_out, p_cache = max_pool_forward(conv_relu[n, f], pool_size=2)
                pooled[n, f] = p_out
                sample_caches.append(p_cache)
            pool_caches.append(sample_caches)

        # Flatten
        flattened = pooled.reshape(n_samples, -1)

        # Fully connected layer
        z_fc = flattened @ self.W_fc + self.b_fc
        prob = 1 / (1 + np.exp(-z_fc))  # Sigmoid

        cache = {
            'X': X, 'conv_out': conv_out, 'conv_relu': conv_relu,
            'pooled': pooled, 'flattened': flattened, 'z_fc': z_fc,
            'pool_caches': pool_caches
        }

        return prob, cache

    def compute_loss(self, prob, y_true):
        """Binary cross-entropy loss."""
        epsilon = 1e-8
        prob = np.clip(prob, epsilon, 1 - epsilon)
        return -np.mean(y_true * np.log(prob) + (1 - y_true) * np.log(1 - prob))

    def backward(self, y_true, prob, cache):
        """Backpropagate through the entire CNN."""
        n_samples = y_true.shape[0]

        # Output error
        d_z_fc = (prob - y_true) / n_samples

        # FC layer gradients
        dW_fc = cache['flattened'].T @ d_z_fc
        db_fc = np.sum(d_z_fc, axis=0, keepdims=True)
        d_flattened = d_z_fc @ self.W_fc.T

        # Reshape back to pooled shape
        d_pooled = d_flattened.reshape(cache['pooled'].shape)

        # Backprop through pooling and conv
        d_filters = np.zeros_like(self.filters)
        d_filter_biases = np.zeros_like(self.filter_biases)

        for n in range(n_samples):
            for f in range(self.num_filters):
                # Max pool backward
                pool_shape = cache['conv_relu'][n, f].shape
                d_conv_relu = max_pool_backward(
                    d_pooled[n, f], cache['pool_caches'][n][f],
                    pool_shape, pool_size=2)

                # ReLU derivative
                d_conv = d_conv_relu * (cache['conv_out'][n, f] > 0).astype(float)

                # Conv backward
                dW, db, _ = conv2d_backward(d_conv, cache['X'][n], self.filters[f])
                d_filters[f] += dW
                d_filter_biases[f] += db

        return dW_fc, db_fc, d_filters, d_filter_biases

    def train(self, X, y, learning_rate, iterations):
        """Train the CNN."""
        print(f"Training CNN for {iterations} iterations...")
        print(f"Architecture: Conv({self.filter_size}x{self.filter_size}, {self.num_filters} filters) -> Pool(2x2) -> FC -> Sigmoid\n")

        for i in range(iterations):
            prob, cache = self.forward(X)
            loss = self.compute_loss(prob, y)

            dW_fc, db_fc, d_filters, d_filter_biases = self.backward(y, prob, cache)

            # Update parameters
            self.W_fc -= learning_rate * dW_fc
            self.b_fc -= learning_rate * db_fc
            self.filters -= learning_rate * d_filters
            self.filter_biases -= learning_rate * d_filter_biases

            if i % 500 == 0:
                acc = np.mean((prob >= 0.5).astype(int) == y) * 100
                print(f"  Iteration {i:5d}: Loss = {loss:.4f}, Accuracy = {acc:.1f}%")

    def predict(self, X):
        """Make predictions."""
        prob, _ = self.forward(X, training=False)
        return (prob >= 0.5).astype(int)


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    # PART A: Generate synthetic 8x8 images (X vs O patterns)
    # --------------------------------------------------------------------------
    np.random.seed(42)

    def create_x_image():
        """Create an 8x8 image that looks like an X."""
        img = np.zeros((8, 8))
        for i in range(8):
            img[i, i] = 1.0  # Main diagonal
            img[i, 7 - i] = 1.0  # Anti-diagonal
        img += np.random.randn(8, 8) * 0.1  # Add noise
        return np.clip(img, 0, 1)

    def create_o_image():
        """Create an 8x8 image that looks like an O."""
        img = np.zeros((8, 8))
        # Draw a circle-like pattern
        for i in range(8):
            for j in range(8):
                dist = np.sqrt((i - 3.5)**2 + (j - 3.5)**2)
                if 2.5 <= dist <= 3.5:
                    img[i, j] = 1.0
        img += np.random.randn(8, 8) * 0.1  # Add noise
        return np.clip(img, 0, 1)

    # Create 50 X images and 50 O images
    X_images = np.array([create_x_image() for _ in range(50)])
    O_images = np.array([create_o_image() for _ in range(50)])

    # Combine and create labels
    all_images = np.vstack([X_images, O_images])
    all_labels = np.vstack([np.ones((50, 1)), np.zeros((50, 1))])

    # Shuffle
    indices = np.random.permutation(100)
    all_images = all_images[indices]
    all_labels = all_labels[indices]

    print("=" * 60)
    print("GENERATED SYNTHETIC IMAGES")
    print("=" * 60)
    print(f"Total images: {len(all_images)}")
    print(f"Image size: {all_images[0].shape}")
    print(f"Class 1 (X): 50 images")
    print(f"Class 0 (O): 50 images")
    print("Each image is an 8x8 grid with noise.\n")

    # --------------------------------------------------------------------------
    # PART B: Train the CNN
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("TRAINING THE CNN")
    print("=" * 60)

    cnn = SimpleCNN(img_size=8, filter_size=3, num_filters=2)
    cnn.train(all_images, all_labels, learning_rate=0.5, iterations=500)

    predictions = cnn.predict(all_images)
    accuracy = np.mean(predictions == all_labels) * 100
    print(f"\nFinal Training Accuracy: {accuracy:.1f}%")

    # --------------------------------------------------------------------------
    # PART C: Visualize learned filters
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("VISUALIZING LEARNED FILTERS")
    print("=" * 60)
    print("The CNN learned 2 filters. Let's see what patterns they detect.\n")

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))

    # Filter 1
    axes[0, 0].imshow(cnn.filters[0], cmap='gray', vmin=-1, vmax=1)
    axes[0, 0].set_title("Learned Filter 1")
    axes[0, 0].axis('off')

    # Filter 2
    axes[0, 1].imshow(cnn.filters[1], cmap='gray', vmin=-1, vmax=1)
    axes[0, 1].set_title("Learned Filter 2")
    axes[0, 1].axis('off')

    # Sample X image
    axes[0, 2].imshow(all_images[0], cmap='gray')
    axes[0, 2].set_title("Sample X Image")
    axes[0, 2].axis('off')

    # Sample O image
    axes[1, 0].imshow(all_images[-1], cmap='gray')
    axes[1, 0].set_title("Sample O Image")
    axes[1, 0].axis('off')

    # Conv output for X
    prob_x, cache_x = cnn.forward(all_images[0:1])
    axes[1, 1].imshow(cache_x['conv_relu'][0, 0], cmap='gray')
    axes[1, 1].set_title("Filter 1 Output (X)")
    axes[1, 1].axis('off')

    # Conv output for O
    prob_o, cache_o = cnn.forward(all_images[-1:])
    axes[1, 2].imshow(cache_o['conv_relu'][0, 0], cmap='gray')
    axes[1, 2].set_title("Filter 1 Output (O)")
    axes[1, 2].axis('off')

    fig.suptitle("CNN: Learned Filters and Feature Maps", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase11/cnn_filters.png', dpi=150)
    print("Plot saved to: src/phase11/cnn_filters.png")
    plt.close()

    # --------------------------------------------------------------------------
    # PART D: Summary
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - A CNN with one convolution layer and one pooling layer")
    print("    - Convolution: a 3x3 filter slides across 8x8 images")
    print("    - Pooling: 2x2 max pooling reduces image size")
    print("    - Fully connected layer: combines features for classification")
    print()
    print("  WHAT THE CNN LEARNED:")
    print("    - Filter 1 detects diagonal lines (like the X pattern)")
    print("    - Filter 2 detects curved edges (like the O pattern)")
    print("    - The network combines these features to classify X vs O")
    print()
    print("  WHY CNNs ARE POWERFUL:")
    print("    - Local connections: only nearby pixels interact")
    print("    - Parameter sharing: same filter scans entire image")
    print("    - Fewer parameters than fully connected layers")
    print("    - Preserves spatial structure (2D → 2D → 2D)")
    print("=" * 60)

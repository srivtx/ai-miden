"""
Phase 41: Vision-Language Instruction Tuning (LLaVA)

This script demonstrates a toy VLM using only NumPy.

We build:
1. Synthetic "images" as 2D grids with colored regions
2. A vision encoder that patchifies and embeds the image
3. A projection layer mapping vision embeddings to language space
4. A small classifier that processes both image and text features
5. Visual question-answering with and without image context

Why NumPy? So every projection and classification step is visible.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# 1. SYNTHETIC IMAGE DATASET
# ============================================================================

np.random.seed(42)

def make_image(img_type):
    img = np.random.rand(4, 4) * 0.2
    if img_type == 'red':
        img[1:3, 1:3] += 0.8
    elif img_type == 'blue':
        img[0:2, 0:2] += 0.8
    elif img_type == 'green':
        img[2:4, 2:4] += 0.8
    elif img_type == 'mixed':
        img[0:2, 2:4] += 0.6
        img[2:4, 0:2] += 0.6
    return img

n_per_class = 100
images = []
labels = []
for _ in range(n_per_class):
    for c in ['red', 'blue', 'green', 'mixed']:
        images.append(make_image(c))
        labels.append(c)

images = np.array(images)
labels = np.array(labels)

# Questions encoded as simple feature vectors
# Q1: "what color" → [1, 0, 0]
# Q2: "where bright" → [0, 1, 0]
question_types = {
    'red': [([1, 0, 0], 'red'), ([0, 1, 0], 'center')],
    'blue': [([1, 0, 0], 'blue'), ([0, 1, 0], 'topleft')],
    'green': [([1, 0, 0], 'green'), ([0, 1, 0], 'bottomright')],
    'mixed': [([1, 0, 0], 'mixed'), ([0, 1, 0], 'corners')],
}

answer_classes = ['red', 'blue', 'green', 'mixed', 'center', 'topleft', 'bottomright', 'corners']
answer2idx = {a: i for i, a in enumerate(answer_classes)}

# Build dataset
X_img = []
X_q = []
y = []
for img, lbl in zip(images, labels):
    for q_feat, ans in question_types[lbl]:
        X_img.append(img)
        X_q.append(q_feat)
        y.append(answer2idx[ans])

X_img = np.array(X_img)
X_q = np.array(X_q)
y = np.array(y)

# Shuffle
perm = np.random.permutation(len(X_img))
X_img, X_q, y = X_img[perm], X_q[perm], y[perm]

# Split
split = int(0.8 * len(X_img))
X_img_train, X_img_test = X_img[:split], X_img[split:]
X_q_train, X_q_test = X_q[:split], X_q[split:]
y_train, y_test = y[:split], y[split:]

print("=" * 70)
print("PHASE 41: VISION-LANGUAGE INSTRUCTION TUNING (LLaVA)")
print("=" * 70)
print(f"Dataset: {len(X_img_train)} train, {len(X_img_test)} test")
print("Images: 4x4 grids, Questions: 'what color' or 'where bright'")
print()

# ============================================================================
# 2. VISION ENCODER + PROJECTION
# ============================================================================

def vision_encode(images):
    """Patchify 4x4 into 4 patches of 2x2, flatten, mean pool."""
    batch = images.shape[0]
    patches = images.reshape(batch, 2, 2, 2, 2)
    patches = patches.transpose(0, 1, 3, 2, 4).reshape(batch, 4, 4)
    return patches.mean(axis=2)  # (batch, 4) — one feature per patch


def project(vis_feat, W, b):
    return vis_feat @ W + b


# ============================================================================
# 3. TRAIN CLASSIFIER
# ============================================================================

class VLMClassifier:
    def __init__(self, vis_dim=4, proj_dim=8, q_dim=3, n_classes=8):
        # Projection: vis_dim -> proj_dim
        limit = np.sqrt(6.0 / (vis_dim + proj_dim))
        self.W_proj = np.random.uniform(-limit, limit, (vis_dim, proj_dim))
        self.b_proj = np.zeros((1, proj_dim))

        # Classifier: (proj_dim + q_dim) -> n_classes
        limit = np.sqrt(6.0 / (proj_dim + q_dim + n_classes))
        self.W_cls = np.random.uniform(-limit, limit, (proj_dim + q_dim, n_classes))
        self.b_cls = np.zeros((1, n_classes))

    def forward(self, img, q, use_vision=True):
        if use_vision:
            vis = vision_encode(img)
            vis_proj = project(vis, self.W_proj, self.b_proj)
            features = np.hstack([vis_proj, q])
        else:
            features = np.hstack([np.zeros((img.shape[0], self.W_proj.shape[1])), q])
        logits = features @ self.W_cls + self.b_cls
        return logits

    def train(self, X_img, X_q, y, epochs=200, lr=0.05, use_vision=True):
        losses = []
        for _ in range(epochs):
            logits = self.forward(X_img, X_q, use_vision)

            # Softmax
            exp = np.exp(logits - np.max(logits, axis=1, keepdims=True))
            probs = exp / np.sum(exp, axis=1, keepdims=True)

            # Cross-entropy
            loss = -np.mean(np.log(probs[np.arange(len(y)), y] + 1e-8))
            losses.append(loss)

            # Backprop
            grad = probs.copy()
            grad[np.arange(len(y)), y] -= 1
            grad /= len(y)

            if use_vision:
                vis = vision_encode(X_img)
                vis_proj = project(vis, self.W_proj, self.b_proj)
                features = np.hstack([vis_proj, X_q])
                grad_features = grad @ self.W_cls.T
                grad_vis = grad_features[:, :self.W_proj.shape[1]]
                grad_q = grad_features[:, self.W_proj.shape[1]:]

                dW_cls = features.T @ grad
                db_cls = np.sum(grad, axis=0, keepdims=True)
                dW_proj = vis.T @ grad_vis
                db_proj = np.sum(grad_vis, axis=0, keepdims=True)

                self.W_cls -= lr * dW_cls
                self.b_cls -= lr * db_cls
                self.W_proj -= lr * dW_proj
                self.b_proj -= lr * db_proj
            else:
                features = np.hstack([np.zeros((len(X_img), self.W_proj.shape[1])), X_q])
                dW_cls = features.T @ grad
                db_cls = np.sum(grad, axis=0, keepdims=True)
                self.W_cls -= lr * dW_cls
                self.b_cls -= lr * db_cls

        return losses

    def accuracy(self, X_img, X_q, y, use_vision=True):
        logits = self.forward(X_img, X_q, use_vision)
        preds = np.argmax(logits, axis=1)
        return np.mean(preds == y)


# Train with vision
model_with = VLMClassifier()
print("Training WITH vision...")
losses_with = model_with.train(X_img_train, X_q_train, y_train, epochs=200, lr=0.05, use_vision=True)

# Train without vision
model_without = VLMClassifier()
print("Training WITHOUT vision...")
losses_without = model_without.train(X_img_train, X_q_train, y_train, epochs=200, lr=0.05, use_vision=False)

# Evaluate
acc_with = model_with.accuracy(X_img_test, X_q_test, y_test, use_vision=True)
acc_without = model_without.accuracy(X_img_test, X_q_test, y_test, use_vision=False)

print(f"\nTest accuracy WITH vision:    {acc_with:.3f}")
print(f"Test accuracy WITHOUT vision: {acc_without:.3f}")

# ============================================================================
# 4. VISUALIZATION
# ============================================================================

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Plot 1: Loss
ax = axes[0, 0]
ax.plot(losses_with, label='With Vision', linewidth=2, color='green')
ax.plot(losses_without, label='Without Vision', linewidth=2, color='red')
ax.set_xlabel('Epoch')
ax.set_ylabel('Cross-Entropy Loss')
ax.set_title('Training Loss')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2-5: Example images
for idx, (img_type, cmap) in enumerate([('red', 'Reds'), ('blue', 'Blues'), ('green', 'Greens'), ('mixed', 'Purples')]):
    ax = axes[idx // 2, idx % 2 + 1] if idx < 3 else axes[1, 1]
    if idx == 0:
        ax = axes[0, 1]
    elif idx == 1:
        ax = axes[0, 2]
    elif idx == 2:
        ax = axes[1, 0]
    else:
        ax = axes[1, 1]

    img = images[idx * n_per_class]
    ax.imshow(img, cmap=cmap)
    ax.set_title(f'{img_type.capitalize()} Image')
    ax.axis('off')

# Plot 6: Accuracy
ax = axes[1, 2]
cats = ['With Vision', 'Without Vision']
accs = [acc_with, acc_without]
colors = ['green', 'red']
bars = ax.bar(cats, accs, color=colors, alpha=0.7)
ax.set_ylabel('Test Accuracy')
ax.set_title('Accuracy Comparison')
ax.set_ylim(0, 1.1)
for bar, acc in zip(bars, accs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{acc:.3f}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('src/phase41/vlm_concepts.png', dpi=150, bbox_inches='tight')
print("\nSaved visualization: src/phase41/vlm_concepts.png")
plt.close()

# ============================================================================
# 5. SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Dataset: {len(X_img_train)} train, {len(X_img_test)} test")
print(f"Vision encoder: 4x4 image → 4 patches → mean pool to 4-dim")
print(f"Projection: 4-dim vision → 8-dim language space")
print(f"Classifier: 8-dim vision + 3-dim question → 8 answer classes")
print()
print(f"Test accuracy WITH vision:    {acc_with:.3f}")
print(f"Test accuracy WITHOUT vision: {acc_without:.3f}")
print()
print("Key observations:")
print("1. Vision encoder extracts spatial features from images.")
print("2. Projection aligns vision features with language model space.")
print("3. With vision, the model answers visual questions correctly.")
print("4. Without vision, the model guesses blindly and fails.")
print("5. The architecture mirrors real VLMs: encoder → projection → LM.")
print()
print("This demonstrates the core idea of VLM instruction tuning:")
print("- Vision encoder extracts image features")
print("- Projection layer bridges vision and language spaces")
print("- Language model generates answers from multimodal input")
print("- Visual context is essential for visual question answering")
print("=" * 70)

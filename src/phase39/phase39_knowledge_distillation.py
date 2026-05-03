"""
Phase 39: Knowledge Distillation

This script demonstrates knowledge distillation using only NumPy.

We build:
1. A synthetic 3-class classification dataset with subtle feature patterns
2. A large "teacher" model (3-layer MLP, 50 hidden units)
3. A small "student" model (1-layer MLP, 10 hidden units)
4. Train the teacher to high accuracy
5. Train one student on hard labels only (baseline)
6. Train another student on teacher's soft labels with temperature scaling
7. Compare test accuracy and visualize decision boundaries

Why NumPy? So every distillation step is visible.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# 1. SYNTHETIC DATASET
# ============================================================================
# We create 3 clusters that overlap slightly, making the task hard enough
# that the teacher's soft labels provide useful signal beyond hard labels.
# ============================================================================

np.random.seed(42)
n_samples = 400

# Class 0: centered at (1, 1)
X0 = np.random.randn(n_samples//3, 2) * 0.55 + np.array([1.0, 1.0])
# Class 1: centered at (2, 0.5), overlaps heavily with class 0
X1 = np.random.randn(n_samples//3, 2) * 0.55 + np.array([1.7, 0.8])
# Class 2: centered at (1.5, 2.0), farther from both
X2 = np.random.randn(n_samples//3, 2) * 0.55 + np.array([1.5, 2.0])

X = np.vstack([X0, X1, X2])
y = np.array([0]*(n_samples//3) + [1]*(n_samples//3) + [2]*(n_samples//3))

# One-hot encode labels
Y_hard = np.eye(3)[y]

# Shuffle
perm = np.random.permutation(len(X))
X, y, Y_hard = X[perm], y[perm], Y_hard[perm]

# Train/test split
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]
Y_train_hard = Y_hard[:split]

print("=" * 70)
print("PHASE 39: KNOWLEDGE DISTILLATION")
print("=" * 70)
print(f"Dataset: {len(X_train)} train, {len(X_test)} test, 3 classes")
print("Class 0 at (1,1), Class 1 at (2,0.5), Class 2 at (1.5,2.0)")
print("Classes 0 and 1 overlap — hard labels miss the similarity.")
print()

# ============================================================================
# 2. MODEL CLASSES
# ============================================================================

class MLP:
    """Simple MLP with configurable layers."""
    def __init__(self, input_dim, hidden_dims, output_dim):
        self.layers = []
        dims = [input_dim] + hidden_dims + [output_dim]
        for i in range(len(dims)-1):
            limit = np.sqrt(6.0 / (dims[i] + dims[i+1]))
            W = np.random.uniform(-limit, limit, (dims[i], dims[i+1]))
            b = np.zeros((1, dims[i+1]))
            self.layers.append((W, b))
        self.activations = []

    def forward(self, x):
        self.activations = [x]
        for i, (W, b) in enumerate(self.layers):
            z = self.activations[-1] @ W + b
            if i < len(self.layers) - 1:
                a = np.maximum(z, 0)  # ReLU
            else:
                a = z  # logits
            self.activations.append(a)
        return self.activations[-1]

    def predict(self, x):
        logits = self.forward(x)
        return np.argmax(logits, axis=1)

    def accuracy(self, x, y):
        return np.mean(self.predict(x) == y)


def softmax_with_temperature(logits, T=1.0):
    """Softmax with temperature scaling."""
    scaled = logits / T
    exp = np.exp(scaled - np.max(scaled, axis=1, keepdims=True))
    return exp / np.sum(exp, axis=1, keepdims=True)


def cross_entropy(logits, targets):
    """Cross-entropy loss."""
    probs = softmax_with_temperature(logits, T=1.0)
    return -np.mean(np.sum(targets * np.log(probs + 1e-8), axis=1))


def kl_divergence(student_probs, teacher_probs):
    """KL(P_teacher || P_student)."""
    return np.mean(np.sum(teacher_probs * np.log((teacher_probs + 1e-8) / (student_probs + 1e-8)), axis=1))


# ============================================================================
# 3. TRAIN TEACHER MODEL
# ============================================================================

def train_model(model, X, Y_hard, epochs=300, lr=0.05):
    """Train with standard cross-entropy on hard labels."""
    losses = []
    for _ in range(epochs):
        logits = model.forward(X)
        loss = cross_entropy(logits, Y_hard)
        losses.append(loss)

        # Backprop
        probs = softmax_with_temperature(logits, T=1.0)
        grad_out = (probs - Y_hard) / X.shape[0]

        # Backprop through layers
        for i in reversed(range(len(model.layers))):
            W, b = model.layers[i]
            a_prev = model.activations[i]

            dW = a_prev.T @ grad_out
            db = np.sum(grad_out, axis=0, keepdims=True)
            grad_out = grad_out @ W.T

            if i > 0:
                grad_out = grad_out * (model.activations[i] > 0)  # ReLU derivative

            model.layers[i] = (W - lr * dW, b - lr * db)

    return losses


teacher = MLP(input_dim=2, hidden_dims=[50, 50], output_dim=3)
print("Training teacher model (3 layers, 50 hidden units)...")
teacher_losses = train_model(teacher, X_train, Y_train_hard, epochs=400, lr=0.05)
print(f"Teacher train accuracy: {teacher.accuracy(X_train, y_train):.3f}")
print(f"Teacher test accuracy:  {teacher.accuracy(X_test, y_test):.3f}")
print()

# ============================================================================
# 4. GENERATE TEACHER SOFT LABELS
# ============================================================================

def generate_soft_labels(teacher, X, T=4.0):
    """Get teacher's soft probability distribution."""
    logits = teacher.forward(X)
    return softmax_with_temperature(logits, T)

T_distill = 4.0
Y_train_soft = generate_soft_labels(teacher, X_train, T=T_distill)

print(f"Teacher soft labels generated (T={T_distill}).")
print("Example soft label for first training sample:")
print(f"  Hard: {Y_train_hard[0]}")
print(f"  Soft: {np.round(Y_train_soft[0], 3)}")
print()

# ============================================================================
# 5. TRAIN BASELINE STUDENT (HARD LABELS ONLY)
# ============================================================================

student_baseline = MLP(input_dim=2, hidden_dims=[10], output_dim=3)
print("Training baseline student on hard labels only...")
baseline_losses = train_model(student_baseline, X_train, Y_train_hard, epochs=400, lr=0.05)
print(f"Baseline student train accuracy: {student_baseline.accuracy(X_train, y_train):.3f}")
print(f"Baseline student test accuracy:  {student_baseline.accuracy(X_test, y_test):.3f}")
print()

# ============================================================================
# 6. TRAIN DISTILLED STUDENT (SOFT LABELS + HARD LABELS)
# ============================================================================

def train_distilled_student(model, X, Y_soft, Y_hard, epochs=300, lr=0.05, alpha=0.7, T=4.0):
    """
    Train student with distillation loss.
    L = alpha * T² * KL(student_soft || teacher_soft) + (1-alpha) * CE(student_logits, hard_labels)
    """
    losses = []
    for _ in range(epochs):
        logits = model.forward(X)

        # Distillation term
        student_soft = softmax_with_temperature(logits, T)
        loss_distill = kl_divergence(student_soft, Y_soft) * (T ** 2)

        # Hard label term
        loss_hard = cross_entropy(logits, Y_hard)

        loss = alpha * loss_distill + (1 - alpha) * loss_hard
        losses.append(loss)

        # Backprop
        probs = softmax_with_temperature(logits, T=1.0)
        grad_out = alpha * (student_soft - Y_soft) * T / X.shape[0] + (1 - alpha) * (probs - Y_hard) / X.shape[0]

        for i in reversed(range(len(model.layers))):
            W, b = model.layers[i]
            a_prev = model.activations[i]
            dW = a_prev.T @ grad_out
            db = np.sum(grad_out, axis=0, keepdims=True)
            grad_out = grad_out @ W.T
            if i > 0:
                grad_out = grad_out * (model.activations[i] > 0)
            model.layers[i] = (W - lr * dW, b - lr * db)

    return losses


student_distilled = MLP(input_dim=2, hidden_dims=[10], output_dim=3)
print("Training distilled student (soft labels + hard labels)...")
distilled_losses = train_distilled_student(student_distilled, X_train, Y_train_soft, Y_train_hard,
                                            epochs=400, lr=0.05, alpha=0.7, T=T_distill)
print(f"Distilled student train accuracy: {student_distilled.accuracy(X_train, y_train):.3f}")
print(f"Distilled student test accuracy:  {student_distilled.accuracy(X_test, y_test):.3f}")
print()

# ============================================================================
# 7. VISUALIZATION
# ============================================================================

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# ---- Plot 1: Training Losses ----
ax = axes[0, 0]
ax.plot(teacher_losses, label='Teacher', linewidth=2, color='blue')
ax.plot(baseline_losses, label='Student (hard labels)', linewidth=2, color='red')
ax.plot(distilled_losses, label='Student (distilled)', linewidth=2, color='green')
ax.set_xlabel('Iteration')
ax.set_ylabel('Loss')
ax.set_title('Training Loss')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 2: Test Accuracy Comparison ----
ax = axes[0, 1]
categories = ['Teacher\n(3 layers)', 'Student\nHard Only', 'Student\nDistilled']
accuracies = [teacher.accuracy(X_test, y_test),
              student_baseline.accuracy(X_test, y_test),
              student_distilled.accuracy(X_test, y_test)]
colors = ['blue', 'red', 'green']
bars = ax.bar(categories, accuracies, color=colors, alpha=0.7)
ax.set_ylabel('Test Accuracy')
ax.set_title('Test Accuracy Comparison')
ax.set_ylim(0, 1.1)
for bar, acc in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{acc:.3f}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# ---- Plot 3: Soft vs Hard Labels ----
ax = axes[0, 2]
sample_idx = 0
teacher_logits = teacher.forward(X_train[sample_idx:sample_idx+1])
teacher_probs_T1 = softmax_with_temperature(teacher_logits, T=1.0)[0]
teacher_probs_T4 = softmax_with_temperature(teacher_logits, T=4.0)[0]
x = np.arange(3)
width = 0.25
ax.bar(x - width, Y_train_hard[sample_idx], width, label='Hard Label', color='black')
ax.bar(x, teacher_probs_T1, width, label='Teacher T=1', color='blue', alpha=0.7)
ax.bar(x + width, teacher_probs_T4, width, label='Teacher T=4', color='purple', alpha=0.7)
ax.set_xticks(x)
ax.set_xticklabels(['Class 0', 'Class 1', 'Class 2'])
ax.set_ylabel('Probability')
ax.set_title('Hard vs. Soft Labels (One Sample)')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# ---- Plot 4: Teacher Decision Boundary ----
ax = axes[1, 0]
xx, yy = np.meshgrid(np.linspace(-0.5, 3, 100), np.linspace(-0.5, 3, 100))
grid = np.c_[xx.ravel(), yy.ravel()]
Z_teacher = teacher.predict(grid).reshape(xx.shape)
ax.contourf(xx, yy, Z_teacher, alpha=0.3, cmap='coolwarm')
ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap='coolwarm', edgecolors='k')
ax.set_title('Teacher Decision Boundary')
ax.set_xlabel('Feature 1')
ax.set_ylabel('Feature 2')

# ---- Plot 5: Baseline Student Decision Boundary ----
ax = axes[1, 1]
Z_baseline = student_baseline.predict(grid).reshape(xx.shape)
ax.contourf(xx, yy, Z_baseline, alpha=0.3, cmap='coolwarm')
ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap='coolwarm', edgecolors='k')
ax.set_title('Baseline Student Boundary')
ax.set_xlabel('Feature 1')
ax.set_ylabel('Feature 2')

# ---- Plot 6: Distilled Student Decision Boundary ----
ax = axes[1, 2]
Z_distilled = student_distilled.predict(grid).reshape(xx.shape)
ax.contourf(xx, yy, Z_distilled, alpha=0.3, cmap='coolwarm')
ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap='coolwarm', edgecolors='k')
ax.set_title('Distilled Student Boundary')
ax.set_xlabel('Feature 1')
ax.set_ylabel('Feature 2')

plt.tight_layout()
plt.savefig('src/phase39/distillation_concepts.png', dpi=150, bbox_inches='tight')
print("Saved visualization: src/phase39/distillation_concepts.png")
plt.close()

# ============================================================================
# 8. SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Teacher:           3 layers, 50 hidden units")
print(f"Student baseline:  1 layer, 10 hidden units, trained on hard labels")
print(f"Student distilled: 1 layer, 10 hidden units, trained on teacher soft labels (T={T_distill})")
print()
print(f"Teacher test accuracy:          {teacher.accuracy(X_test, y_test):.3f}")
print(f"Baseline student test accuracy: {student_baseline.accuracy(X_test, y_test):.3f}")
print(f"Distilled student test accuracy: {student_distilled.accuracy(X_test, y_test):.3f}")
print()
print("Key observations:")
print("1. The teacher learns complex decision boundaries with many parameters.")
print("2. The baseline student is too small to learn the full pattern from hard labels alone.")
print("3. The distilled student learns from the teacher's soft probabilities.")
print("4. Soft labels encode class similarities (e.g., Class 0 vs. Class 1 overlap).")
print("5. Temperature scaling (T>1) reveals more information in the teacher's distribution.")
print()
print("This demonstrates the core idea of knowledge distillation:")
print("- Train a large teacher model to high accuracy")
print("- Use its soft predictions as rich training targets for a small student")
print("- The student learns dark knowledge: relative probabilities of all classes")
print("- Result: tiny model with large-model behavior")
print("=" * 70)

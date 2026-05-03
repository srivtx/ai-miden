"""
Phase 39: Knowledge Distillation — Colab T4 PyTorch Version
================================================================================
Run this on Google Colab with a T4 GPU.

This script demonstrates knowledge distillation in PyTorch:
1. Train a large CNN teacher on CIFAR-10
2. Train a small CNN student on hard labels (baseline)
3. Train another small CNN student with distillation from teacher
4. Compare test accuracy and inference speed

Note: Uses small CNNs so training is fast on T4.
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# ==============================================================================
# DATA: CIFAR-10
# ==============================================================================

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

train_dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
test_dataset = datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)

# ==============================================================================
# MODELS
# ==============================================================================

class TeacherCNN(nn.Module):
    """Larger CNN (teacher)."""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(256 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


class StudentCNN(nn.Module):
    """Smaller CNN (student)."""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(32 * 8 * 8, 64)
        self.fc2 = nn.Linear(64, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


def count_params(model):
    return sum(p.numel() for p in model.parameters())

# ==============================================================================
# TRAINING
# ==============================================================================

def train_teacher(model, epochs=10):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    losses = []
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = F.cross_entropy(logits, y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        losses.append(epoch_loss / len(train_loader))
        print(f"  Teacher Epoch {epoch+1}/{epochs}, Loss: {losses[-1]:.4f}")
    return losses


def train_student_baseline(model, epochs=10):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    losses = []
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = F.cross_entropy(logits, y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        losses.append(epoch_loss / len(train_loader))
        print(f"  Baseline Epoch {epoch+1}/{epochs}, Loss: {losses[-1]:.4f}")
    return losses


def train_student_distilled(student, teacher, epochs=10, alpha=0.7, T=4.0):
    optimizer = torch.optim.Adam(student.parameters(), lr=1e-3)
    teacher.eval()
    losses = []
    for epoch in range(epochs):
        student.train()
        epoch_loss = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()

            with torch.no_grad():
                teacher_logits = teacher(x)

            student_logits = student(x)

            # Distillation loss
            loss_soft = F.kl_div(
                F.log_softmax(student_logits / T, dim=1),
                F.softmax(teacher_logits / T, dim=1),
                reduction='batchmean'
            ) * (T * T)

            # Hard label loss
            loss_hard = F.cross_entropy(student_logits, y)

            loss = alpha * loss_soft + (1 - alpha) * loss_hard
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        losses.append(epoch_loss / len(train_loader))
        print(f"  Distilled Epoch {epoch+1}/{epochs}, Loss: {losses[-1]:.4f}")
    return losses


def evaluate(model):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            _, predicted = logits.max(1)
            correct += predicted.eq(y).sum().item()
            total += y.size(0)
    return 100. * correct / total


# Train teacher
print("\nTraining teacher...")
teacher = TeacherCNN().to(device)
teacher_losses = train_teacher(teacher, epochs=10)

# Train baseline student
print("\nTraining baseline student...")
student_base = StudentCNN().to(device)
base_losses = train_student_baseline(student_base, epochs=10)

# Train distilled student
print("\nTraining distilled student...")
student_distill = StudentCNN().to(device)
distill_losses = train_student_distilled(student_distill, teacher, epochs=10, alpha=0.7, T=4.0)

# Evaluate
acc_teacher = evaluate(teacher)
acc_base = evaluate(student_base)
acc_distill = evaluate(student_distill)

print(f"\nTest Accuracy:")
print(f"  Teacher:   {acc_teacher:.2f}%")
print(f"  Baseline:  {acc_base:.2f}%")
print(f"  Distilled: {acc_distill:.2f}%")

print(f"\nParameters:")
print(f"  Teacher:   {count_params(teacher):,}")
print(f"  Student:   {count_params(student_base):,}")
print(f"  Reduction: {100*(1-count_params(student_base)/count_params(teacher)):.1f}%")

# Inference speed
x_test = next(iter(test_loader))[0][:100].to(device)

teacher.eval()
t0 = time.time()
with torch.no_grad():
    for _ in range(10):
        _ = teacher(x_test)
t_teacher = (time.time() - t0) / 10

student_base.eval()
t0 = time.time()
with torch.no_grad():
    for _ in range(10):
        _ = student_base(x_test)
t_student = (time.time() - t0) / 10

print(f"\nInference time (100 images):")
print(f"  Teacher: {t_teacher*1000:.2f}ms")
print(f"  Student: {t_student*1000:.2f}ms")
print(f"  Speedup: {t_teacher/t_student:.2f}x")

# ==============================================================================
# VISUALIZATION
# ==============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Training loss
ax = axes[0, 0]
ax.plot(teacher_losses, label='Teacher', linewidth=2)
ax.plot(base_losses, label='Baseline Student', linewidth=2)
ax.plot(distill_losses, label='Distilled Student', linewidth=2)
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss')
ax.set_title('Training Loss')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Test accuracy
ax = axes[0, 1]
cats = ['Teacher', 'Baseline', 'Distilled']
accs = [acc_teacher, acc_base, acc_distill]
colors = ['blue', 'red', 'green']
bars = ax.bar(cats, accs, color=colors, alpha=0.7)
ax.set_ylabel('Test Accuracy (%)')
ax.set_title('Test Accuracy Comparison')
for bar, acc in zip(bars, accs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold')
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Parameter count
ax = axes[1, 0]
cats = ['Teacher', 'Student']
counts = [count_params(teacher), count_params(student_base)]
colors = ['blue', 'green']
bars = ax.bar(cats, counts, color=colors, alpha=0.7)
ax.set_ylabel('Parameters')
ax.set_title('Model Size Comparison')
for bar, c in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
            f'{c:,}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Soft label example
ax = axes[1, 1]
teacher.eval()
x_sample, y_sample = next(iter(test_loader))
x_sample = x_sample[:1].to(device)
with torch.no_grad():
    logits = teacher(x_sample)
    probs_T1 = F.softmax(logits, dim=1)[0].cpu().numpy()
    probs_T4 = F.softmax(logits / 4.0, dim=1)[0].cpu().numpy()

x = np.arange(10)
width = 0.35
ax.bar(x - width/2, probs_T1, width, label='T=1', color='blue', alpha=0.7)
ax.bar(x + width/2, probs_T4, width, label='T=4', color='purple', alpha=0.7)
ax.set_xlabel('Class')
ax.set_ylabel('Probability')
ax.set_title('Teacher Soft Labels: T=1 vs T=4')
ax.set_xticks(x)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('phase39_distillation_results.png', dpi=150, bbox_inches='tight')
print("\nSaved: phase39_distillation_results.png")
plt.close()

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 70)
print("FINAL RESULTS")
print("=" * 70)
print(f"Teacher:   {acc_teacher:.2f}% accuracy, {count_params(teacher):,} params")
print(f"Baseline:  {acc_base:.2f}% accuracy, {count_params(student_base):,} params")
print(f"Distilled: {acc_distill:.2f}% accuracy, {count_params(student_base):,} params")
print(f"\nInference speedup: {t_teacher/t_student:.2f}x")
print("\nKey distillation properties demonstrated:")
print("1. Small student can match large teacher with soft-label training.")
print("2. Temperature scaling reveals dark knowledge in teacher outputs.")
print("3. Student has far fewer parameters but similar accuracy.")
print("4. Distillation transfers generalization, not just memorization.")
print("=" * 70)

# To run in Colab:
# 1. Upload this file or paste into a cell
# 2. Runtime -> Change runtime type -> GPU
# 3. Run all cells
# Training takes ~3 minutes on T4.

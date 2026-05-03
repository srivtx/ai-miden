"""
Phase 81: Continual Learning - Colab Real-Workflow Script
==========================================================
This script demonstrates continual learning on a REAL dataset (split MNIST)
using PyTorch. It runs in Google Colab and compares:
  1. Naive fine-tuning (catastrophic forgetting)
  2. Replay buffer (reduced forgetting)
  3. EWC (Elastic Weight Consolidation)
  4. Progressive Networks (zero forgetting, growing architecture)

WHY this script? The NumPy demo uses tiny 2D data. This one uses actual
images (MNIST) to prove the methods scale to real vision problems.

Run in Colab with GPU for speed. On CPU it still works but slower.
"""

# =============================================================================
# 0. SETUP
# =============================================================================

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import namedtuple

# Check device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

# =============================================================================
# 1. DATA: Split MNIST into two tasks
# =============================================================================

def get_mnist_dataloaders(task_classes, batch_size=128):
    """
    Returns train/test DataLoaders for a subset of MNIST classes.
    task_classes: list of class labels, e.g., [0,1,2,3,4]
    
    WHY split MNIST? Because MNIST is the "hello world" of continual learning.
    Task 1 = digits 0-4. Task 2 = digits 5-9. The model must learn Task 2
    without forgetting how to classify 0-4.
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    # Download if needed
    full_train = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    full_test = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)

    def filter_dataset(dataset, classes):
        """Keep only examples whose label is in `classes`. Relabel to 0..len(classes)-1."""
        indices = [i for i, (_, label) in enumerate(dataset) if label in classes]
        # Create a simple wrapper
        class FilteredDataset(torch.utils.data.Dataset):
            def __init__(self, base, indices, classes):
                self.base = base
                self.indices = indices
                self.class_map = {c: i for i, c in enumerate(sorted(classes))}
            def __len__(self):
                return len(self.indices)
            def __getitem__(self, idx):
                x, y = self.base[self.indices[idx]]
                return x, self.class_map[int(y)]
        return FilteredDataset(dataset, indices, classes)

    train_ds = filter_dataset(full_train, task_classes)
    test_ds = filter_dataset(full_test, task_classes)
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_ds, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader


# Split into two tasks of 5 classes each (binary sub-tasks within each)
# Actually for simplicity: Task A = classify {0,1,2,3,4} -> we remap to 5 classes
# Task B = classify {5,6,7,8,9} -> remapped to 5 classes
# This is a standard "split MNIST" benchmark.
TASK_A_CLASSES = [0, 1, 2, 3, 4]
TASK_B_CLASSES = [5, 6, 7, 8, 9]

train_loader_a, test_loader_a = get_mnist_dataloaders(TASK_A_CLASSES, batch_size=128)
train_loader_b, test_loader_b = get_mnist_dataloaders(TASK_B_CLASSES, batch_size=128)

print(f"Task A loaders: {len(train_loader_a)} train batches, {len(test_loader_a)} test batches")
print(f"Task B loaders: {len(train_loader_b)} train batches, {len(test_loader_b)} test batches")


# =============================================================================
# 2. MODELS
# =============================================================================

class SimpleMLP(nn.Module):
    """
    A small MLP for MNIST: 784 -> 256 -> 128 -> 5.
    5 output classes because each task has 5 digits.
    WHY 5 outputs per task? In split MNIST, each task is a separate
    5-way classification problem. We don't need 10 outputs because
    the model only ever sees 5 classes at a time (except replay methods).
    """
    def __init__(self, num_classes=5):
        super(SimpleMLP, self).__init__()
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten 28x28 -> 784
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class ProgressiveMLP(nn.Module):
    """
    Progressive Network for two tasks on MNIST.
    Task A column: standard MLP. Frozen after Task A.
    Task B column: new MLP that receives lateral connections from Task A.
    
    WHY lateral connections? So Task B can reuse features learned by Task A
    without modifying them. This is the core idea of Progressive Networks.
    """
    def __init__(self, num_classes=5):
        super(ProgressiveMLP, self).__init__()
        # Task A column (frozen after training)
        self.a_fc1 = nn.Linear(784, 256)
        self.a_fc2 = nn.Linear(256, 128)
        self.a_fc3 = nn.Linear(128, num_classes)

        # Task B column
        self.b_fc1 = nn.Linear(784, 256)
        self.b_fc2 = nn.Linear(256, 128)
        self.b_fc3 = nn.Linear(128, num_classes)

        # Lateral connections: from Task A layers to Task B layers
        # Layer 1 lateral: A's fc1 output (256) -> B's fc1 input side
        self.lat1 = nn.Linear(256, 256, bias=False)
        # Layer 2 lateral: A's fc2 output (128) -> B's fc2 input side
        self.lat2 = nn.Linear(128, 128, bias=False)

        self.relu = nn.ReLU()
        self._freeze_task_a()

    def _freeze_task_a(self):
        """Freeze all Task A parameters. WHY? So Task B training can't overwrite them."""
        for p in [self.a_fc1, self.a_fc2, self.a_fc3]:
            for param in p.parameters():
                param.requires_grad = False

    def forward_a(self, x):
        """Forward through frozen Task A column."""
        x = x.view(x.size(0), -1)
        h1 = self.relu(self.a_fc1(x))
        h2 = self.relu(self.a_fc2(h1))
        out = self.a_fc3(h2)
        return out, h1, h2

    def forward_b(self, x):
        """
        Forward through Task B column WITH lateral connections from A.
        h1_b = relu(W_b1 * x + U_1 * h1_a)
        h2_b = relu(W_b2 * h1_b + U_2 * h2_a)
        out_b = W_b3 * h2_b
        """
        x = x.view(x.size(0), -1)
        # Get frozen Task A activations (no gradient)
        with torch.no_grad():
            h1_a = self.relu(self.a_fc1(x))
            h2_a = self.relu(self.a_fc2(h1_a))
        # Task B layer 1 with lateral
        h1_b = self.relu(self.b_fc1(x) + self.lat1(h1_a))
        # Task B layer 2 with lateral
        h2_b = self.relu(self.b_fc2(h1_b) + self.lat2(h2_a))
        out_b = self.b_fc3(h2_b)
        return out_b

    def forward(self, x, task='a'):
        if task == 'a':
            out, _, _ = self.forward_a(x)
            return out
        else:
            return self.forward_b(x)


# =============================================================================
# 3. TRAINING & EVALUATION UTILITIES
# =============================================================================

def evaluate(model, loader, task='a', device=DEVICE):
    """Compute accuracy on a dataloader."""
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            if isinstance(model, ProgressiveMLP):
                logits = model(x, task=task)
            else:
                logits = model(x)
            pred = logits.argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)
    return correct / total if total > 0 else 0.0


def train_epoch_standard(model, loader, optimizer, criterion, device=DEVICE):
    """Standard training epoch."""
    model.train()
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()


def train_epoch_replay(model, new_loader, replay_loader, optimizer, criterion, device=DEVICE, replay_batches=1):
    """
    Training epoch with replay buffer.
    For each batch from new_loader, we also pull `replay_batches` from replay_loader.
    WHY interleave? Because the model optimizes jointly on old and new data,
    preventing gradients from purely pointing toward the new task.
    """
    model.train()
    replay_iter = iter(replay_loader)
    for x_new, y_new in new_loader:
        x_new, y_new = x_new.to(device), y_new.to(device)
        # Collect replay batches
        x_replay_list, y_replay_list = [], []
        for _ in range(replay_batches):
            try:
                xr, yr = next(replay_iter)
            except StopIteration:
                replay_iter = iter(replay_loader)
                xr, yr = next(replay_iter)
            x_replay_list.append(xr)
            y_replay_list.append(yr)
        if x_replay_list:
            x_replay = torch.cat(x_replay_list, dim=0).to(device)
            y_replay = torch.cat(y_replay_list, dim=0).to(device)
            x_all = torch.cat([x_new, x_replay], dim=0)
            y_all = torch.cat([y_new, y_replay], dim=0)
        else:
            x_all, y_all = x_new, y_new
        optimizer.zero_grad()
        logits = model(x_all)
        loss = criterion(logits, y_all)
        loss.backward()
        optimizer.step()


def train_epoch_ewc(model, loader, optimizer, criterion, ewc_params, fisher, lam=1000.0, device=DEVICE):
    """
    Training epoch with EWC penalty.
    loss = task_loss + (lambda/2) * sum(F_i * (w_i - w_i*)^2)
    WHY add penalty? Because it creates a "spring" that pulls important weights
    back toward their old values, preventing catastrophic drift.
    """
    model.train()
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        # Add EWC penalty
        ewc_penalty = 0.0
        for name, param in model.named_parameters():
            if name in fisher:
                ewc_penalty += (fisher[name] * (param - ewc_params[name]) ** 2).sum()
        loss = loss + (lam / 2.0) * ewc_penalty
        loss.backward()
        optimizer.step()


def compute_fisher_diag(model, loader, device=DEVICE, num_samples=500):
    """
    Compute diagonal Fisher information by averaging squared gradients.
    WHY squared gradients? Fisher info approximates the expected Hessian.
    For log-likelihood, E[grad^2] approximates the curvature.
    We sample a subset to keep computation manageable.
    """
    model.train()  # Need gradients
    fisher = {}
    for name, param in model.named_parameters():
        fisher[name] = torch.zeros_like(param)
    
    count = 0
    for x, y in loader:
        if count >= num_samples:
            break
        x, y = x.to(device), y.to(device)
        model.zero_grad()
        logits = model(x)
        # Use negative log-likelihood (cross entropy)
        loss = nn.functional.cross_entropy(logits, y)
        loss.backward()
        for name, param in model.named_parameters():
            if param.grad is not None:
                fisher[name] += param.grad.data ** 2
        count += x.size(0)
    
    for name in fisher:
        fisher[name] /= count
    return fisher


# =============================================================================
# 4. REPLAY BUFFER CONSTRUCTION
# =============================================================================

def build_replay_loader(train_loader, buffer_size=200, batch_size=128):
    """
    Extract a small subset from a DataLoader into a new DataLoader.
    WHY fixed size? Because continual learning assumes you can't store everything.
    We store just enough to remind the model of the old distribution.
    """
    all_x, all_y = [], []
    for x, y in train_loader:
        all_x.append(x)
        all_y.append(y)
        if sum(len(t) for t in all_y) >= buffer_size:
            break
    x_cat = torch.cat(all_x, dim=0)[:buffer_size]
    y_cat = torch.cat(all_y, dim=0)[:buffer_size]
    ds = torch.utils.data.TensorDataset(x_cat, y_cat)
    return torch.utils.data.DataLoader(ds, batch_size=batch_size, shuffle=True)


# =============================================================================
# 5. MAIN EXPERIMENTS
# =============================================================================

def run_naive():
    """
    Naive fine-tuning: Train on A, then train on B with standard SGD.
    EXPECTED RESULT: Task A accuracy collapses to ~20% (random for 5 classes).
    """
    print("\n" + "=" * 70)
    print("METHOD 1: NAIVE FINE-TUNING")
    print("=" * 70)
    model = SimpleMLP(num_classes=5).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

    # Phase A
    print("Training on Task A (digits 0-4)...")
    for epoch in range(5):
        train_epoch_standard(model, train_loader_a, optimizer, criterion, DEVICE)
    acc_a = evaluate(model, test_loader_a, device=DEVICE)
    print(f"  Task A test accuracy after Phase A: {acc_a:.4f}")

    # Phase B (naive: same model, same optimizer, Task B data only)
    print("Training on Task B (digits 5-9) WITHOUT Task A data...")
    for epoch in range(5):
        train_epoch_standard(model, train_loader_b, optimizer, criterion, DEVICE)
    acc_a_after = evaluate(model, test_loader_a, device=DEVICE)
    acc_b_after = evaluate(model, test_loader_b, device=DEVICE)
    print(f"  Task A test accuracy after Phase B: {acc_a_after:.4f}  <-- FORGOTTEN")
    print(f"  Task B test accuracy after Phase B: {acc_b_after:.4f}")
    return {'task_a_final': acc_a_after, 'task_b_final': acc_b_after}


def run_replay():
    """
    Replay buffer: Store 200 examples from Task A. During Task B training,
    mix replay data into each batch.
    EXPECTED RESULT: Task A accuracy stays ~80%+ while Task B learns.
    """
    print("\n" + "=" * 70)
    print("METHOD 2: REPLAY BUFFER")
    print("=" * 70)
    model = SimpleMLP(num_classes=5).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

    # Phase A
    print("Training on Task A (digits 0-4)...")
    for epoch in range(5):
        train_epoch_standard(model, train_loader_a, optimizer, criterion, DEVICE)
    acc_a = evaluate(model, test_loader_a, device=DEVICE)
    print(f"  Task A test accuracy after Phase A: {acc_a:.4f}")

    # Build replay buffer from Task A
    replay_loader = build_replay_loader(train_loader_a, buffer_size=200, batch_size=64)
    print(f"  Built replay buffer with 200 examples from Task A")

    # Phase B with replay
    print("Training on Task B with replay buffer...")
    for epoch in range(5):
        train_epoch_replay(model, train_loader_b, replay_loader, optimizer, criterion, DEVICE, replay_batches=1)
    acc_a_after = evaluate(model, test_loader_a, device=DEVICE)
    acc_b_after = evaluate(model, test_loader_b, device=DEVICE)
    print(f"  Task A test accuracy after Phase B: {acc_a_after:.4f}")
    print(f"  Task B test accuracy after Phase B: {acc_b_after:.4f}")
    return {'task_a_final': acc_a_after, 'task_b_final': acc_b_after}


def run_ewc():
    """
    EWC: After Task A, compute Fisher diagonal. During Task B, penalize
    changes to important weights.
    EXPECTED RESULT: Task A accuracy ~70-85%, Task B accuracy high.
    """
    print("\n" + "=" * 70)
    print("METHOD 3: ELASTIC WEIGHT CONSOLIDATION (EWC)")
    print("=" * 70)
    model = SimpleMLP(num_classes=5).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

    # Phase A
    print("Training on Task A (digits 0-4)...")
    for epoch in range(5):
        train_epoch_standard(model, train_loader_a, optimizer, criterion, DEVICE)
    acc_a = evaluate(model, test_loader_a, device=DEVICE)
    print(f"  Task A test accuracy after Phase A: {acc_a:.4f}")

    # Save old params and compute Fisher
    old_params = {name: param.data.clone() for name, param in model.named_parameters()}
    print("  Computing Fisher Information on Task A data...")
    fisher = compute_fisher_diag(model, train_loader_a, device=DEVICE, num_samples=500)
    mean_fisher = torch.mean(torch.stack([f.mean() for f in fisher.values()])).item()
    print(f"  Mean Fisher info: {mean_fisher:.6f}")

    # Phase B with EWC
    print("Training on Task B with EWC penalty (lambda=1000)...")
    optimizer = optim.SGD(model.parameters(), lr=0.005, momentum=0.9)
    for epoch in range(5):
        train_epoch_ewc(model, train_loader_b, optimizer, criterion, old_params, fisher, lam=1000.0, device=DEVICE)
    acc_a_after = evaluate(model, test_loader_a, device=DEVICE)
    acc_b_after = evaluate(model, test_loader_b, device=DEVICE)
    print(f"  Task A test accuracy after Phase B: {acc_a_after:.4f}")
    print(f"  Task B test accuracy after Phase B: {acc_b_after:.4f}")
    return {'task_a_final': acc_a_after, 'task_b_final': acc_b_after}


def run_progressive():
    """
    Progressive Networks: Train Task A column. Freeze it. Add Task B column
    with lateral connections. Train only Task B parameters.
    EXPECTED RESULT: Task A accuracy stays EXACTLY the same (zero forgetting).
    Task B accuracy may be slightly lower due to smaller B-only capacity.
    """
    print("\n" + "=" * 70)
    print("METHOD 4: PROGRESSIVE NETWORKS")
    print("=" * 70)
    model = ProgressiveMLP(num_classes=5).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    # Phase A: train only Task A column
    optimizer_a = optim.SGD([
        {'params': model.a_fc1.parameters()},
        {'params': model.a_fc2.parameters()},
        {'params': model.a_fc3.parameters()},
    ], lr=0.01, momentum=0.9)

    print("Training Task A column (digits 0-4)...")
    for epoch in range(5):
        model.train()
        for x, y in train_loader_a:
            x, y = x.to(DEVICE), y.to(DEVICE)
            optimizer_a.zero_grad()
            logits, _, _ = model.forward_a(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer_a.step()
    acc_a = evaluate(model, test_loader_a, task='a', device=DEVICE)
    print(f"  Task A test accuracy after Phase A: {acc_a:.4f}")

    # Freeze Task A
    model._freeze_task_a()
    # Phase B: train only Task B column + lateral connections
    optimizer_b = optim.SGD([
        {'params': model.b_fc1.parameters()},
        {'params': model.b_fc2.parameters()},
        {'params': model.b_fc3.parameters()},
        {'params': model.lat1.parameters()},
        {'params': model.lat2.parameters()},
    ], lr=0.01, momentum=0.9)

    print("Training Task B column (digits 5-9) with lateral connections...")
    for epoch in range(5):
        model.train()
        for x, y in train_loader_b:
            x, y = x.to(DEVICE), y.to(DEVICE)
            optimizer_b.zero_grad()
            logits = model.forward_b(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer_b.step()
    acc_a_after = evaluate(model, test_loader_a, task='a', device=DEVICE)
    acc_b_after = evaluate(model, test_loader_b, task='b', device=DEVICE)
    print(f"  Task A test accuracy after Phase B: {acc_a_after:.4f}  <-- ZERO FORGETTING")
    print(f"  Task B test accuracy after Phase B: {acc_b_after:.4f}")
    return {'task_a_final': acc_a_after, 'task_b_final': acc_b_after}


# =============================================================================
# 6. RUN ALL AND PLOT
# =============================================================================

def main():
    print("\n" + "#" * 70)
    print("# PHASE 81 CONTINUAL LEARNING ON SPLIT MNIST")
    print("#" * 70)

    results = {}
    results['naive'] = run_naive()
    results['replay'] = run_replay()
    results['ewc'] = run_ewc()
    results['progressive'] = run_progressive()

    print("\n" + "=" * 70)
    print("FINAL COMPARISON")
    print("=" * 70)
    print(f"{'Method':<20} {'Task A Acc':>12} {'Task B Acc':>12}")
    print("-" * 46)
    for method, res in results.items():
        print(f"{method:<20} {res['task_a_final']:>12.4f} {res['task_b_final']:>12.4f}")
    print("=" * 70)

    # Plot comparison bar chart
    methods = list(results.keys())
    task_a_accs = [results[m]['task_a_final'] for m in methods]
    task_b_accs = [results[m]['task_b_final'] for m in methods]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(methods))
    width = 0.35
    bars1 = ax.bar(x - width/2, task_a_accs, width, label='Task A (digits 0-4)', color='steelblue')
    bars2 = ax.bar(x + width/2, task_b_accs, width, label='Task B (digits 5-9)', color='coral')
    ax.set_ylabel('Test Accuracy')
    ax.set_title('Continual Learning on Split MNIST: Accuracy After Task B Training')
    ax.set_xticks(x)
    ax.set_xticklabels([m.capitalize() for m in methods])
    ax.set_ylim(0, 1.05)
    ax.axhline(y=0.2, color='gray', linestyle='--', alpha=0.5, label='Random (5 classes)')
    ax.legend()
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.savefig('continual_learning_mnist_comparison.png', dpi=150)
    print("\nComparison plot saved to: continual_learning_mnist_comparison.png")


if __name__ == "__main__":
    main()

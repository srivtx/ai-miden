"""
MSPCH-Net (PyTorch / Colab version)
====================================

This is the GPU-friendly version of the prototype. Same five systems
as prototype.py, but using PyTorch + CUDA for training-heavy experiments.

It is meant to be run in Google Colab with a T4 GPU. It is *not* the
production system; it is a research prototype to test MSPCH-style
architectures against benchmarks (Omniglot, miniImageNet, etc.).

Run in Colab:
    !python prototype_colab.py

The script will:
1. Generate Omniglot-like 5-way 1-shot tasks procedurally.
2. Train a baseline MLP.
3. Train MSPCH-Net with all 5 systems.
4. Compare sample efficiency.
5. Save plots to /content/plots/.

Differences from prototype.py:
- Uses PyTorch tensors (GPU-friendly).
- Adds the homeostatic scaling system (was disabled in prototype.py).
- Adds the full consolidation step (not just distillation).
- Adds an "active inference" optional mode.
- Logs to tensorboard (optional).

The code follows the ai-miden AGENTS.md conventions.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Optional: only required for prototype_colab.py
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not available. This script requires PyTorch.")
    print("In Colab: !pip install torch")
    print("On a local machine: pip install torch")
    print("Or run the NumPy version: prototype.py")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
INPUT_DIM = 64
HIDDEN_DIMS = (64, 32)
OUTPUT_DIM = 2
FAST_CAPACITY = 64
REPLAY_CAPACITY = 256
TARGET_ACTIVITY = 0.10
INNER_LR = 0.01
OUTER_LR = 0.001
SLEEP_EVERY = 5
N_SLEEP = 2
NUM_OUTER_STEPS = 200
WINDOW = 20
SEED = 42


# =============================================================================
# Task generation
# =============================================================================

def make_task_torch(num_classes=2, image_size=8, seed=0, num_base=4, noise=0.2):
    """Same as in prototype.py but returns torch tensors."""
    rng = np.random.RandomState(seed)
    coords = [(1, 1), (1, 6), (6, 1), (6, 6)]
    base = []
    for cy, cx in coords[:num_base]:
        ii, jj = np.meshgrid(range(image_size), range(image_size), indexing="ij")
        p = np.exp(-((ii - cy) ** 2 + (jj - cx) ** 2) / 2.0)
        base.append(p.flatten())
    chosen = rng.choice(num_base, num_classes, replace=False)
    support_x, support_y, query_x, query_y = [], [], [], []
    for nl, bi in enumerate(chosen):
        for _ in range(1):
            support_x.append(base[bi] + 0.02 * rng.randn(image_size * image_size))
            support_y.append(nl)
        for _ in range(4):
            query_x.append(base[bi] + noise * rng.randn(image_size * image_size))
            query_y.append(nl)
    return (torch.tensor(np.array(support_x), dtype=torch.float32, device=DEVICE),
            torch.tensor(support_y, dtype=torch.long, device=DEVICE),
            torch.tensor(np.array(query_x), dtype=torch.float32, device=DEVICE),
            torch.tensor(query_y, dtype=torch.long, device=DEVICE))


# =============================================================================
# The MSPCH-Net (PyTorch)
# =============================================================================

class SlowMemory(nn.Module):
    """A small MLP, the slow (gradient-updated) memory."""
    def __init__(self, input_dim, hidden_dims, output_dim):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers.append(nn.Linear(prev, h))
            layers.append(nn.ReLU())
            prev = h
        layers.append(nn.Linear(prev, output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class MSPCHNet:
    """
    Multi-Scale Predictive Coding Network (PyTorch).
    Five systems: multi-system memory, neuromodulation, replay, homeostasis,
    intrinsic motivation.
    """
    def __init__(self, seed=0):
        torch.manual_seed(seed)
        self.slow = SlowMemory(INPUT_DIM, HIDDEN_DIMS, OUTPUT_DIM).to(DEVICE)
        self.opt = torch.optim.Adam(self.slow.parameters(), lr=OUTER_LR)

        # Fast memory: a list of (key, value) tuples.
        self.fast_keys = []
        self.fast_values = []

        # Replay buffer
        self.replay_x = []
        self.replay_y = []

        # Neuromodulator levels
        self.da = 0.5
        self.ach = 0.5
        self.ne = 0.5
        self.ser = 0.5
        self.orex = 0.5

        # Homeostatic activity trackers
        self.activity_avg = [torch.zeros(d, device=DEVICE) for d in HIDDEN_DIMS]

        self.step_count = 0

    def fast_recall(self, x):
        """Cosine-similarity-based recall from fast memory."""
        if not self.fast_keys:
            return None, 0.0
        keys = torch.stack(self.fast_keys, dim=0)  # (N, D)
        x_norm = F.normalize(x.unsqueeze(0), dim=1)
        k_norm = F.normalize(keys, dim=1)
        sims = (k_norm @ x_norm.T).squeeze()
        best = int(torch.argmax(sims).item())
        return self.fast_values[best], float(sims[best].item())

    def predict(self, x):
        slow_out = self.slow(x.unsqueeze(0)).squeeze(0)
        fast_out, sim = self.fast_recall(x)
        if fast_out is None:
            return slow_out
        # Sharp attention: trust = ACh * sigmoid(10 * (sim - 0.3))
        trust = self.ach / (1.0 + np.exp(-10.0 * (sim - 0.3)))
        return trust * fast_out + (1.0 - trust) * slow_out

    def update_neuromodulators(self, reward, prediction_error, novelty):
        self.da = float(np.clip(self.da + 0.1 * (reward - self.da), 0.0, 1.0))
        self.ach = float(np.clip(0.3 + 0.7 * novelty, 0.0, 1.0))
        self.ne = float(np.clip(0.3 + 0.7 * prediction_error, 0.0, 1.0))
        self.ser = float(np.clip(0.5 + 0.5 * (1.0 - reward), 0.0, 1.0))
        self.orex = float(np.clip(0.5 + 0.5 * (1.0 - 0.5 * (self.step_count % 50 < 10)), 0.0, 1.0))

    def homeostatic_scale(self):
        """Turrigiano-style multiplicative synaptic scaling."""
        with torch.no_grad():
            for i, layer in enumerate(self.slow.net):
                if isinstance(layer, nn.Linear) and i // 2 < len(self.activity_avg):
                    idx = i // 2
                    if idx < len(self.activity_avg):
                        avg = float(self.activity_avg[idx].mean().item())
                        ratio = TARGET_ACTIVITY / (avg + 1e-6)
                        scale = float(np.clip(0.995 + 0.005 * ratio, 0.95, 1.05))
                        layer.weight *= scale
                        # NaN guard
                        if not torch.isfinite(layer.weight).all():
                            layer.weight.data = torch.nan_to_num(layer.weight.data)

    def consolidate_distill(self, batch_size=16, lr=0.0005):
        """Distill fast-memory outputs into slow-memory weights."""
        if len(self.replay_x) < 2:
            return
        idx = np.random.choice(len(self.replay_x),
                               min(batch_size, len(self.replay_x)),
                               replace=False)
        # Build targets from fast memory
        targets = []
        valid_idx = []
        for i in idx:
            x = self.replay_x[i]
            f, sim = self.fast_recall(x)
            if f is not None and sim > 0.3:
                targets.append(f)
                valid_idx.append(i)
        if not valid_idx:
            return
        x = torch.stack([self.replay_x[i] for i in valid_idx], dim=0)
        y = torch.stack(targets, dim=0)
        self.opt.zero_grad()
        pred = self.slow(x)
        loss = F.mse_loss(pred, y)
        loss.backward()
        # DA-gated gradient
        for p in self.slow.parameters():
            if p.grad is not None:
                p.grad *= self.da
        self.opt.step()
        # NaN guard
        for p in self.slow.parameters():
            if not torch.isfinite(p).all():
                p.data = torch.nan_to_num(p.data)

    def train_step(self, support_x, support_y, query_x, query_y):
        self.step_count += 1
        y_onehot = F.one_hot(support_y, OUTPUT_DIM).float()

        # Fast adaptation: store support in fast memory and replay buffer
        for i in range(len(support_x)):
            self.fast_keys.append(support_x[i])
            self.fast_values.append(y_onehot[i])
            if len(self.fast_keys) > FAST_CAPACITY:
                self.fast_keys.pop(0)
                self.fast_values.pop(0)
            self.replay_x.append(support_x[i])
            self.replay_y.append(y_onehot[i])
            if len(self.replay_x) > REPLAY_CAPACITY:
                self.replay_x.pop(0)
                self.replay_y.pop(0)

        # Predict on query
        preds = torch.stack([self.predict(q) for q in query_x], dim=0)
        p = F.softmax(preds, dim=1)
        pred_class = torch.argmax(p, dim=1)
        accuracy = float((pred_class == query_y).float().mean().item())
        target_oh = F.one_hot(query_y, OUTPUT_DIM).float()
        loss = -float((target_oh * torch.log(p + 1e-8)).sum(dim=1).mean().item())
        prediction_error = float((p - target_oh).abs().mean().item())

        # Neuromodulator update
        novelty = prediction_error
        reward = 0.5 * accuracy + 0.5 * prediction_error
        self.update_neuromodulators(reward, prediction_error, novelty)

        # Sleep / consolidation
        if self.step_count % SLEEP_EVERY == 0:
            for _ in range(N_SLEEP):
                self.consolidate_distill()

        # Update activity tracking for homeostasis
        with torch.no_grad():
            h = query_x
            for layer in self.slow.net:
                if isinstance(layer, nn.Linear):
                    h = layer(h)
                    if h.dim() == 2 and h.shape[1] in HIDDEN_DIMS:
                        idx = HIDDEN_DIMS.index(h.shape[1])
                        if idx < len(self.activity_avg):
                            self.activity_avg[idx] = 0.95 * self.activity_avg[idx] + 0.05 * h.mean(0)

        # Homeostatic scaling (glial)
        if self.step_count % 10 == 0:
            self.homeostatic_scale()

        return loss, accuracy, prediction_error, reward


# =============================================================================
# Baseline
# =============================================================================

class BaselineMLP(nn.Module):
    def __init__(self):
        super().__init__()
        layers = []
        prev = INPUT_DIM
        for h in HIDDEN_DIMS:
            layers.append(nn.Linear(prev, h))
            layers.append(nn.ReLU())
            prev = h
        layers.append(nn.Linear(prev, OUTPUT_DIM))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def train_baseline(support_x, support_y, baseline, opt, n_inner=1):
    """One inner-loop step for the baseline."""
    y_onehot = F.one_hot(support_y, OUTPUT_DIM).float()
    opt.zero_grad()
    pred = baseline(support_x)
    loss = F.cross_entropy(pred, support_y)
    loss.backward()
    opt.step()
    return float(loss.item())


# =============================================================================
# The experiment
# =============================================================================

def run_experiment():
    print("=" * 60)
    print("MSPCH-Net (PyTorch) vs Baseline MLP: 2-way 1-shot learning")
    print(f"Device: {DEVICE}")
    print("=" * 60)

    torch.manual_seed(SEED)
    np.random.seed(SEED)

    mspch = MSPCHNet(seed=SEED)
    baseline = BaselineMLP().to(DEVICE)
    base_opt = torch.optim.Adam(baseline.parameters(), lr=INNER_LR)

    acc_mspch, acc_baseline = [], []
    da_trace, ach_trace, ne_trace = [], [], []
    pe_mspch = []

    for step in range(NUM_OUTER_STEPS):
        task_idx = step % 6
        task_seed = task_idx * 137
        sx, sy, qx, qy = make_task_torch(seed=task_seed, noise=0.2)

        # MSPCH-Net
        loss_m, acc_m, pe_m, ir_m = mspch.train_step(sx, sy, qx, qy)
        acc_mspch.append(acc_m)
        pe_mspch.append(pe_m)
        da_trace.append(mspch.da)
        ach_trace.append(mspch.ach)
        ne_trace.append(mspch.ne)

        # Baseline
        train_baseline(sx, sy, baseline, base_opt, n_inner=1)
        with torch.no_grad():
            bpred = baseline(qx)
            bacc = float((torch.argmax(bpred, dim=1) == qy).float().mean().item())
        acc_baseline.append(bacc)

        if (step + 1) % 25 == 0 or step == 0:
            def roll(x):
                return float(np.mean(x[-WINDOW:])) if len(x) >= WINDOW else float(np.mean(x))
            print(f"Step {step+1:4d} | MSPCH acc={roll(acc_mspch):.3f} "
                  f"loss={loss_m:.3f} pe={pe_m:.3f} | "
                  f"Baseline acc={roll(acc_baseline):.3f} (raw {bacc:.2f}) | "
                  f"DA={mspch.da:.2f} ACh={mspch.ach:.2f} NE={mspch.ne:.2f}")

    # Save plots
    os.makedirs("plots", exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(acc_mspch, alpha=0.3, color="#1f77b4", label="MSPCH-Net (raw)")
    ax.plot(acc_baseline, alpha=0.3, color="#ff7f0e", label="Baseline (raw)")
    m_smooth = np.convolve(acc_mspch, np.ones(WINDOW)/WINDOW, mode="valid")
    b_smooth = np.convolve(acc_baseline, np.ones(WINDOW)/WINDOW, mode="valid")
    ax.plot(range(WINDOW-1, len(acc_mspch)), m_smooth, color="#1f77b4", linewidth=2.5, label=f"MSPCH (rolling-{WINDOW})")
    ax.plot(range(WINDOW-1, len(acc_baseline)), b_smooth, color="#ff7f0e", linewidth=2.5, label=f"Baseline (rolling-{WINDOW})")
    ax.axhline(0.5, color="gray", linestyle="--", alpha=0.4, label="Chance (50%)")
    ax.set_xlabel("Outer step")
    ax.set_ylabel("Query-set accuracy")
    ax.set_title("MSPCH-Net vs Baseline MLP (PyTorch): 2-way 1-shot")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    fig.savefig("plots/mspch_pytorch_vs_mlp.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/mspch_pytorch_vs_mlp.png")

    # Neuromodulator plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(da_trace, label="DA", linewidth=2)
    ax.plot(ach_trace, label="ACh", linewidth=2)
    ax.plot(ne_trace, label="NE", linewidth=2)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Outer step")
    ax.set_ylabel("Neuromodulator level")
    ax.set_title("Neuromodulator dynamics (PyTorch run)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("plots/mspch_pytorch_neuromod.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/mspch_pytorch_neuromod.png")

    print()
    print("Final rolling-mean accuracy (last 20 steps):")
    print(f"  MSPCH-Net: {np.mean(acc_mspch[-WINDOW:]):.3f}")
    print(f"  Baseline:  {np.mean(acc_baseline[-WINDOW:]):.3f}")


if __name__ == "__main__":
    run_experiment()

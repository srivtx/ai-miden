#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 112 — Multi-Token Prediction Concepts
LOCAL NumPy demonstration of MTP training dynamics.

This script simulates a tiny transformer-like language model with
multiple prediction heads to show:
  - How one forward pass produces N next-token predictions
  - MTP loss vs standard next-token loss
  - Gradient norm comparison (richer gradients from MTP)
  - Loss surface visualization
  - Token probability distributions at multiple offsets
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. TOY VOCABULARY AND DATASET
# ---------------------------------------------------------------------------
# We use a tiny vocabulary so the softmax and cross-entropy are cheap.
VOCAB_SIZE = 16
SEQ_LEN = 32
BATCH_SIZE = 8
N_HEADS = 4  # predict t+1, t+2, t+3, t+4
SEED = 112
np.random.seed(SEED)

# Generate synthetic sequences with Markov structure so there is
# learnable correlation between nearby tokens.
def generate_sequence(length):
    seq = [0]
    for _ in range(length - 1):
        # Next token is strongly correlated with previous token
        next_tok = (seq[-1] + np.random.randint(1, 4)) % VOCAB_SIZE
        seq.append(next_tok)
    return np.array(seq, dtype=np.int32)

data = np.stack([generate_sequence(SEQ_LEN) for _ in range(BATCH_SIZE)])

# ---------------------------------------------------------------------------
# 2. TINY MODEL DEFINITION (NumPy)
# ---------------------------------------------------------------------------
# We simulate a single linear projection + softmax for each head.
# The "backbone" is a simple embedding lookup + positional encoding.
# This is sufficient to demonstrate the MTP mechanics.

class TinyMTPModel:
    def __init__(self, vocab_size, embed_dim, n_heads):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.n_heads = n_heads

        # Embedding matrix: vocab -> embed
        self.W_embed = np.random.randn(vocab_size, embed_dim).astype(np.float32) * 0.1
        # Positional encoding (fixed, not learned, for simplicity)
        self.pos_enc = np.random.randn(SEQ_LEN, embed_dim).astype(np.float32) * 0.01

        # Each head is a linear projection embed -> vocab
        # Head 0 predicts t+1, head 1 predicts t+2, etc.
        self.W_heads = [np.random.randn(embed_dim, vocab_size).astype(np.float32) * 0.1
                        for _ in range(n_heads)]

        # Single hidden MLP to simulate a tiny transformer layer
        self.W_hid = np.random.randn(embed_dim, embed_dim).astype(np.float32) * 0.1
        self.b_hid = np.zeros(embed_dim, dtype=np.float32)

    def forward(self, token_ids):
        """
        token_ids: [batch, seq_len]
        Returns logits_list: list of [batch, seq_len - offset, vocab_size]
        and hidden states [batch, seq_len, embed_dim]
        """
        batch_size, seq_len = token_ids.shape
        # Embed tokens
        h = self.W_embed[token_ids]  # [batch, seq_len, embed_dim]
        h = h + self.pos_enc[:seq_len]  # add positional info

        # Tiny nonlinearity (simulates one transformer layer)
        h = np.tanh(h @ self.W_hid + self.b_hid)

        # Compute logits for each head
        logits_list = []
        for i in range(self.n_heads):
            # Head i uses hidden states up to seq_len - i - 1
            # to predict tokens at offset i+1
            valid_len = seq_len - (i + 1)
            if valid_len <= 0:
                logits_list.append(None)
                continue
            h_slice = h[:, :valid_len, :]  # [batch, valid_len, embed_dim]
            # Project: [batch, valid_len, embed_dim] @ [embed_dim, vocab]
            logits = h_slice @ self.W_heads[i]  # [batch, valid_len, vocab]
            logits_list.append(logits)
        return logits_list, h

    def parameters(self):
        """Flat list of parameter arrays for gradient checking."""
        return [self.W_embed] + self.W_heads + [self.W_hid, self.b_hid]


# ---------------------------------------------------------------------------
# 3. LOSS FUNCTIONS
# ---------------------------------------------------------------------------

def softmax(x):
    """Numerically stable softmax over last axis."""
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / np.sum(e, axis=-1, keepdims=True)


def cross_entropy(logits, targets):
    """
    logits: [batch, length, vocab]
    targets: [batch, length] int
    """
    probs = softmax(logits)
    batch, length = targets.shape
    flat_probs = probs.reshape(-1, probs.shape[-1])
    flat_targets = targets.reshape(-1)
    # gather correct class probabilities
    correct_probs = flat_probs[np.arange(flat_targets.shape[0]), flat_targets]
    ce = -np.log(np.maximum(correct_probs, 1e-12))
    return float(np.mean(ce))


def mtp_loss(model, token_ids):
    """Average CE over N heads."""
    logits_list, _ = model.forward(token_ids)
    losses = []
    for i in range(model.n_heads):
        if logits_list[i] is None:
            continue
        targets = token_ids[:, (i + 1):]
        # logits are already truncated to valid length
        losses.append(cross_entropy(logits_list[i], targets))
    return float(np.mean(losses))


def standard_loss(model, token_ids):
    """Only use head 0 (t+1 prediction)."""
    logits_list, _ = model.forward(token_ids)
    targets = token_ids[:, 1:]
    return cross_entropy(logits_list[0], targets)


# ---------------------------------------------------------------------------
# 4. GRADIENT COMPUTATION (FINITE DIFFERENCES)
# ---------------------------------------------------------------------------
# We use central differences to approximate gradients for the tiny model.
# This avoids writing full backprop by hand while still showing gradient
# norms accurately enough for demonstration.

def compute_gradients(loss_fn, model, token_ids):
    """Returns list of gradients and the scalar loss."""
    eps = 1e-5
    grads = []
    base_loss = loss_fn(model, token_ids)
    for param in model.parameters():
        grad = np.zeros_like(param)
        it = np.nditer(param, flags=['multi_index'], op_flags=['readwrite'])
        while not it.finished:
            idx = it.multi_index
            orig = param[idx]
            param[idx] = orig + eps
            loss_plus = loss_fn(model, token_ids)
            param[idx] = orig - eps
            loss_minus = loss_fn(model, token_ids)
            param[idx] = orig
            grad[idx] = (loss_plus - loss_minus) / (2 * eps)
            it.iternext()
        grads.append(grad)
    return grads, base_loss


# ---------------------------------------------------------------------------
# 5. COMPARE STANDARD VS MTP
# ---------------------------------------------------------------------------
print("=" * 70)
print("PHASE 112: Multi-Token Prediction Concepts")
print("=" * 70)

model_mtp = TinyMTPModel(VOCAB_SIZE, embed_dim=32, n_heads=N_HEADS)
# For fair comparison, standard model uses the same architecture but only head 0
model_std = TinyMTPModel(VOCAB_SIZE, embed_dim=32, n_heads=1)

# Copy initial embeddings so both start from the same representation
model_std.W_embed = model_mtp.W_embed.copy()
model_std.pos_enc = model_mtp.pos_enc.copy()
model_std.W_hid = model_mtp.W_hid.copy()
model_std.b_hid = model_mtp.b_hid.copy()
model_std.W_heads[0] = model_mtp.W_heads[0].copy()

print("\n--- Loss comparison on same batch ---")
loss_mtp = mtp_loss(model_mtp, data)
loss_std = standard_loss(model_std, data)
print(f"MTP loss (avg over {N_HEADS} heads): {loss_mtp:.4f}")
print(f"Standard loss (head 0 only):         {loss_std:.4f}")

print("\n--- Gradient norm comparison ---")
grads_mtp, _ = compute_gradients(mtp_loss, model_mtp, data)
grads_std, _ = compute_gradients(standard_loss, model_std, data)

mtp_norms = [float(np.linalg.norm(g)) for g in grads_mtp]
std_norms = [float(np.linalg.norm(g)) for g in grads_std]
print(f"MTP total gradient norm:  {sum(mtp_norms):.4f}")
print(f"Std total gradient norm:  {sum(std_norms):.4f}")
print(f"Ratio (MTP/Std):          {sum(mtp_norms)/(sum(std_norms)+1e-12):.2f}")

# ---------------------------------------------------------------------------
# 6. PLOT: GRADIENT NORMS PER PARAMETER GROUP
# ---------------------------------------------------------------------------
os.makedirs("src/phase112", exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 5))
x_labels = ['Embed', 'Head0', 'Head1', 'Head2', 'Head3', 'W_hid', 'b_hid']
ax.bar(np.arange(len(x_labels)) - 0.2, mtp_norms, width=0.4, label='MTP', alpha=0.8)
# Pad std_norms to match length for visualization
std_norms_padded = std_norms + [0.0] * (len(x_labels) - len(std_norms))
ax.bar(np.arange(len(x_labels)) + 0.2, std_norms_padded, width=0.4, label='Standard', alpha=0.8)
ax.set_xticks(range(len(x_labels)))
ax.set_xticklabels(x_labels)
ax.set_ylabel('Gradient L2 norm')
ax.set_title('Gradient Norms: MTP vs Standard Next-Token')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('src/phase112/mtp_gradient_norms.png', dpi=150)
plt.close()
print("\nSaved: src/phase112/mtp_gradient_norms.png")

# ---------------------------------------------------------------------------
# 7. PLOT: TOKEN PROBABILITY DISTRIBUTIONS
# ---------------------------------------------------------------------------
# Show how the probability mass shifts across head offsets.

logits_list, _ = model_mtp.forward(data)
fig, axes = plt.subplots(1, N_HEADS, figsize=(16, 3))
for i in range(N_HEADS):
    if logits_list[i] is None:
        continue
    probs = softmax(logits_list[i])  # [batch, len, vocab]
    # Average over batch and positions
    avg_probs = np.mean(probs, axis=(0, 1))
    axes[i].bar(range(VOCAB_SIZE), avg_probs, alpha=0.7)
    axes[i].set_title(f'Head {i+1} (t+{i+1})')
    axes[i].set_xlabel('Token ID')
    axes[i].set_ylabel('Avg probability')
    axes[i].set_ylim(0, max(avg_probs) * 1.2)
    axes[i].grid(True, alpha=0.3, axis='y')

plt.suptitle('Average Token Probability Distributions per Head')
plt.tight_layout()
plt.savefig('src/phase112/mtp_token_distribution.png', dpi=150)
plt.close()
print("Saved: src/phase112/mtp_token_distribution.png")

# ---------------------------------------------------------------------------
# 8. LOSS SURFACE VISUALIZATION
# ---------------------------------------------------------------------------
# Vary one parameter dimension and plot loss for both MTP and standard.

param_idx = (5, 3)  # W_embed[5, 3]
values = np.linspace(-0.5, 0.5, 41)
losses_mtp_scan = []
losses_std_scan = []

orig_mtp = model_mtp.W_embed[param_idx]
orig_std = model_std.W_embed[param_idx]
for v in values:
    model_mtp.W_embed[param_idx] = v
    model_std.W_embed[param_idx] = v
    losses_mtp_scan.append(mtp_loss(model_mtp, data))
    losses_std_scan.append(standard_loss(model_std, data))

model_mtp.W_embed[param_idx] = orig_mtp
model_std.W_embed[param_idx] = orig_std

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(values, losses_mtp_scan, label='MTP', marker='o', markersize=3)
ax.plot(values, losses_std_scan, label='Standard', marker='s', markersize=3)
ax.set_xlabel('W_embed[5, 3] value')
ax.set_ylabel('Loss')
ax.set_title('Loss Surface Slice: MTP vs Standard')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('src/phase112/mtp_loss_surface.png', dpi=150)
plt.close()
print("Saved: src/phase112/mtp_loss_surface.png")

# ---------------------------------------------------------------------------
# 9. PER-HEAD LOSS BREAKDOWN
# ---------------------------------------------------------------------------
logits_list, _ = model_mtp.forward(data)
head_losses = []
for i in range(N_HEADS):
    if logits_list[i] is None:
        continue
    targets = data[:, (i + 1):]
    head_losses.append(cross_entropy(logits_list[i], targets))

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(range(1, len(head_losses) + 1), head_losses, alpha=0.8)
ax.set_xticks(range(1, len(head_losses) + 1))
ax.set_xticklabels([f't+{i+1}' for i in range(len(head_losses))])
ax.set_ylabel('Cross-entropy loss')
ax.set_title('Per-Head Loss (MTP)')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('src/phase112/mtp_per_head_loss.png', dpi=150)
plt.close()
print("Saved: src/phase112/mtp_per_head_loss.png")

print("\n--- Per-head loss values ---")
for i, l in enumerate(head_losses):
    print(f"Head {i+1} (t+{i+1}): {l:.4f}")

print("\n" + "=" * 70)
print("Phase 112 concepts demonstration complete.")
print("=" * 70)

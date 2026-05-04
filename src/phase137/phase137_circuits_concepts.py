#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 137 — Circuit Discovery Concepts
LOCAL NumPy demonstration of automated circuit finding in a toy transformer.

This script simulates a small transformer and uses ablations to discover
which components (attention heads, MLP neurons) implement a specific task.
We then test faithfulness and completeness of the discovered circuit.

Why NumPy? Real circuit discovery on 7B models requires GPU access and
hours of computation. NumPy lets us demonstrate the algorithm — ablation,
pruning, and evaluation — in seconds on any laptop.
"""

import os
import numpy as np

# Use non-interactive backend so this script runs headless on any machine.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. TOY TASK: SEQUENCE COPYING WITH A TWIST
# ---------------------------------------------------------------------------
# The model sees a sequence of tokens where two special "marker" tokens
# appear. The task is to copy the token that appears immediately after
# the first marker to the output position. This mimics the IOI structure:
# attend to a specific position, copy its value, and suppress distractors.

VOCAB_SIZE = 16
SEQ_LEN = 8
D_MODEL = 32
N_LAYERS = 3
N_HEADS = 4
HEAD_DIM = D_MODEL // N_HEADS  # 8
MLP_HIDDEN = 64

np.random.seed(137)


def generate_task_batch(batch_size=256):
    """
    Generate synthetic IOI-like tasks.
    Tokens 0-9 are content. Token 10 is marker A. Token 11 is marker B.
    The prompt is: [random tokens] + [marker A] + [target token] + [random] + [marker B] + [query]
    The model must output the target token (the one after marker A).
    """
    tokens = np.random.randint(0, 10, size=(batch_size, SEQ_LEN))
    target = np.random.randint(0, 10, size=batch_size)
    marker_a_pos = 2
    marker_b_pos = 5
    query_pos = 6
    tokens[:, marker_a_pos] = 10  # marker A
    tokens[:, marker_a_pos + 1] = target  # target token
    tokens[:, marker_b_pos] = 11  # marker B
    tokens[:, query_pos] = 12  # query token
    return tokens, target


# ---------------------------------------------------------------------------
# 2. TOY TRANSFORMER IN NUMPY
# ---------------------------------------------------------------------------
# We build a tiny transformer with random weights. The goal is not to train
# it but to study its existing computation graph via ablations.

class ToyTransformer:
    def __init__(self):
        # Embeddings
        self.embed = np.random.randn(VOCAB_SIZE, D_MODEL).astype(np.float32) * 0.1
        self.pos_embed = np.random.randn(SEQ_LEN, D_MODEL).astype(np.float32) * 0.1

        # Attention parameters per layer
        self.W_q = []
        self.W_k = []
        self.W_v = []
        self.W_o = []
        self.b_q = []
        self.b_k = []
        self.b_v = []
        self.b_o = []

        # MLP parameters per layer
        self.W_mlp_up = []
        self.W_mlp_down = []
        self.b_mlp_up = []
        self.b_mlp_down = []

        for _ in range(N_LAYERS):
            # Attention: each head gets its own projection matrices
            self.W_q.append(np.random.randn(N_HEADS, D_MODEL, HEAD_DIM).astype(np.float32) * 0.1)
            self.W_k.append(np.random.randn(N_HEADS, D_MODEL, HEAD_DIM).astype(np.float32) * 0.1)
            self.W_v.append(np.random.randn(N_HEADS, D_MODEL, HEAD_DIM).astype(np.float32) * 0.1)
            self.W_o.append(np.random.randn(N_HEADS, HEAD_DIM, D_MODEL).astype(np.float32) * 0.1)
            self.b_q.append(np.zeros((N_HEADS, 1, HEAD_DIM), dtype=np.float32))
            self.b_k.append(np.zeros((N_HEADS, 1, HEAD_DIM), dtype=np.float32))
            self.b_v.append(np.zeros((N_HEADS, 1, HEAD_DIM), dtype=np.float32))
            self.b_o.append(np.zeros((1, D_MODEL), dtype=np.float32))

            # MLP
            self.W_mlp_up.append(np.random.randn(D_MODEL, MLP_HIDDEN).astype(np.float32) * 0.1)
            self.W_mlp_down.append(np.random.randn(MLP_HIDDEN, D_MODEL).astype(np.float32) * 0.1)
            self.b_mlp_up.append(np.zeros((1, MLP_HIDDEN), dtype=np.float32))
            self.b_mlp_down.append(np.zeros((1, D_MODEL), dtype=np.float32))

        # Output projection
        self.W_out = np.random.randn(D_MODEL, VOCAB_SIZE).astype(np.float32) * 0.1
        self.b_out = np.zeros((1, VOCAB_SIZE), dtype=np.float32)

        # Layer norms (simplified: just scaling, no learnable shift)
        self.ln_scale = [np.ones((1, D_MODEL), dtype=np.float32) for _ in range(N_LAYERS)]

    def softmax(self, x):
        # x shape: (..., seq, seq)
        e = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e / np.sum(e, axis=-1, keepdims=True)

    def gelu(self, x):
        # Approximate GELU
        return 0.5 * x * (1 + np.tanh(0.7978845608 * (x + 0.044715 * x ** 3)))

    def layer_norm(self, x, scale):
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        return scale * (x - mean) / np.sqrt(var + 1e-5)

    def forward(self, tokens, ablate_heads=None, ablate_mlps=None):
        """
        Forward pass with optional ablations.
        ablate_heads: set of (layer, head) tuples to zero out
        ablate_mlps: set of layer indices to zero out
        """
        if ablate_heads is None:
            ablate_heads = set()
        if ablate_mlps is None:
            ablate_mlps = set()

        B, T = tokens.shape
        x = self.embed[tokens] + self.pos_embed[None, :T, :]  # (B, T, D)

        for layer in range(N_LAYERS):
            # --- Attention ---
            attn_out = np.zeros_like(x)
            for h in range(N_HEADS):
                q = x @ self.W_q[layer][h] + self.b_q[layer][h]  # (B, T, H)
                k = x @ self.W_k[layer][h] + self.b_k[layer][h]  # (B, T, H)
                v = x @ self.W_v[layer][h] + self.b_v[layer][h]  # (B, T, H)

                scores = q @ np.swapaxes(k, -2, -1) / np.sqrt(HEAD_DIM)  # (B, T, T)
                # Causal mask
                mask = np.tril(np.ones((T, T)))[None, :, :]
                scores = np.where(mask, scores, -1e9)
                attn_weights = self.softmax(scores)  # (B, T, T)
                head_out = attn_weights @ v  # (B, T, H)
                head_proj = head_out @ self.W_o[layer][h]  # (B, T, D)

                if (layer, h) not in ablate_heads:
                    attn_out += head_proj
                # else: head is ablated (contributes zero)

            x = self.layer_norm(x + attn_out, self.ln_scale[layer])

            # --- MLP ---
            if layer not in ablate_mlps:
                mlp_hidden = self.gelu(x @ self.W_mlp_up[layer] + self.b_mlp_up[layer])
                mlp_out = mlp_hidden @ self.W_mlp_down[layer] + self.b_mlp_down[layer]
                x = self.layer_norm(x + mlp_out, self.ln_scale[layer])
            else:
                # MLP ablated: residual connection only
                x = self.layer_norm(x, self.ln_scale[layer])

        # Output logits at query position (index 6)
        logits = x[:, 6, :] @ self.W_out + self.b_out  # (B, VOCAB_SIZE)
        return logits


# ---------------------------------------------------------------------------
# 3. EVALUATE FULL MODEL
# ---------------------------------------------------------------------------
model = ToyTransformer()
tokens, targets = generate_task_batch(batch_size=512)
logits_full = model.forward(tokens)
preds_full = np.argmax(logits_full, axis=-1)
acc_full = float(np.mean(preds_full == targets))
print("=" * 70)
print("PHASE 137: Circuit Discovery Concepts")
print("=" * 70)
print(f"\nFull model accuracy: {acc_full:.3f}")

# ---------------------------------------------------------------------------
# 4. SINGLE-COMPONENT ABLATIONS
# ---------------------------------------------------------------------------
# We ablate each attention head and each MLP individually, measuring the
# drop in accuracy. A large drop means the component is important for the task.

head_importance = []
mlp_importance = []

print("\n--- Single-component ablation study ---")
print(f"{'Component':<20}  {'Accuracy':>10}  {'Drop':>10}")
print("-" * 45)

# Ablate heads
for layer in range(N_LAYERS):
    for h in range(N_HEADS):
        logits = model.forward(tokens, ablate_heads={(layer, h)})
        acc = float(np.mean(np.argmax(logits, axis=-1) == targets))
        drop = acc_full - acc
        head_importance.append(((layer, h), acc, drop))
        print(f"L{layer}H{h:<13}  {acc:>10.3f}  {drop:>10.3f}")

# Ablate MLPs
for layer in range(N_LAYERS):
    logits = model.forward(tokens, ablate_mlps={layer})
    acc = float(np.mean(np.argmax(logits, axis=-1) == targets))
    drop = acc_full - acc
    mlp_importance.append((layer, acc, drop))
    print(f"L{layer} MLP{'':<9}  {acc:>10.3f}  {drop:>10.3f}")

# Sort by drop (importance)
head_importance.sort(key=lambda x: x[2], reverse=True)
mlp_importance.sort(key=lambda x: x[2], reverse=True)

print(f"\nMost important head: {head_importance[0][0]} (drop {head_importance[0][2]:.3f})")
print(f"Most important MLP:  L{mlp_importance[0][0]} (drop {mlp_importance[0][2]:.3f})")

# ---------------------------------------------------------------------------
# 5. GREEDY PRUNING TO FIND MINIMAL CIRCUIT
# ---------------------------------------------------------------------------
# Starting from the full model, we iteratively remove the least important
# component that is still present. We stop when accuracy drops below a threshold.
# This gives us a candidate minimal circuit.

THRESHOLD = 0.02  # allow up to 2% accuracy drop from full model
min_acc = acc_full - THRESHOLD

# Start with all components active
active_heads = {(l, h) for l in range(N_LAYERS) for h in range(N_HEADS)}
active_mlps = set(range(N_LAYERS))

circuit_history = []

while True:
    # Try removing each active component, find the one with smallest drop
    best_candidate = None
    best_acc = -1.0

    for comp in list(active_heads):
        test_heads = active_heads - {comp}
        logits = model.forward(tokens, ablate_heads=active_heads - test_heads,
                               ablate_mlps=active_mlps)
        # Note: ablate_heads expects the set to ablate, so pass the complement
        logits = model.forward(tokens, ablate_heads=active_heads - test_heads,
                               ablate_mlps=set(range(N_LAYERS)) - active_mlps)
        acc = float(np.mean(np.argmax(logits, axis=-1) == targets))
        if acc > best_acc:
            best_acc = acc
            best_candidate = ('head', comp)

    for comp in list(active_mlps):
        test_mlps = active_mlps - {comp}
        logits = model.forward(tokens, ablate_heads=set(range(N_LAYERS)) - active_heads,
                               ablate_mlps=active_mlps - test_mlps)
        acc = float(np.mean(np.argmax(logits, axis=-1) == targets))
        if acc > best_acc:
            best_acc = acc
            best_candidate = ('mlp', comp)

    if best_acc < min_acc or best_candidate is None:
        break

    # Remove the least harmful component
    if best_candidate[0] == 'head':
        active_heads.remove(best_candidate[1])
    else:
        active_mlps.remove(best_candidate[1])

    circuit_history.append((len(active_heads) + len(active_mlps), best_acc))
    print(f"Pruned {best_candidate[0]} {best_candidate[1]}, size {len(active_heads)+len(active_mlps)}, acc {best_acc:.3f}")

print(f"\nMinimal circuit size: {len(active_heads)} heads + {len(active_mlps)} MLPs = {len(active_heads)+len(active_mlps)} components")
print(f"Circuit accuracy: {circuit_history[-1][1]:.3f}")

# ---------------------------------------------------------------------------
# 6. FAITHFULNESS TEST
# ---------------------------------------------------------------------------
# Faithfulness: does the circuit behave like the full model?
# We compare circuit accuracy against full model and random subset.

logits_circuit = model.forward(tokens,
                               ablate_heads=set(range(N_LAYERS)) - active_heads,
                               ablate_mlps=set(range(N_LAYERS)) - active_mlps)
acc_circuit = float(np.mean(np.argmax(logits_circuit, axis=-1) == targets))

# Random subset of same size
rng = np.random.RandomState(137)
n_components = N_LAYERS * N_HEADS + N_LAYERS
n_circuit = len(active_heads) + len(active_mlps)
n_random_ablate = n_components - n_circuit
all_heads = [(l, h) for l in range(N_LAYERS) for h in range(N_HEADS)]
all_mlps = list(range(N_LAYERS))
all_components = [('head', h) for h in all_heads] + [('mlp', m) for m in all_mlps]
random_subset = rng.choice(len(all_components), size=n_circuit, replace=False)
random_active = set(random_subset)
random_ablate_heads = set()
random_ablate_mlps = set()
for idx in range(len(all_components)):
    if idx not in random_active:
        typ, val = all_components[idx]
        if typ == 'head':
            random_ablate_heads.add(val)
        else:
            random_ablate_mlps.add(val)

logits_random = model.forward(tokens, ablate_heads=random_ablate_heads, ablate_mlps=random_ablate_mlps)
acc_random = float(np.mean(np.argmax(logits_random, axis=-1) == targets))

print("\n--- Faithfulness test ---")
print(f"Full model accuracy:     {acc_full:.3f}")
print(f"Circuit accuracy:        {acc_circuit:.3f}  (drop {acc_full - acc_circuit:.3f})")
print(f"Random subset accuracy:  {acc_random:.3f}  (drop {acc_full - acc_random:.3f})")

faithful = (acc_full - acc_circuit) <= THRESHOLD
print(f"Circuit is faithful?     {faithful}")

# ---------------------------------------------------------------------------
# 7. COMPLETENESS TEST
# ---------------------------------------------------------------------------
# Completeness: is every component in the circuit necessary?
# Ablate each component in the circuit individually. If any ablation
# causes a small drop, the component might be unnecessary (redundancy or bloat).

print("\n--- Completeness test (ablating each circuit component) ---")
print(f"{'Component':<20}  {'Accuracy':>10}  {'Drop':>10}  {'Necessary?':>12}")
print("-" * 60)

all_necessary = True
for comp in sorted(active_heads):
    logits = model.forward(tokens, ablate_heads={(comp[0], comp[1])})
    acc = float(np.mean(np.argmax(logits, axis=-1) == targets))
    drop = acc_full - acc
    necessary = drop > 0.005  # threshold for necessity
    if not necessary:
        all_necessary = False
    print(f"L{comp[0]}H{comp[1]:<13}  {acc:>10.3f}  {drop:>10.3f}  {'YES' if necessary else 'NO':>12}")

for comp in sorted(active_mlps):
    logits = model.forward(tokens, ablate_mlps={comp})
    acc = float(np.mean(np.argmax(logits, axis=-1) == targets))
    drop = acc_full - acc
    necessary = drop > 0.005
    if not necessary:
        all_necessary = False
    print(f"L{comp} MLP{'':<9}  {acc:>10.3f}  {drop:>10.3f}  {'YES' if necessary else 'NO':>12}")

print(f"\nCircuit is complete (all components necessary)? {all_necessary}")

# ---------------------------------------------------------------------------
# 8. VISUALIZATIONS
# ---------------------------------------------------------------------------
os.makedirs("src/phase137", exist_ok=True)

# Plot 1: Node importance bar chart
fig, ax = plt.subplots(figsize=(12, 5))
labels = [f"L{l}H{h}" for (l, h), _, _ in head_importance] + [f"L{l} MLP" for l, _, _ in mlp_importance]
drops = [d for _, _, d in head_importance] + [d for _, _, d in mlp_importance]
colors = ['C0'] * len(head_importance) + ['C1'] * len(mlp_importance)
ax.bar(range(len(labels)), drops, color=colors, alpha=0.8)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
ax.set_ylabel('Accuracy drop when ablated')
ax.set_title('Component Importance: Ablating One Component at a Time')
ax.axhline(0, color='black', linewidth=0.5)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('src/phase137/node_importance.png', dpi=150)
plt.close()
print("\nSaved: src/phase137/node_importance.png")

# Plot 2: Faithfulness curve (accuracy vs circuit size)
if circuit_history:
    sizes, accs = zip(*circuit_history)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sizes, accs, marker='o', label='Greedy pruning')
    ax.axhline(acc_full, color='C1', linestyle='--', label='Full model')
    ax.axhline(min_acc, color='C2', linestyle='--', label='Min acceptable')
    ax.set_xlabel('Circuit size (number of components)')
    ax.set_ylabel('Accuracy')
    ax.set_title('Faithfulness Curve: Accuracy vs Circuit Size')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('src/phase137/faithfulness_curve.png', dpi=150)
    plt.close()
    print("Saved: src/phase137/faithfulness_curve.png")

# Plot 3: Circuit graph visualization
fig, ax = plt.subplots(figsize=(8, 6))
# Draw layers as columns, heads as rows
for layer in range(N_LAYERS):
    ax.axvline(layer, color='gray', alpha=0.2)
    for h in range(N_HEADS):
        if (layer, h) in active_heads:
            color = 'C0'
            alpha = 1.0
        else:
            color = 'lightgray'
            alpha = 0.3
        ax.scatter(layer, h, s=200, c=color, alpha=alpha, edgecolors='black', linewidths=0.5)
    # MLP
    if layer in active_mlps:
        color = 'C1'
        alpha = 1.0
    else:
        color = 'lightgray'
        alpha = 0.3
    ax.scatter(layer, N_HEADS + 0.5, s=300, c=color, alpha=alpha, marker='s', edgecolors='black', linewidths=0.5)

ax.set_xlabel('Layer')
ax.set_ylabel('Component')
ax.set_yticks(list(range(N_HEADS)) + [N_HEADS + 0.5])
ax.set_yticklabels([f'Head {h}' for h in range(N_HEADS)] + ['MLP'])
ax.set_xticks(range(N_LAYERS))
ax.set_title('Discovered Circuit: Active Components (Blue=Head, Orange=MLP)')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('src/phase137/circuit_graph.png', dpi=150)
plt.close()
print("Saved: src/phase137/circuit_graph.png")

# ---------------------------------------------------------------------------
# 9. SUMMARY
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print(f"Full model:           {N_LAYERS*N_HEADS + N_LAYERS} components, accuracy {acc_full:.3f}")
print(f"Circuit:              {len(active_heads)+len(active_mlps)} components, accuracy {acc_circuit:.3f}")
print(f"Random same-size:     {n_circuit} components, accuracy {acc_random:.3f}")
print(f"Faithful?             {faithful}")
print(f"Complete?             {all_necessary}")
print("=" * 70)

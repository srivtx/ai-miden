#!/usr/bin/env python3
"""
Phase 121: Pretraining Concepts — NumPy Demo
==============================================
This script simulates training a tiny language model from scratch on a
synthetic corpus. We demonstrate:

  1. Weight initialization (Xavier for hidden layers, small std for embeddings)
  2. Forward pass with causal next-token prediction
  3. Cross-entropy loss computation
  4. Backward pass with manual backpropagation
  5. Tracking loss curves, gradient norms, and weight distributions

Key insight: Even a tiny model with a few thousand parameters, trained on
a synthetic corpus, exhibits the signature patterns of real pretraining:
  - Loss decays exponentially in early steps
  - Gradient norms spike early then stabilize
  - Weight distributions shift from Gaussian init to task-specific structure
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(121)

# =============================================================================
# SECTION 1: CONFIGURATION — Tiny model, tiny corpus
# =============================================================================
# We deliberately keep everything small so the NumPy simulation runs in
# seconds while still exhibiting real training dynamics.

VOCAB_SIZE = 30          # 30 unique tokens
EMBED_DIM = 16           # embedding dimension
HIDDEN_DIM = 32          # hidden layer size
CONTEXT_LEN = 4          # number of previous tokens to use for prediction
N_SAMPLES = 2000         # synthetic training sequences
N_STEPS = 500            # training steps
BATCH_SIZE = 32          # sequences per batch
LR = 0.05                # learning rate

print("="*60)
print("Phase 121: Pretraining Concepts (NumPy Simulation)")
print("="*60)
print(f"Vocab size:     {VOCAB_SIZE}")
print(f"Embed dim:      {EMBED_DIM}")
print(f"Hidden dim:     {HIDDEN_DIM}")
print(f"Context length: {CONTEXT_LEN}")
print(f"Training steps: {N_STEPS}")
print(f"Batch size:     {BATCH_SIZE}")

# =============================================================================
# SECTION 2: SYNTHETIC CORPUS GENERATION
# =============================================================================
# We generate sequences from a Markov-like process so the data has
# predictable structure the model can learn. Some tokens strongly follow
# others, creating learnable patterns.

def generate_corpus(n_samples, vocab_size, context_len):
    """Generate synthetic token sequences with predictable transitions."""
    # Define transition rules: token i is likely followed by (i+1) % vocab_size
    # with some noise. This creates learnable sequential structure.
    sequences = []
    next_tokens = []
    for _ in range(n_samples):
        seq = [np.random.randint(0, vocab_size)]
        for _ in range(context_len):
            # 70% chance to follow the deterministic pattern, 30% random
            if np.random.rand() < 0.7:
                next_tok = (seq[-1] + 1) % vocab_size
            else:
                next_tok = np.random.randint(0, vocab_size)
            seq.append(next_tok)
        sequences.append(seq[:-1])   # context tokens
        next_tokens.append(seq[-1])  # target token
    return np.array(sequences), np.array(next_tokens)

X_train, y_train = generate_corpus(N_SAMPLES, VOCAB_SIZE, CONTEXT_LEN)
print(f"\nCorpus: {N_SAMPLES} sequences generated")
print(f"Example sequence: {X_train[0]} -> target: {y_train[0]}")

# =============================================================================
# SECTION 3: MODEL INITIALIZATION
# =============================================================================
# Xavier (Glorot) initialization for the hidden layer ensures that the
# variance of activations stays roughly constant across the layer.
# We use a smaller std for embeddings because extreme initial embeddings
# can produce extreme logits and unstable early loss.

# Embedding matrix: each token gets a dense vector
W_embed = np.random.randn(VOCAB_SIZE, EMBED_DIM) * 0.1  # small std

# Hidden layer: Xavier init using fan_in = CONTEXT_LEN * EMBED_DIM
fan_in = CONTEXT_LEN * EMBED_DIM
xavier_std = np.sqrt(2.0 / fan_in)
W_hidden = np.random.randn(fan_in, HIDDEN_DIM) * xavier_std
b_hidden = np.zeros(HIDDEN_DIM)

# Output layer: maps hidden activations to vocabulary logits
fan_in_out = HIDDEN_DIM
xavier_std_out = np.sqrt(2.0 / fan_in_out)
W_out = np.random.randn(HIDDEN_DIM, VOCAB_SIZE) * xavier_std_out
b_out = np.zeros(VOCAB_SIZE)

print("\n--- Initialization ---")
print(f"Embedding std:  {np.std(W_embed):.4f} (target: small)")
print(f"Hidden std:     {np.std(W_hidden):.4f} (Xavier: {xavier_std:.4f})")
print(f"Output std:     {np.std(W_out):.4f} (Xavier: {xavier_std_out:.4f})")

# =============================================================================
# SECTION 4: TRAINING LOOP
# =============================================================================
# We train with vanilla SGD and manual backprop. Each step samples a batch,
# runs forward propagation, computes cross-entropy loss, then backpropagates
# gradients through embedding -> hidden -> output.

loss_history = []
grad_norm_history = []
weight_std_history = {"embed": [], "hidden": [], "out": []}

for step in range(N_STEPS):
    # Sample a random batch
    idx = np.random.choice(N_SAMPLES, BATCH_SIZE, replace=False)
    X_batch = X_train[idx]    # (BATCH_SIZE, CONTEXT_LEN)
    y_batch = y_train[idx]    # (BATCH_SIZE,)

    # -------------------------------------------------------------------------
    # FORWARD PASS
    # -------------------------------------------------------------------------
    # Embedding lookup: (batch, context_len) -> (batch, context_len, embed_dim)
    embeds = W_embed[X_batch]                 # (B, C, E)
    embeds_flat = embeds.reshape(BATCH_SIZE, -1)  # (B, C*E)

    # Hidden layer with tanh activation
    hidden_pre = embeds_flat @ W_hidden + b_hidden  # (B, H)
    hidden = np.tanh(hidden_pre)                     # (B, H)

    # Output logits
    logits = hidden @ W_out + b_out                  # (B, V)

    # Softmax probabilities
    logits_shifted = logits - np.max(logits, axis=1, keepdims=True)
    exp_scores = np.exp(logits_shifted)
    probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)  # (B, V)

    # Cross-entropy loss
    correct_logprobs = -np.log(probs[np.arange(BATCH_SIZE), y_batch] + 1e-12)
    loss = np.mean(correct_logprobs)
    loss_history.append(loss)

    # -------------------------------------------------------------------------
    # BACKWARD PASS
    # -------------------------------------------------------------------------
    # Gradient of loss w.r.t. logits
    dlogits = probs.copy()
    dlogits[np.arange(BATCH_SIZE), y_batch] -= 1
    dlogits /= BATCH_SIZE  # average over batch

    # Output layer gradients
    dW_out = hidden.T @ dlogits          # (H, V)
    db_out = np.sum(dlogits, axis=0)     # (V,)
    dhidden = dlogits @ W_out.T          # (B, H)

    # Tanh backward: dtanh(x) = (1 - tanh(x)^2) * grad
    dhidden_pre = dhidden * (1 - hidden ** 2)  # (B, H)

    # Hidden layer gradients
    dW_hidden = embeds_flat.T @ dhidden_pre     # (C*E, H)
    db_hidden = np.sum(dhidden_pre, axis=0)     # (H,)
    dembeds_flat = dhidden_pre @ W_hidden.T     # (B, C*E)
    dembeds = dembeds_flat.reshape(BATCH_SIZE, CONTEXT_LEN, EMBED_DIM)

    # Embedding gradients (accumulate into vocabulary rows)
    dW_embed = np.zeros_like(W_embed)
    for b in range(BATCH_SIZE):
        for c in range(CONTEXT_LEN):
            tok_id = X_batch[b, c]
            dW_embed[tok_id] += dembeds[b, c]

    # -------------------------------------------------------------------------
    # PARAMETER UPDATE
    # -------------------------------------------------------------------------
    W_embed -= LR * dW_embed
    W_hidden -= LR * dW_hidden
    b_hidden -= LR * db_hidden
    W_out -= LR * dW_out
    b_out -= LR * db_out

    # -------------------------------------------------------------------------
    # METRICS
    # -------------------------------------------------------------------------
    total_grad_norm = (
        np.linalg.norm(dW_embed) +
        np.linalg.norm(dW_hidden) +
        np.linalg.norm(dW_out)
    )
    grad_norm_history.append(total_grad_norm)

    weight_std_history["embed"].append(np.std(W_embed))
    weight_std_history["hidden"].append(np.std(W_hidden))
    weight_std_history["out"].append(np.std(W_out))

    if step % 100 == 0:
        acc = np.mean(np.argmax(logits, axis=1) == y_batch)
        print(f"Step {step:4d}: loss = {loss:.4f}, batch_acc = {acc:.3f}, grad_norm = {total_grad_norm:.4f}")

# =============================================================================
# SECTION 5: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Loss curve
ax = axes[0, 0]
ax.plot(loss_history, color='#2c3e50', linewidth=1.5)
ax.set_xlabel('Training Step')
ax.set_ylabel('Cross-Entropy Loss')
ax.set_title('Pretraining Loss Curve')
ax.grid(True, alpha=0.3)

# Plot 2: Gradient norms
ax = axes[0, 1]
ax.plot(grad_norm_history, color='#e74c3c', linewidth=1.5)
ax.set_xlabel('Training Step')
ax.set_ylabel('Total Gradient Norm')
ax.set_title('Gradient Norms Over Training')
ax.grid(True, alpha=0.3)

# Plot 3: Weight distribution shift
ax = axes[1, 0]
ax.plot(weight_std_history["embed"], label='Embedding', color='#3498db', linewidth=1.5)
ax.plot(weight_std_history["hidden"], label='Hidden', color='#27ae60', linewidth=1.5)
ax.plot(weight_std_history["out"], label='Output', color='#9b59b6', linewidth=1.5)
ax.set_xlabel('Training Step')
ax.set_ylabel('Weight Standard Deviation')
ax.set_title('Weight Distribution Evolution')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Initial vs final weight histograms
ax = axes[1, 1]
# Re-initialize to compare
W_embed_init = np.random.randn(VOCAB_SIZE, EMBED_DIM) * 0.1
ax.hist(W_embed_init.flatten(), bins=30, alpha=0.5, label='Initial', color='#95a5a6', density=True)
ax.hist(W_embed.flatten(), bins=30, alpha=0.5, label='Final', color='#e67e22', density=True)
ax.set_xlabel('Weight Value')
ax.set_ylabel('Density')
ax.set_title('Embedding Weights: Initial vs Final')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase121', exist_ok=True)
plt.savefig('src/phase121/pretraining_concepts.png', dpi=150)
print("\nSaved plot to src/phase121/pretraining_concepts.png")

# =============================================================================
# SECTION 6: SAMPLE GENERATION (simple greedy decoding)
# =============================================================================
print("\n" + "="*60)
print("SAMPLE GENERATIONS (greedy decoding)")
print("="*60)

for start_tok in [0, 5, 10]:
    context = [start_tok] * CONTEXT_LEN
    generated = list(context)
    for _ in range(10):
        emb = W_embed[np.array(context)].reshape(1, -1)
        h = np.tanh(emb @ W_hidden + b_hidden)
        logit = h @ W_out + b_out
        next_tok = int(np.argmax(logit, axis=1)[0])
        generated.append(next_tok)
        context = context[1:] + [next_tok]
    print(f"Start {start_tok}: {generated}")

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Initial loss:     {loss_history[0]:.4f}")
print(f"Final loss:       {loss_history[-1]:.4f}")
print(f"Initial grad norm:{grad_norm_history[0]:.4f}")
print(f"Final grad norm:  {grad_norm_history[-1]:.4f}")
print(f"Embedding std:    {np.std(W_embed):.4f} (init target ~0.1)")
print(f"Hidden std:       {np.std(W_hidden):.4f} (init ~{xavier_std:.4f})")
print("\nKey lessons:")
print("  1. Random initialization is critical — bad scaling kills training")
print("  2. Loss decays exponentially in early steps, then plateaus")
print("  3. Gradient norms are largest early and stabilize as weights converge")
print("  4. Weight distributions shift from Gaussian init to task-specific structure")
print("  5. Even tiny models learn sequential patterns when initialized well")

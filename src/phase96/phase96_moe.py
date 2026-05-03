import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

np.random.seed(42)

# --- Tiny MoE Layer Simulation ---
# We simulate a single MoE layer with:
# - 4 experts (each is a small linear layer)
# - A gating network that routes tokens to top-2 experts
# - Load balancing loss calculation

d_model = 8
num_experts = 4
top_k = 2
num_tokens = 8

# Token embeddings
x = np.random.randn(num_tokens, d_model)

# Expert weights: each expert is a linear map d_model -> d_model
experts = [np.random.randn(d_model, d_model) * 0.1 for _ in range(num_experts)]

# Gating network: maps token to logits over experts
W_gate = np.random.randn(d_model, num_experts) * 0.1
b_gate = np.zeros(num_experts)

# Forward pass through gate
logits = x @ W_gate + b_gate  # (num_tokens, num_experts)


def softmax(z):
    e = np.exp(z - np.max(z, axis=-1, keepdims=True))
    return e / np.sum(e, axis=-1, keepdims=True)


probs = softmax(logits)

# Top-k routing
top_k_indices = np.argsort(-probs, axis=1)[:, :top_k]
top_k_probs = np.take_along_axis(probs, top_k_indices, axis=1)

# Normalize top-k probs so they sum to 1
top_k_probs = top_k_probs / (top_k_probs.sum(axis=1, keepdims=True) + 1e-9)

# Compute expert outputs and weighted sum
output = np.zeros((num_tokens, d_model))
for t in range(num_tokens):
    token_out = np.zeros(d_model)
    for rank, e_idx in enumerate(top_k_indices[t]):
        expert_out = x[t] @ experts[e_idx]
        token_out += top_k_probs[t, rank] * expert_out
    output[t] = token_out

print("Input shape:", x.shape)
print("MoE output shape:", output.shape)
print("Top-k indices per token:\n", top_k_indices)

# --- Load Balancing Loss ---
# L = num_experts * sum_e (f_e * P_e)
# where f_e = fraction of tokens routed to expert e (by top-1)
# and P_e = mean routing probability to expert e across all tokens

top1_indices = np.argmax(probs, axis=1)

f = np.zeros(num_experts)
for e in range(num_experts):
    f[e] = np.mean(top1_indices == e)

P = probs.mean(axis=0)

load_balance_loss = num_experts * np.sum(f * P)
print("\nLoad Balancing Loss:", load_balance_loss)

# --- Visualization: Expert usage ---
plt.figure(figsize=(8, 4))
plt.bar(range(num_experts), f, color='steelblue', edgecolor='black')
plt.xlabel('Expert Index')
plt.ylabel('Fraction of Top-1 Routing')
plt.title('Expert Usage Distribution (Phase 96 MoE)')
plt.xticks(range(num_experts))
plt.ylim(0, max(f.max() * 1.2, 0.1))
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'phase96_expert_usage.png')
plt.savefig(out_path)
print("Saved plot to", out_path)

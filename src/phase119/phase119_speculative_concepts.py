#!/usr/bin/env python3
"""
Phase 119: Advanced Speculative Decoding — NumPy Concept Demo
==============================================================
This script demonstrates advanced speculative decoding concepts using
pure NumPy simulations. We cover:

  1. Basic speculative decoding: independent draft model verification
  2. EAGLE principle: draft model conditioned on base model hidden states
  3. Medusa decoding: 4 heads predict future tokens t+1 through t+4
  4. Tree attention: verify multiple draft branches in parallel
  5. Expected tokens per forward pass comparison

Key insight: speculative decoding is about alignment. The closer the draft
distribution is to the target distribution, the higher the acceptance rate
and the greater the speedup. Tree attention further improves efficiency by
not wasting compute on rejected subtrees.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(119)

# =============================================================================
# SECTION 1: SETUP — Simulate target and draft model distributions
# =============================================================================
# We simulate a vocabulary of 50 tokens. The target model has a "true"
# distribution over the vocabulary. The draft model tries to guess it.
# We compare three draft strategies: independent, EAGLE-conditioned, and Medusa.

vocab_size = 50
n_positions = 20  # how many generation steps to simulate

# Target model: a softmax distribution that changes slightly each step
# We make it peaked (low entropy) so greedy decoding is easy,
# but not deterministic so speculative decoding has room to help.
def generate_target_probs(step, vocab_size):
    """Generate target model probability distribution at generation step."""
    # A shifting peaked distribution: the "correct" token moves slowly
    logits = np.random.randn(vocab_size) * 0.3
    peak = (step * 2) % vocab_size
    logits[peak] += 2.0
    logits[(peak + 1) % vocab_size] += 1.0
    logits[(peak - 1) % vocab_size] += 0.5
    # Normalize with temperature
    exp_scores = np.exp(logits - np.max(logits))
    probs = exp_scores / np.sum(exp_scores)
    return probs

# Draft model (independent): similar but noisier, less aligned
def generate_independent_draft_probs(target_probs):
    """Draft model guesses without seeing target hidden states."""
    noise = np.random.randn(vocab_size) * 0.4
    draft_logits = np.log(target_probs + 1e-10) + noise
    exp_scores = np.exp(draft_logits - np.max(draft_logits))
    return exp_scores / np.sum(exp_scores)

# EAGLE draft model: conditioned on target hidden state, much more aligned
def generate_eagle_draft_probs(target_probs):
    """Draft model sees target hidden state, so it tracks closely."""
    noise = np.random.randn(vocab_size) * 0.15
    draft_logits = np.log(target_probs + 1e-10) + noise
    exp_scores = np.exp(draft_logits - np.max(draft_logits))
    return exp_scores / np.sum(exp_scores)

# Medusa heads: predict future tokens from current hidden state
# Each head predicts token at offset k (head 0 = t+1, head 1 = t+2, etc.)
def generate_medusa_probs(target_probs_list):
    """
    Each head predicts a future token. Accuracy degrades with distance.
    target_probs_list[k] is the true distribution for token t+k+1.
    """
    medusa_probs = []
    for k, true_probs in enumerate(target_probs_list):
        # Degrading accuracy: more noise for farther predictions
        noise_scale = 0.2 + k * 0.15
        noise = np.random.randn(vocab_size) * noise_scale
        draft_logits = np.log(true_probs + 1e-10) + noise
        exp_scores = np.exp(draft_logits - np.max(draft_logits))
        medusa_probs.append(exp_scores / np.sum(exp_scores))
    return medusa_probs

print("="*70)
print("Phase 119: Advanced Speculative Decoding")
print("="*70)
print(f"Vocabulary size: {vocab_size}")
print(f"Simulation steps: {n_positions}")

# =============================================================================
# SECTION 2: BASIC SPECULATIVE DECODING SIMULATION
# =============================================================================
# Standard speculative decoding: draft model generates K tokens,
# target model verifies all K in one forward pass.
# Acceptance criterion: u ~ Uniform(0,1), accept if u < min(1, p_target/p_draft)

def speculative_decode_step(target_probs_fn, draft_probs_fn, K=4):
    """
    Simulate one speculative decoding step with draft length K.
    Returns: (number of accepted tokens, acceptance details)
    """
    accepted = 0
    # Draft generates K tokens auto-regressively
    draft_tokens = []
    draft_probs_seq = []
    for k in range(K):
        t_probs = target_probs_fn(k)  # true distribution at position k
        d_probs = draft_probs_fn(t_probs)
        token = np.random.choice(vocab_size, p=d_probs)
        draft_tokens.append(token)
        draft_probs_seq.append((t_probs, d_probs, token))

    # Target verifies: one forward pass computes ALL K distributions
    for k in range(K):
        t_probs, d_probs, token = draft_probs_seq[k]
        p_t = t_probs[token]
        p_d = d_probs[token]
        # Rejection sampling criterion
        accept_threshold = min(1.0, p_t / (p_d + 1e-10))
        u = np.random.rand()
        if u < accept_threshold:
            accepted += 1
        else:
            # Rejection: resample from adjusted distribution
            # (p_target - p_draft)_+ then normalize
            break
    return accepted

# Run simulation for basic speculative decoding
K = 4
basic_acceptances = []
for step in range(n_positions):
    def tp(k):
        return generate_target_probs(step + k, vocab_size)
    def dp(tp):
        return generate_independent_draft_probs(tp)
    acc = speculative_decode_step(tp, dp, K=K)
    basic_acceptances.append(acc)

basic_expected = np.mean(basic_acceptances)
print(f"\n--- Basic Speculative Decoding (K={K}) ---")
print(f"Average accepted tokens per step: {basic_expected:.2f}")
print(f"Effective tokens per forward pass: {1 + basic_expected:.2f}")

# =============================================================================
# SECTION 3: EAGLE-STYLE SPECULATIVE DECODING
# =============================================================================
# EAGLE draft model sees the target hidden state, so its predictions
# are much more aligned with the target distribution.

eagle_acceptances = []
for step in range(n_positions):
    def tp(k):
        return generate_target_probs(step + k, vocab_size)
    def dp(tp):
        return generate_eagle_draft_probs(tp)
    acc = speculative_decode_step(tp, dp, K=K)
    eagle_acceptances.append(acc)

eagle_expected = np.mean(eagle_acceptances)
print(f"\n--- EAGLE Speculative Decoding (K={K}) ---")
print(f"Average accepted tokens per step: {eagle_expected:.2f}")
print(f"Effective tokens per forward pass: {1 + eagle_expected:.2f}")
print(f"Improvement over basic: {(eagle_expected / basic_expected - 1)*100:.1f}%")

# =============================================================================
# SECTION 4: MEDUSA DECODING SIMULATION
# =============================================================================
# Medusa attaches 4 heads to the base model. Each head predicts a future
# token from the CURRENT hidden state. We verify all predictions in one
# forward pass. Because heads predict from h_t (not h_t+k), accuracy
# degrades with distance.

n_medusa_heads = 4
medusa_acceptances = []

for step in range(n_positions):
    # Generate true distributions for t+1 through t+4
    true_probs_list = [generate_target_probs(step + k + 1, vocab_size)
                       for k in range(n_medusa_heads)]
    # Medusa heads predict from current hidden state
    medusa_preds = generate_medusa_probs(true_probs_list)

    # Sample draft tokens from each head
    draft_tokens = [np.random.choice(vocab_size, p=medusa_preds[k])
                    for k in range(n_medusa_heads)]

    # Verify all in one forward pass
    accepted = 0
    for k in range(n_medusa_heads):
        t_probs = true_probs_list[k]
        d_probs = medusa_preds[k]
        token = draft_tokens[k]
        p_t = t_probs[token]
        p_d = d_probs[token]
        accept_threshold = min(1.0, p_t / (p_d + 1e-10))
        u = np.random.rand()
        if u < accept_threshold:
            accepted += 1
        else:
            break
    medusa_acceptances.append(accepted)

medusa_expected = np.mean(medusa_acceptances)
print(f"\n--- Medusa Decoding ({n_medusa_heads} heads) ---")
print(f"Average accepted tokens per step: {medusa_expected:.2f}")
print(f"Effective tokens per forward pass: {1 + medusa_expected:.2f}")
print(f"Head degradation: head 0 aligns best, head 3 aligns worst")

# =============================================================================
# SECTION 5: TREE ATTENTION VERIFICATION
# =============================================================================
# Instead of verifying a linear chain, we verify a tree of possibilities.
# Each branch is an independent draft hypothesis. We process all nodes
# in one forward pass with a tree-structured attention mask.
# For simulation, we model a tree with 1 root, 3 first-level branches,
# and each branch has 2 second-level options.

class TokenTree:
    """Represents a draft tree for verification."""
    def __init__(self, vocab_size):
        self.vocab_size = vocab_size
        self.nodes = []  # list of (parent_idx, depth, draft_probs)
        self.root_idx = 0
        self.add_node(-1, 0, None)  # root

    def add_node(self, parent_idx, depth, draft_probs):
        self.nodes.append({'parent': parent_idx, 'depth': depth,
                           'probs': draft_probs})
        return len(self.nodes) - 1

    def get_children(self, idx):
        return [i for i, n in enumerate(self.nodes) if n['parent'] == idx]

# Build a sample tree for one step
tree_accepts_per_step = []
for step in range(n_positions):
    tree = TokenTree(vocab_size)
    # Root already added
    # Add 3 first-level branches (different draft hypotheses for t+1)
    first_level_probs = [generate_target_probs(step + 1, vocab_size)
                         for _ in range(3)]
    first_level_drafts = [generate_eagle_draft_probs(p) for p in first_level_probs]

    level1_indices = []
    for d_probs in first_level_drafts:
        idx = tree.add_node(0, 1, d_probs)
        level1_indices.append(idx)

    # Add 2 second-level children per first-level node (t+2 options)
    for parent_idx in level1_indices:
        for _ in range(2):
            t_probs = generate_target_probs(step + 2, vocab_size)
            d_probs = generate_eagle_draft_probs(t_probs)
            tree.add_node(parent_idx, 2, d_probs)

    # Simulate tree verification in one forward pass
    # In reality, the target model computes probabilities for ALL tree nodes
    # using a tree attention mask. Here we simulate the acceptance process.
    accepted_branches = []
    for l1_idx in level1_indices:
        # Check if first-level token is accepted
        node = tree.nodes[l1_idx]
        token = np.random.choice(vocab_size, p=node['probs'])
        true_probs = first_level_probs[level1_indices.index(l1_idx)]
        p_t = true_probs[token]
        p_d = node['probs'][token]
        accept_threshold = min(1.0, p_t / (p_d + 1e-10))
        if np.random.rand() < accept_threshold:
            # First level accepted, check children
            children = tree.get_children(l1_idx)
            best_child_len = 0
            for child_idx in children:
                c_node = tree.nodes[child_idx]
                c_token = np.random.choice(vocab_size, p=c_node['probs'])
                c_true = generate_target_probs(step + 2, vocab_size)
                cp_t = c_true[c_token]
                cp_d = c_node['probs'][c_token]
                c_accept = min(1.0, cp_t / (cp_d + 1e-10))
                if np.random.rand() < c_accept:
                    best_child_len = max(best_child_len, 1)
            accepted_branches.append(1 + best_child_len)
        else:
            accepted_branches.append(0)

    # Tree verification keeps the longest valid branch
    tree_accepts_per_step.append(max(accepted_branches) if accepted_branches else 0)

tree_expected = np.mean(tree_accepts_per_step)
print(f"\n--- Tree Attention Verification ---")
print(f"Tree structure: 1 root, 3 branches, 2 children each")
print(f"Average accepted tokens per step: {tree_expected:.2f}")
print(f"Effective tokens per forward pass: {1 + tree_expected:.2f}")
print(f"Why better? Rejected first-level nodes do not block other branches.")

# =============================================================================
# SECTION 6: COMPARISON OF ALL METHODS
# =============================================================================
# We compute expected tokens per forward pass for all strategies.
# Greedy = 1.0. Each speculative method adds accepted drafts.

methods = {
    'Greedy': 1.0,
    'Basic Speculative': 1.0 + basic_expected,
    'EAGLE': 1.0 + eagle_expected,
    'Medusa': 1.0 + medusa_expected,
    'Tree Attention': 1.0 + tree_expected,
}

print("\n" + "="*70)
print("EXPECTED TOKENS PER FORWARD PASS")
print("="*70)
for name, val in methods.items():
    print(f"  {name:20s}: {val:.2f}x")

# =============================================================================
# SECTION 7: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Acceptance distribution histogram
ax = axes[0, 0]
bins = np.arange(-0.5, K + 1.5, 1)
ax.hist(basic_acceptances, bins=bins, alpha=0.6, label='Basic', color='#e74c3c', edgecolor='black')
ax.hist(eagle_acceptances, bins=bins, alpha=0.6, label='EAGLE', color='#27ae60', edgecolor='black')
ax.hist(medusa_acceptances, bins=bins, alpha=0.6, label='Medusa', color='#2980b9', edgecolor='black')
ax.set_xlabel('Accepted Draft Tokens')
ax.set_ylabel('Frequency')
ax.set_title('Acceptance Distribution Across Methods')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Speedup comparison bar chart
ax = axes[0, 1]
names = list(methods.keys())
values = list(methods.values())
colors = ['#95a5a6', '#e74c3c', '#27ae60', '#2980b9', '#8e44ad']
bars = ax.bar(names, values, color=colors, edgecolor='black', alpha=0.8)
ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1, label='Greedy baseline')
ax.set_ylabel('Tokens per Forward Pass')
ax.set_title('Speedup Factor: Speculative Methods vs. Greedy')
ax.set_xticklabels(names, rotation=15, ha='right')
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{val:.2f}x', ha='center', va='bottom', fontsize=9)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Token tree visualization (one example step)
ax = axes[1, 0]
# Draw a simple tree diagram for step 0
# Root at top, branches spread below
ax.set_xlim(-1, 5)
ax.set_ylim(-1, 4)
ax.axis('off')
ax.set_title('Example Token Tree for Verification')

# Root
ax.plot(2, 3, 'o', markersize=20, color='#2c3e50', zorder=3)
ax.text(2, 3, 'ROOT', ha='center', va='center', color='white', fontsize=8, fontweight='bold')

# Level 1: 3 branches
l1_x = [0.5, 2.0, 3.5]
l1_colors = ['#27ae60', '#e74c3c', '#f39c12']
l1_labels = ['A (acc)', 'B (rej)', 'C (acc)']
for x, c, lab in zip(l1_x, l1_colors, l1_labels):
    ax.plot([2, x], [3, 1.5], '-', color='#7f8c8d', linewidth=2, zorder=1)
    ax.plot(x, 1.5, 'o', markersize=18, color=c, zorder=3)
    ax.text(x, 1.5, lab, ha='center', va='center', color='white', fontsize=7, fontweight='bold')

# Level 2: children of accepted branches (A and C)
l2_children = {
    0.5: [('A1', '#27ae60'), ('A2', '#e74c3c')],
    3.5: [('C1', '#27ae60'), ('C2', '#27ae60')],
}
for parent_x, children in l2_children.items():
    offsets = [-0.6, 0.6]
    for (lab, c), off in zip(children, offsets):
        child_x = parent_x + off
        ax.plot([parent_x, child_x], [1.5, 0], '-', color='#7f8c8d', linewidth=2, zorder=1)
        ax.plot(child_x, 0, 'o', markersize=14, color=c, zorder=3)
        ax.text(child_x, 0, lab, ha='center', va='center', color='white', fontsize=6, fontweight='bold')

ax.text(2, -0.8, 'Green = accepted, Red = rejected, Orange = rejected parent',
        ha='center', fontsize=9, style='italic')

# Plot 4: Medusa head degradation
ax = axes[1, 1]
# Compute per-head acceptance rate across all steps
head_accs = []
for head_k in range(n_medusa_heads):
    acc_count = 0
    total = 0
    for step in range(n_positions):
        true_probs_list = [generate_target_probs(step + kk + 1, vocab_size)
                           for kk in range(n_medusa_heads)]
        medusa_preds = generate_medusa_probs(true_probs_list)
        token = np.random.choice(vocab_size, p=medusa_preds[head_k])
        p_t = true_probs_list[head_k][token]
        p_d = medusa_preds[head_k][token]
        if np.random.rand() < min(1.0, p_t / (p_d + 1e-10)):
            acc_count += 1
        total += 1
    head_accs.append(acc_count / total)

ax.bar(range(n_medusa_heads), head_accs, color=['#27ae60', '#2ecc71', '#f39c12', '#e74c3c'],
       edgecolor='black', alpha=0.8)
ax.set_xlabel('Medusa Head (distance into future)')
ax.set_ylabel('Acceptance Rate')
ax.set_title('Medusa Head Accuracy Degradation')
ax.set_xticks(range(n_medusa_heads))
ax.set_xticklabels([f't+{k+1}' for k in range(n_medusa_heads)])
ax.set_ylim(0, 1.0)
for i, v in enumerate(head_accs):
    ax.text(i, v + 0.03, f'{v:.2f}', ha='center', fontsize=9)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase119', exist_ok=True)
plt.savefig('src/phase119/speculative_concepts.png', dpi=150)
print("\nSaved plot to src/phase119/speculative_concepts.png")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Greedy decoding baseline:      1.00 tokens per forward pass")
print(f"Basic speculative (K={K}):       {methods['Basic Speculative']:.2f} tokens per forward pass")
print(f"EAGLE speculative (K={K}):       {methods['EAGLE']:.2f} tokens per forward pass")
print(f"Medusa ({n_medusa_heads} heads):              {methods['Medusa']:.2f} tokens per forward pass")
print(f"Tree attention:                {methods['Tree Attention']:.2f} tokens per forward pass")
print("\nKey lessons:")
print("  1. Draft-target alignment determines acceptance rate (EAGLE principle)")
print("  2. In-model heads eliminate separate draft model overhead (Medusa)")
print("  3. Tree verification wastes less compute on rejected subtrees")
print("  4. Medusa heads degrade with distance; 3-4 heads is the sweet spot")
print("  5. Real speedup depends on draft generation cost, not just acceptance")
print("="*70)

"""
Phase 36: Speculative Decoding

This script demonstrates speculative decoding using only NumPy.

We simulate:
1. A small, fast "draft model" (n-gram based)
2. A larger, more accurate "target model"
3. The speculative decoding algorithm: draft K tokens, verify in one pass
4. Acceptance sampling that preserves the exact target distribution
5. Speedup comparison vs. pure autoregressive generation

Why NumPy? So every acceptance/rejection decision is visible.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# 1. SETUP: SMALL VOCABULARY AND MODELS
# ============================================================================
# We use a vocabulary of 5 tokens and define two probability distributions:
# - Target model: more accurate, "slower"
# - Draft model: less accurate, "faster"
#
# Both models are just lookup tables: P(next_token | current_token)
# This lets us focus on the speculative decoding algorithm itself.
# ============================================================================

np.random.seed(42)
vocab_size = 5
K = 4  # number of draft tokens to generate per speculative step

# Target model: more concentrated (higher confidence on correct tokens)
target_probs = np.array([
    [0.50, 0.20, 0.15, 0.10, 0.05],  # from token 0
    [0.10, 0.55, 0.15, 0.10, 0.10],  # from token 1
    [0.10, 0.10, 0.50, 0.20, 0.10],  # from token 2
    [0.15, 0.15, 0.10, 0.45, 0.15],  # from token 3
    [0.05, 0.10, 0.15, 0.20, 0.50],  # from token 4
])

# Draft model: noisier version of target
draft_probs = 0.6 * target_probs + 0.4 * (np.ones((vocab_size, vocab_size)) / vocab_size)
# Renormalize rows
draft_probs = draft_probs / draft_probs.sum(axis=1, keepdims=True)

print("=" * 70)
print("PHASE 36: SPECULATIVE DECODING")
print("=" * 70)
print(f"Vocabulary size: {vocab_size}")
print(f"Draft tokens per step (K): {K}")
print(f"Target model: accurate but 'slow'")
print(f"Draft model:  noisy but 'fast'")
print()

# ============================================================================
# 2. SAMPLING FUNCTIONS
# ============================================================================

def sample_token(probs):
    """Sample from a categorical distribution."""
    return np.random.choice(len(probs), p=probs)

def autoregressive_generate(model_probs, start_token, length):
    """Standard token-by-token generation."""
    tokens = [start_token]
    for _ in range(length - 1):
        next_token = sample_token(model_probs[tokens[-1]])
        tokens.append(next_token)
    return tokens

def speculative_generate(target_probs, draft_probs, start_token, length, K):
    """
    Speculative decoding: draft K tokens, verify in one target pass.
    Returns (tokens, num_target_passes, acceptance_log)
    """
    tokens = [start_token]
    num_target_passes = 0
    acceptance_log = []  # list of (position, draft_token, accepted, reason)

    while len(tokens) < length:
        current = tokens[-1]

        # ---- Step 1: Draft model generates K candidates ----
        draft_tokens = []
        draft_state = current
        for _ in range(K):
            t = sample_token(draft_probs[draft_state])
            draft_tokens.append(t)
            draft_state = t

        # ---- Step 2: Target model verifies all K candidates ----
        # In reality, the target runs ONE forward pass with the prefix + K tokens
        # Here we simulate by looking up probabilities sequentially
        num_target_passes += 1
        accepted_count = 0

        for i, draft_t in enumerate(draft_tokens):
            if len(tokens) >= length:
                break

            # Target's probability for this token at this position
            target_p = target_probs[tokens[-1]][draft_t]
            draft_p = draft_probs[tokens[-1]][draft_t]

            # Acceptance criterion
            p_accept = min(1.0, target_p / draft_p)

            if np.random.random() < p_accept:
                # Accept!
                tokens.append(draft_t)
                accepted_count += 1
                acceptance_log.append((len(tokens)-1, draft_t, True, f"p_accept={p_accept:.2f}"))
            else:
                # Reject! Sample from residual distribution
                residual = np.maximum(0, target_probs[tokens[-1]] - draft_probs[tokens[-1]])
                if residual.sum() > 0:
                    residual = residual / residual.sum()
                    new_token = sample_token(residual)
                else:
                    new_token = sample_token(target_probs[tokens[-1]])
                tokens.append(new_token)
                acceptance_log.append((len(tokens)-1, draft_t, False, f"rejected, resampled to {new_token}"))
                break  # Stop verifying, restart from here

        if accepted_count == K:
            # All K accepted! We generated K+1 tokens (including the verification
            # of the last draft token) in one target pass. Actually, in standard
            # speculative decoding, after accepting all K draft tokens, the target
            # generates one additional token. For simplicity, we just continue.
            pass

    return tokens, num_target_passes, acceptance_log

# ============================================================================
# 3. GENERATE SEQUENCES AND COMPARE
# ============================================================================

seq_length = 50
n_trials = 100

print("Running trials...")

target_only_tokens = []
speculative_tokens = []
target_passes_auto = []
target_passes_spec = []

for trial in range(n_trials):
    start = np.random.randint(vocab_size)

    # Pure target (autoregressive)
    t_auto = autoregressive_generate(target_probs, start, seq_length)
    target_only_tokens.append(t_auto)
    target_passes_auto.append(seq_length - 1)  # one pass per token after start

    # Speculative
    t_spec, n_passes, _ = speculative_generate(target_probs, draft_probs, start, seq_length, K)
    speculative_tokens.append(t_spec)
    target_passes_spec.append(n_passes)

avg_passes_auto = np.mean(target_passes_auto)
avg_passes_spec = np.mean(target_passes_spec)
speedup = avg_passes_auto / avg_passes_spec

print(f"\nAverage target passes (autoregressive): {avg_passes_auto:.1f}")
print(f"Average target passes (speculative):    {avg_passes_spec:.1f}")
print(f"Effective speedup:                      {speedup:.2f}x")

# Verify distribution match (compare token frequencies)
auto_counts = np.bincount(np.array(target_only_tokens).flatten(), minlength=vocab_size)
spec_counts = np.bincount(np.array(speculative_tokens).flatten(), minlength=vocab_size)
auto_freq = auto_counts / auto_counts.sum()
spec_freq = spec_counts / spec_counts.sum()

print(f"\nToken distribution comparison (should match):")
for v in range(vocab_size):
    print(f"  Token {v}: auto={auto_freq[v]:.3f}, spec={spec_freq[v]:.3f}, diff={abs(auto_freq[v]-spec_freq[v]):.4f}")

# ============================================================================
# 4. DETAILED ACCEPTANCE LOG FOR ONE SEQUENCE
# ============================================================================

start = 0
tokens_spec, n_passes, log = speculative_generate(target_probs, draft_probs, start, 30, K)

print(f"\nDetailed log for one sequence (first 30 tokens):")
print(f"Target passes needed: {n_passes} (vs. 29 for autoregressive)")
print(f"Acceptance events:")
accepted = sum(1 for _, _, acc, _ in log if acc)
total_events = len(log)
print(f"  Accepted: {accepted}/{total_events} ({100*accepted/total_events:.1f}%)")
for pos, tok, acc, reason in log[:10]:
    status = "ACCEPT" if acc else "REJECT"
    print(f"  Pos {pos:2d}: draft={tok} -> {status} ({reason})")
if len(log) > 10:
    print(f"  ... and {len(log)-10} more")

# ============================================================================
# 5. VISUALIZATION
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# ---- Plot 1: Target Passes Comparison ----
ax = axes[0, 0]
categories = ['Autoregressive', 'Speculative\nDecoding']
passes = [avg_passes_auto, avg_passes_spec]
colors = ['steelblue', 'lightgreen']
bars = ax.bar(categories, passes, color=colors)
ax.set_ylabel('Average Target Passes')
ax.set_title(f'Target Passes: Auto vs. Speculative\n(Speedup: {speedup:.2f}x)')
for bar, p in zip(bars, passes):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{p:.1f}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# ---- Plot 2: Token Distribution Match ----
ax = axes[0, 1]
x = np.arange(vocab_size)
width = 0.35
ax.bar(x - width/2, auto_freq, width, label='Autoregressive', color='steelblue')
ax.bar(x + width/2, spec_freq, width, label='Speculative', color='lightgreen')
ax.set_xlabel('Token')
ax.set_ylabel('Frequency')
ax.set_title('Token Distribution: Exact Match Guaranteed')
ax.set_xticks(x)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# ---- Plot 3: Acceptance Rate Over Trials ----
ax = axes[1, 0]
acceptance_rates = []
for trial in range(n_trials):
    _, _, log_trial = speculative_generate(target_probs, draft_probs,
                                           np.random.randint(vocab_size), seq_length, K)
    if len(log_trial) > 0:
        rate = sum(1 for _, _, acc, _ in log_trial if acc) / len(log_trial)
        acceptance_rates.append(rate)
ax.hist(acceptance_rates, bins=15, color='purple', alpha=0.7, edgecolor='black')
ax.axvline(x=np.mean(acceptance_rates), color='red', linestyle='--', linewidth=2,
           label=f'Mean: {np.mean(acceptance_rates):.2f}')
ax.set_xlabel('Acceptance Rate')
ax.set_ylabel('Number of Trials')
ax.set_title('Acceptance Rate Distribution')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 4: Speedup vs. Draft Quality ----
ax = axes[1, 1]
# Vary how similar draft is to target
draft_qualities = np.linspace(0.3, 0.95, 10)
speedups = []
for quality in draft_qualities:
    dp = quality * target_probs + (1 - quality) * (np.ones((vocab_size, vocab_size)) / vocab_size)
    dp = dp / dp.sum(axis=1, keepdims=True)
    passes = []
    for _ in range(20):
        _, n_p, _ = speculative_generate(target_probs, dp, np.random.randint(vocab_size), 30, K)
        passes.append(n_p)
    speedups.append(29 / np.mean(passes))

ax.plot(draft_qualities, speedups, 'o-', color='green', linewidth=2)
ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='No speedup')
ax.set_xlabel('Draft-Target Similarity')
ax.set_ylabel('Speedup Factor')
ax.set_title('Speedup vs. Draft Quality')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('src/phase36/speculative_decoding.png', dpi=150, bbox_inches='tight')
print("\nSaved visualization: src/phase36/speculative_decoding.png")
plt.close()

# ============================================================================
# 6. SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Sequence length: {seq_length}")
print(f"Draft tokens per step: {K}")
print(f"Trials: {n_trials}")
print()
print(f"Autoregressive target passes: {avg_passes_auto:.1f}")
print(f"Speculative target passes:    {avg_passes_spec:.1f}")
print(f"Speedup:                      {speedup:.2f}x")
print()
print("Key observations:")
print("1. Speculative decoding reduces target model forward passes.")
print("2. The output distribution is EXACTLY the same as autoregressive.")
print("3. Acceptance rate depends on draft-target similarity.")
print("4. Speedup increases as the draft model better matches the target.")
print()
print("This demonstrates the core idea of speculative decoding:")
print("- Use a fast draft model to predict multiple tokens")
print("- Use a slow target model to verify them in one pass")
print("- Accept/reject with a statistical guarantee of identical distribution")
print("- Achieve 2-3x speedup with zero quality loss")
print("=" * 70)

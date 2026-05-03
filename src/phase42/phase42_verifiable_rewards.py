#!/usr/bin/env python3
"""
Phase 42: Reasoning with Verifiable Rewards — NumPy Concept Demo
=================================================================
This script demonstrates how a tiny model can be trained with
verifiable rewards using proper REINFORCE policy gradients.

Key insight: Instead of human preference labels, we use a simple
answer checker as the reward signal. The model learns to generate
intermediate reasoning steps because doing so improves accuracy.

Concepts demonstrated:
  - Verifiable rewards (correct answer = +1, wrong = 0)
  - GRPO baseline (group mean subtraction)
  - REINFORCE policy gradient (proper backprop)
  - Emergent reasoning (chain length tracking)

Architecture: Each problem is encoded as a learnable embedding vector.
The policy outputs a fixed-length sequence of tokens (one softmax per
position). This is a proper policy gradient model in pure NumPy.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)

# =============================================================================
# SECTION 1: VOCABULARY AND TOKENIZATION
# =============================================================================
# We define a tiny vocabulary of digits, operators, and special tokens.
# The model learns to map problem tokens to reasoning + answer tokens.

vocab = [
    '0','1','2','3','4','5','6','7','8','9',
    '+','-','*','/',
    '=', '(', ')', ' ',
    '<START>','<END>','<REASON>','<ANSWER>'
]
token_to_idx = {t:i for i,t in enumerate(vocab)}
idx_to_token = {i:t for t,i in token_to_idx.items()}
vocab_size = len(vocab)
embed_dim = 16
max_output_len = 12  # positions in the output sequence
num_problems_train = 50   # number of unique problems we train on

# =============================================================================
# SECTION 2: DATASET — SIMPLE ARITHMETIC PROBLEMS
# =============================================================================
# We enumerate all simple problems and map each to a unique ID.

def generate_all_problems():
    """Generate simple a op b problems with single-digit answers."""
    problems = []
    for a in range(1, 5):
        for b in range(1, 5):
            for op in ['+', '-']:
                if op == '+':
                    ans = a + b
                else:
                    ans = a - b
                # Only include problems with single-digit answers (including negative)
                if -9 <= ans <= 9:
                    text = f"{a}{op}{b}"
                    problems.append((text, ans))
    return problems

all_problems = generate_all_problems()
# Subsample for training
train_problems = all_problems[:num_problems_train]
problem_to_idx = {p[0]: i for i, p in enumerate(train_problems)}
num_train = len(train_problems)

def answer_to_tokens(ans: int):
    """Convert integer answer to token sequence with special tokens."""
    s = str(ans)
    tokens = [token_to_idx['<REASON>']] + [token_to_idx[c] for c in s] + [token_to_idx['<END>']]
    # Pad
    while len(tokens) < max_output_len:
        tokens.append(token_to_idx['<END>'])
    return tokens[:max_output_len]

def extract_answer_from_tokens(tokens):
    """Extract integer answer from token sequence."""
    # Look for digits after <REASON>
    found_reason = False
    digits = ''
    for t in tokens:
        if t == token_to_idx['<REASON>']:
            found_reason = True
            continue
        if found_reason:
            c = idx_to_token.get(t, '')
            if c.isdigit() or (c == '-' and not digits):
                digits += c
            elif digits:
                break
    if digits == '' or digits == '-':
        return None
    return int(digits)

# =============================================================================
# SECTION 3: MODEL — POSITION-WISE SOFTMAX POLICY
# =============================================================================
# For each problem, we learn an embedding vector.
# For each output position, we have a linear layer: embedding -> logits -> softmax.
# This is a proper policy: p(token | problem, position).

class PositionWisePolicy:
    def __init__(self):
        # Learnable embedding for each problem
        self.problem_embed = np.random.randn(num_train, embed_dim) * 0.1
        # Position-wise output layers
        self.W = np.random.randn(max_output_len, embed_dim, vocab_size) * 0.1
        self.b = np.zeros((max_output_len, vocab_size))

    def forward(self, problem_idx):
        """
        Return log-probabilities for each position.
        Returns: log_probs shape (max_output_len, vocab_size)
        """
        h = self.problem_embed[problem_idx]  # (embed_dim,)
        logits = np.zeros((max_output_len, vocab_size))
        for pos in range(max_output_len):
            logits[pos] = h @ self.W[pos] + self.b[pos]
        # Log-softmax for numerical stability
        logits_max = np.max(logits, axis=1, keepdims=True)
        exp_logits = np.exp(logits - logits_max)
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        log_probs = np.log(probs + 1e-10)
        return log_probs, probs

    def sample(self, problem_idx):
        """Sample an output sequence for the problem."""
        log_probs, probs = self.forward(problem_idx)
        tokens = []
        sampled_log_probs = []
        for pos in range(max_output_len):
            tok = np.random.choice(vocab_size, p=probs[pos])
            tokens.append(tok)
            sampled_log_probs.append(log_probs[pos, tok])
        return tokens, sampled_log_probs, probs

    def update(self, problem_idx, tokens, advantage, lr=0.1):
        """
        REINFORCE update: increase log-prob of chosen tokens if advantage > 0,
        decrease if advantage < 0.
        """
        _, probs = self.forward(problem_idx)
        h = self.problem_embed[problem_idx]

        # Gradient for each position
        for pos in range(max_output_len):
            tok = tokens[pos]
            # Gradient of log_prob w.r.t. logits: (one_hot - probs)
            grad_logits = -probs[pos].copy()
            grad_logits[tok] += 1.0
            grad_logits *= advantage  # scale by advantage

            # Update position weights
            self.W[pos] += lr * np.outer(h, grad_logits)
            self.b[pos] += lr * grad_logits

            # Update problem embedding
            self.problem_embed[problem_idx] += lr * grad_logits @ self.W[pos].T

# =============================================================================
# SECTION 4: VERIFIABLE REWARD
# =============================================================================

def verifiable_reward(tokens, ground_truth):
    """Return 1.0 if extracted answer matches ground truth, else 0.0."""
    ans = extract_answer_from_tokens(tokens)
    if ans is None:
        return 0.0
    return 1.0 if ans == ground_truth else 0.0

# =============================================================================
# SECTION 5: GRPO TRAINING
# =============================================================================

def train_grpo(policy, num_epochs=100, group_size=8, lr=0.1):
    history = {
        'epoch': [],
        'mean_reward': [],
        'mean_length': [],
        'best_reward': []
    }

    for epoch in range(num_epochs):
        epoch_rewards = []
        epoch_lengths = []

        # Train on a batch of problems
        batch_indices = np.random.choice(num_train, size=16, replace=False)

        for p_idx in batch_indices:
            problem_text, answer = train_problems[p_idx]

            # Sample group of outputs
            group_tokens = []
            group_rewards = []

            for _ in range(group_size):
                tokens, _, _ = policy.sample(p_idx)
                reward = verifiable_reward(tokens, answer)
                group_tokens.append(tokens)
                group_rewards.append(reward)
                epoch_rewards.append(reward)
                # "Chain length" = number of tokens before first <END> after <REASON>
                length = max_output_len
                for i, t in enumerate(tokens):
                    if i > 0 and t == token_to_idx['<END>']:
                        length = i
                        break
                epoch_lengths.append(length)

            # Group mean baseline (GRPO)
            baseline = np.mean(group_rewards)

            # Update policy for each output
            for i in range(group_size):
                advantage = group_rewards[i] - baseline
                if abs(advantage) < 1e-6:
                    continue
                policy.update(p_idx, group_tokens[i], advantage, lr=lr)

        history['epoch'].append(epoch)
        history['mean_reward'].append(np.mean(epoch_rewards))
        history['mean_length'].append(np.mean(epoch_lengths))
        history['best_reward'].append(np.max(epoch_rewards) if epoch_rewards else 0)

        if epoch % 10 == 0:
            print(f"Epoch {epoch}: mean_reward={history['mean_reward'][-1]:.3f}, "
                  f"mean_length={history['mean_length'][-1]:.1f}, "
                  f"best={history['best_reward'][-1]:.1f}")

    return history

# =============================================================================
# SECTION 6: EVALUATION
# =============================================================================

def evaluate(policy, n=10):
    print("\n" + "="*60)
    print("EVALUATION")
    print("="*60)
    correct = 0
    for i in range(n):
        p_idx = np.random.randint(num_train)
        text, ans = train_problems[p_idx]
        tokens, _, probs = policy.sample(p_idx)
        pred = extract_answer_from_tokens(tokens)
        reward = verifiable_reward(tokens, ans)
        correct += reward
        out_str = ''.join([idx_to_token.get(t, '') for t in tokens])
        print(f"{text}=? GT:{ans} Pred:{pred} Reward:{reward} | {out_str}")
    print(f"Accuracy: {correct}/{n} = {correct/n:.1%}")

# =============================================================================
# SECTION 7: MAIN
# =============================================================================

if __name__ == '__main__':
    print("="*60)
    print("Phase 42: Reasoning with Verifiable Rewards (NumPy)")
    print("="*60)
    print(f"Training on {num_train} unique problems.")

    policy = PositionWisePolicy()

    print("\n--- Before Training ---")
    evaluate(policy, n=10)

    print("\n--- Training with GRPO ---")
    history = train_grpo(policy, num_epochs=100, group_size=8, lr=0.15)

    print("\n--- After Training ---")
    evaluate(policy, n=10)

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(history['epoch'], history['mean_reward'], 'b-', label='Mean Reward')
    axes[0].plot(history['epoch'], history['best_reward'], 'g--', label='Best in Group')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Reward')
    axes[0].set_title('GRPO Training with Verifiable Rewards')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(history['epoch'], history['mean_length'], 'r-')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Output Length (tokens)')
    axes[1].set_title('Chain Length Over Training')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs('src/phase42', exist_ok=True)
    plt.savefig('src/phase42/verifiable_rewards.png', dpi=150)
    print("\nSaved plot to src/phase42/verifiable_rewards.png")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Final mean reward: {history['mean_reward'][-1]:.3f}")
    print("Key insight: Verifiable rewards + GRPO baseline train a policy")
    print("without any human labels. The model learns to map problems to")
    print("correct answers by trial-and-error with automatic grading.")

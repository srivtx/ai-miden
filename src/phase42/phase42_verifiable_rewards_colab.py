# Phase 42: Reasoning with Verifiable Rewards — Colab T4 PyTorch Version
# ============================================================================
# Run this in Google Colab with T4 GPU runtime.
# This demonstrates GRPO training on a small transformer for arithmetic reasoning.
#
# Key concepts:
#   - Verifiable rewards: correct answer = +1, wrong = 0
#   - GRPO: group-relative baseline, no critic needed
#   - Emergent reasoning: model learns to generate longer chains for hard problems
# ============================================================================

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
import random

# Set seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

# Check device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# =============================================================================
# SECTION 1: DATASET — ARITHMETIC PROBLEMS WITH GROUND TRUTH
# =============================================================================

def generate_arithmetic_problem(max_num: int = 20) -> Tuple[str, int]:
    """Generate a problem like '15 + 7' with integer answer."""
    a = random.randint(1, max_num)
    b = random.randint(1, max_num)
    op = random.choice(['+', '-', '*'])
    if op == '+':
        ans = a + b
    elif op == '-':
        ans = a - b
    else:
        ans = a * b
    return f"{a} {op} {b}", ans

def build_vocabulary():
    """Build vocab for digits, ops, and special tokens."""
    chars = list("0123456789+-*=() ")
    special = ['<PAD>', '<START>', '<END>', '<REASON>', '<ANSWER>']
    vocab = special + chars
    tok2idx = {c: i for i, c in enumerate(vocab)}
    idx2tok = {i: c for c, i in tok2idx.items()}
    return vocab, tok2idx, idx2tok

vocab, tok2idx, idx2tok = build_vocabulary()
vocab_size = len(vocab)
print(f"Vocabulary size: {vocab_size}")

def encode(s: str, max_len: int = 32) -> List[int]:
    """Encode string to token indices, padded."""
    tokens = [tok2idx.get(c, tok2idx['<PAD>']) for c in s]
    tokens = tokens[:max_len]
    while len(tokens) < max_len:
        tokens.append(tok2idx['<PAD>'])
    return tokens

def decode(tokens: List[int]) -> str:
    """Decode token indices to string."""
    return ''.join([idx2tok.get(t, '') for t in tokens if t != tok2idx['<PAD>']])

def extract_answer(text: str) -> int:
    """Extract integer after <ANSWER> token."""
    if '<ANSWER>' not in text:
        return None
    ans_part = text.split('<ANSWER>')[-1].replace('<END>', '').strip()
    # Extract first integer
    num_str = ''
    for ch in ans_part:
        if ch.isdigit() or (ch == '-' and not num_str):
            num_str += ch
        elif num_str:
            break
    if num_str == '' or num_str == '-':
        return None
    return int(num_str)

# =============================================================================
# SECTION 2: MINI TRANSFORMER FOR REASONING
# =============================================================================

class MiniTransformer(nn.Module):
    def __init__(self, vocab_size: int, d_model: int = 64, nhead: int = 2,
                 num_layers: int = 2, dim_feedforward: int = 128, max_len: int = 32):
        super().__init__()
        self.d_model = d_model
        self.max_len = max_len
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_len, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
            batch_first=True, dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        # x: (batch, seq_len)
        batch_size, seq_len = x.shape
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        x = self.embedding(x) + self.pos_embedding(positions)
        mask = (x[:, :, 0] == tok2idx['<PAD>'])  # simple padding mask
        out = self.transformer(x, src_key_padding_mask=mask)
        logits = self.output(out)
        return logits

    def generate(self, prompt_tokens: torch.Tensor, max_length: int = 30,
                 temperature: float = 1.0) -> Tuple[str, List[int], List[float]]:
        """Autoregressive generation with temperature sampling."""
        self.eval()
        generated = prompt_tokens.tolist()
        log_probs = []

        with torch.no_grad():
            for _ in range(max_length):
                input_tensor = torch.tensor([generated[-self.max_len:]], device=device)
                logits = self.forward(input_tensor)[:, -1, :] / temperature
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1).item()
                generated.append(next_token)
                log_probs.append(torch.log(probs[0, next_token] + 1e-10).item())
                if next_token == tok2idx['<END>']:
                    break

        text = decode(generated)
        return text, generated, log_probs

# =============================================================================
# SECTION 3: GRPO TRAINING LOOP
# =============================================================================

def verifiable_reward(output_text: str, ground_truth: int) -> float:
    """Return 1.0 if answer correct, 0.0 otherwise."""
    ans = extract_answer(output_text)
    if ans is None:
        return 0.0
    return 1.0 if ans == ground_truth else 0.0

def train_grpo(model, num_epochs=100, problems_per_epoch=16,
               group_size=8, lr=1e-3, max_len=32):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    history = {'epoch': [], 'mean_reward': [], 'mean_length': []}

    model.train()
    for epoch in range(num_epochs):
        epoch_rewards = []
        epoch_lengths = []

        for _ in range(problems_per_epoch):
            problem, answer = generate_arithmetic_problem()
            prompt = f"<START>{problem}=<REASON>"
            prompt_tokens = torch.tensor([encode(prompt, max_len=max_len)], device=device)

            # Sample group of outputs
            group_texts = []
            group_rewards = []
            group_log_probs = []

            for _ in range(group_size):
                text, tokens, log_probs = model.generate(prompt_tokens[0], max_length=20)
                reward = verifiable_reward(text, answer)
                group_texts.append(text)
                group_rewards.append(reward)
                group_log_probs.append(log_probs)
                epoch_rewards.append(reward)
                epoch_lengths.append(len(tokens))

            # Group-relative baseline
            baseline = np.mean(group_rewards)
            advantages = [r - baseline for r in group_rewards]

            # Compute policy gradient loss
            # We approximate by recomputing log probs for the generated sequences
            loss = 0.0
            for i in range(group_size):
                if advantages[i] == 0:
                    continue
                # Recompute log probs for this sequence
                seq_tokens = group_texts[i]
                seq_indices = encode(seq_tokens, max_len=max_len)
                input_ids = torch.tensor([seq_indices[:-1]], device=device)
                target_ids = torch.tensor([seq_indices[1:]], device=device)

                logits = model(input_ids)
                log_probs_all = F.log_softmax(logits, dim=-1)
                # Gather log probs for actual tokens
                gathered = log_probs_all.gather(2, target_ids.unsqueeze(-1)).squeeze(-1)
                # Mask padding
                mask = (target_ids != tok2idx['<PAD>']).float()
                seq_log_prob = (gathered * mask).sum() / (mask.sum() + 1e-8)

                loss -= advantages[i] * seq_log_prob  # gradient ascent

            if problems_per_epoch > 0:
                loss = loss / problems_per_epoch
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

        history['epoch'].append(epoch)
        history['mean_reward'].append(np.mean(epoch_rewards))
        history['mean_length'].append(np.mean(epoch_lengths))

        if epoch % 10 == 0:
            print(f"Epoch {epoch}: mean_reward={history['mean_reward'][-1]:.3f}, "
                  f"mean_length={history['mean_length'][-1]:.1f}")

    return history

# =============================================================================
# SECTION 4: MAIN — TRAIN AND VISUALIZE
# =============================================================================

if __name__ == '__main__':
    print("="*60)
    print("Phase 42 Colab: GRPO with Verifiable Rewards")
    print("="*60)

    model = MiniTransformer(vocab_size=vocab_size, d_model=64, nhead=2,
                            num_layers=2, dim_feedforward=128).to(device)

    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Train
    history = train_grpo(model, num_epochs=100, problems_per_epoch=16,
                         group_size=8, lr=1e-3)

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(history['epoch'], history['mean_reward'], 'b-')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Mean Reward')
    axes[0].set_title('GRPO Training: Mean Reward')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(history['epoch'], history['mean_length'], 'r-')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Mean Chain Length')
    axes[1].set_title('Emergent Reasoning: Chain Length')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('phase42_grpo.png', dpi=150)
    print("\nSaved plot to phase42_grpo.png")

    # Show examples
    print("\n" + "="*60)
    print("SAMPLE REASONING CHAINS")
    print("="*60)
    model.eval()
    for i in range(5):
        problem, answer = generate_arithmetic_problem()
        prompt = f"<START>{problem}=<REASON>"
        prompt_tokens = torch.tensor([encode(prompt, max_len=32)], device=device)
        text, _, _ = model.generate(prompt_tokens[0], max_length=20, temperature=0.7)
        print(f"\nProblem: {problem} = ?")
        print(f"Ground truth: {answer}")
        print(f"Model: {text}")
        print(f"Extracted: {extract_answer(text)}")

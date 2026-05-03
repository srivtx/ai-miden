#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 112 — Multi-Token Prediction Training
Designed for Google Colab T4 (16GB VRAM)
Runtime → Change runtime type → GPU → T4
This script uses REAL models (GPT-2 124M)

What this script demonstrates:
  1. Load GPT-2 124M from HuggingFace
  2. Add 3 additional LM heads on top of the final hidden state
  3. Train on Wikitext-2 with MTP loss (average CE over 4 offsets)
  4. Train a second model with standard next-token loss for comparison
  5. Evaluate both on validation perplexity
  6. Compare wall-clock speed (tokens processed per second)
  7. Generate sample text from both models

Key insight: MTP processes 4x more tokens per forward pass,
so it trains faster and provides richer gradients.
"""

# ---------------------------------------------------------------------------
# INSTALL DEPENDENCIES
# ---------------------------------------------------------------------------
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                       "transformers", "datasets", "torch", "matplotlib", "tqdm"])

import os
import time
import math
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config
from datasets import load_dataset

# ---------------------------------------------------------------------------
# REPRODUCIBILITY
# ---------------------------------------------------------------------------
SEED = 112
torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
BATCH_SIZE = 4
SEQ_LEN = 128
LEARNING_RATE = 5e-5
NUM_EPOCHS = 1
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N_MTP_HEADS = 4  # head 0 = t+1, head 1 = t+2, head 2 = t+3, head 3 = t+4
MAX_TRAIN_STEPS = 400  # cap so Colab finishes in reasonable time
MAX_VAL_STEPS = 50

print(f"Device: {DEVICE}")
print(f"Batch size: {BATCH_SIZE}, Seq len: {SEQ_LEN}, LR: {LEARNING_RATE}")
print(f"MTP heads: {N_MTP_HEADS}")

# ---------------------------------------------------------------------------
# DATASET: WIKITEXT-2
# ---------------------------------------------------------------------------
print("\nLoading wikitext-2-raw-v1 ...")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

train_dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
val_dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="validation")


def chunk_dataset(dataset, max_samples=2048):
    """
    Collapse all text into one string, then chunk into SEQ_LEN token blocks.
    Why? Wikitext-2 has many short lines; chunking gives us contiguous
    sequences that MTP heads can actually predict into.
    """
    full_text = "\n\n".join([ex["text"] for ex in dataset if len(ex["text"].strip()) > 0])
    tokens = tokenizer.encode(full_text, add_special_tokens=False)
    # Drop remainder so every chunk is exactly SEQ_LEN
    n_chunks = len(tokens) // SEQ_LEN
    tokens = tokens[:n_chunks * SEQ_LEN]
    chunks = torch.tensor(tokens, dtype=torch.long).view(-1, SEQ_LEN)
    if chunks.shape[0] > max_samples:
        chunks = chunks[:max_samples]
    return chunks

train_chunks = chunk_dataset(train_dataset, max_samples=2048)
val_chunks = chunk_dataset(val_dataset, max_samples=256)
print(f"Train chunks: {train_chunks.shape}, Val chunks: {val_chunks.shape}")

train_loader = DataLoader(torch.utils.data.TensorDataset(train_chunks),
                          batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(torch.utils.data.TensorDataset(val_chunks),
                        batch_size=BATCH_SIZE, shuffle=False)

# ---------------------------------------------------------------------------
# MODEL: GPT-2 124M WITH MTP HEADS
# ---------------------------------------------------------------------------
# We subclass GPT2LMHeadModel to add extra linear heads.
# Each head shares the transformer backbone but has its own output projection.

class GPT2MTP(GPT2LMHeadModel):
    def __init__(self, config, n_mtp_heads=4):
        super().__init__(config)
        self.n_mtp_heads = n_mtp_heads
        # The base model already has lm_head (head 0).
        # We add heads 1..n-1.
        self.mtp_heads = nn.ModuleList([
            nn.Linear(config.n_embd, config.vocab_size, bias=False)
            for _ in range(1, n_mtp_heads)
        ])
        # Initialize new heads with same std as base lm_head for stability
        with torch.no_grad():
            for head in self.mtp_heads:
                head.weight.normal_(mean=0.0, std=config.initializer_range)
        self.to(DEVICE)

    def forward_mtp(self, input_ids, labels=None):
        """
        Forward pass that returns logits for all MTP heads.
        input_ids: [batch, seq_len]
        labels: optional, same shape, used for standard evaluation

        Returns:
          all_logits: list of [batch, seq_len - offset, vocab_size]
          hidden: final hidden states [batch, seq_len, n_embd]
          base_loss: standard next-token loss from base lm_head
        """
        # Get hidden states from transformer
        outputs = self.transformer(input_ids, output_hidden_states=True)
        hidden = outputs.last_hidden_state  # [batch, seq_len, n_embd]

        all_logits = []
        # Base head predicts t+1
        logits_0 = self.lm_head(hidden[:, :-1, :])  # [batch, seq_len-1, vocab]
        all_logits.append(logits_0)

        # Extra heads predict t+2, t+3, t+4
        for i, head in enumerate(self.mtp_heads, start=2):
            # Head i predicts offset i (i=2 means t+2)
            # It sees hidden[:, :-i, :] to avoid looking past sequence end
            if hidden.size(1) <= i:
                all_logits.append(None)
                continue
            h_slice = hidden[:, :-i, :]
            all_logits.append(head(h_slice))

        # Compute standard base loss for comparison
        base_loss = None
        if labels is not None:
            shift_logits = logits_0
            shift_labels = labels[:, 1:shift_logits.size(1) + 1]
            base_loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.reshape(-1),
                ignore_index=-100
            )
        return all_logits, hidden, base_loss


def create_model():
    """Load pretrained GPT-2 config and instantiate our MTP subclass."""
    config = GPT2Config.from_pretrained("gpt2")
    model = GPT2MTP(config, n_mtp_heads=N_MTP_HEADS)
    # Copy pretrained weights into backbone and base lm_head
    pretrained = GPT2LMHeadModel.from_pretrained("gpt2")
    model.load_state_dict(pretrained.state_dict(), strict=False)
    model.to(DEVICE)
    return model


# ---------------------------------------------------------------------------
# LOSS FUNCTIONS
# ---------------------------------------------------------------------------

def mtp_loss(all_logits, input_ids):
    """
    Compute averaged cross-entropy over all MTP heads.
    all_logits[i] predicts token at offset (i+1).
    We slice input_ids accordingly.
    """
    losses = []
    for i, logits in enumerate(all_logits):
        if logits is None:
            continue
        offset = i + 1
        targets = input_ids[:, offset:offset + logits.size(1)]
        # Ensure lengths match (due to slicing)
        min_len = min(logits.size(1), targets.size(1))
        logits = logits[:, :min_len, :]
        targets = targets[:, :min_len]
        loss = F.cross_entropy(
            logits.reshape(-1, logits.size(-1)),
            targets.reshape(-1),
            ignore_index=-100
        )
        losses.append(loss)
    return torch.stack(losses).mean()


# ---------------------------------------------------------------------------
# TRAINING LOOPS
# ---------------------------------------------------------------------------

def train_mtp(model, loader, max_steps):
    """Train with multi-token prediction loss."""
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    losses = []
    tokens_processed = 0
    start_time = time.time()
    step = 0
    for batch in tqdm(loader, desc="Train MTP", total=max_steps):
        if step >= max_steps:
            break
        input_ids = batch[0].to(DEVICE)
        optimizer.zero_grad()
        all_logits, _, _ = model.forward_mtp(input_ids)
        loss = mtp_loss(all_logits, input_ids)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.item()))
        # Each forward pass processes seq_len tokens, but MTP produces
        # multiple labels per position. For throughput we count raw tokens.
        tokens_processed += input_ids.numel()
        step += 1
    elapsed = time.time() - start_time
    return losses, tokens_processed, elapsed


def train_standard(model, loader, max_steps):
    """Train with standard next-token prediction (base head only)."""
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    losses = []
    tokens_processed = 0
    start_time = time.time()
    step = 0
    for batch in tqdm(loader, desc="Train Standard", total=max_steps):
        if step >= max_steps:
            break
        input_ids = batch[0].to(DEVICE)
        labels = input_ids.clone()
        optimizer.zero_grad()
        # Use base model's built-in loss computation for exact parity
        outputs = model(input_ids, labels=labels)
        loss = outputs.loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.item()))
        tokens_processed += input_ids.numel()
        step += 1
    elapsed = time.time() - start_time
    return losses, tokens_processed, elapsed


# ---------------------------------------------------------------------------
# EVALUATION: PERPLEXITY
# ---------------------------------------------------------------------------

def evaluate_perplexity(model, loader, max_steps, mode="mtp"):
    """
    Compute average next-token perplexity.
    For MTP model, we evaluate using only the base head (t+1)
    so the comparison is fair.
    """
    model.eval()
    total_nll = 0.0
    total_tokens = 0
    step = 0
    with torch.no_grad():
        for batch in tqdm(loader, desc=f"Eval {mode}", total=max_steps):
            if step >= max_steps:
                break
            input_ids = batch[0].to(DEVICE)
            if mode == "mtp":
                all_logits, _, _ = model.forward_mtp(input_ids)
                logits = all_logits[0]  # base head
                targets = input_ids[:, 1:logits.size(1) + 1]
            else:
                logits = model(input_ids).logits[:, :-1, :]
                targets = input_ids[:, 1:]
            min_len = min(logits.size(1), targets.size(1))
            logits = logits[:, :min_len, :]
            targets = targets[:, :min_len]
            nll = F.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                targets.reshape(-1),
                reduction='sum'
            )
            total_nll += float(nll.item())
            total_tokens += targets.numel()
            step += 1
    avg_nll = total_nll / total_tokens
    ppl = math.exp(avg_nll)
    return ppl


# ---------------------------------------------------------------------------
# GENERATION
# ---------------------------------------------------------------------------

def generate_sample(model, prompt="In the year 2150, humanity", max_new_tokens=30, mode="mtp"):
    """Greedy generation for quick qualitative comparison."""
    model.eval()
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        # For MTP model, generation uses base model path only
        output = model.generate(input_ids, max_new_tokens=max_new_tokens,
                                do_sample=False, pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(output[0], skip_special_tokens=True)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 112: Multi-Token Prediction Training on GPT-2 124M")
print("=" * 70)

# --- Train MTP model ---
print("\n--- Training with MTP (4 heads) ---")
model_mtp = create_model()
losses_mtp, tokens_mtp, time_mtp = train_mtp(model_mtp, train_loader, MAX_TRAIN_STEPS)
print(f"MTP: processed {tokens_mtp} tokens in {time_mtp:.1f}s")
print(f"MTP: throughput = {tokens_mtp/time_mtp:.1f} tokens/sec")
print("Sample (MTP):", generate_sample(model_mtp, mode="mtp"))

# --- Train Standard model ---
print("\n--- Training with Standard Next-Token Prediction ---")
# Create a fresh standard GPT-2 for fair comparison
from transformers import GPT2LMHeadModel
model_std = GPT2LMHeadModel.from_pretrained("gpt2").to(DEVICE)
losses_std, tokens_std, time_std = train_standard(model_std, train_loader, MAX_TRAIN_STEPS)
print(f"Std: processed {tokens_std} tokens in {time_std:.1f}s")
print(f"Std: throughput = {tokens_std/time_std:.1f} tokens/sec")
print("Sample (Std):", generate_sample(model_std, mode="std"))

# --- Perplexity evaluation ---
print("\n--- Validation Perplexity ---")
ppl_mtp = evaluate_perplexity(model_mtp, val_loader, MAX_VAL_STEPS, mode="mtp")
ppl_std = evaluate_perplexity(model_std, val_loader, MAX_VAL_STEPS, mode="std")
print(f"MTP perplexity:  {ppl_mtp:.2f}")
print(f"Std perplexity:  {ppl_std:.2f}")

# --- Plot loss curves ---
os.makedirs("src/phase112", exist_ok=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Loss vs steps
axes[0].plot(losses_mtp, label='MTP (4 heads)', alpha=0.8)
axes[0].plot(losses_std, label='Standard (1 head)', alpha=0.8)
axes[0].set_xlabel('Step')
axes[0].set_ylabel('Loss')
axes[0].set_title('Training Loss per Step')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Loss vs wall-clock time (interpolated)
# We assume uniform time per step within each run
time_mtp_per_step = time_mtp / len(losses_mtp) if losses_mtp else 0
time_std_per_step = time_std / len(losses_std) if losses_std else 0
t_mtp = np.arange(len(losses_mtp)) * time_mtp_per_step
t_std = np.arange(len(losses_std)) * time_std_per_step
axes[1].plot(t_mtp, losses_mtp, label='MTP', alpha=0.8)
axes[1].plot(t_std, losses_std, label='Standard', alpha=0.8)
axes[1].set_xlabel('Wall-clock time (seconds)')
axes[1].set_ylabel('Loss')
axes[1].set_title('Training Loss vs Time')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('src/phase112/mtp_loss_comparison.png', dpi=150)
plt.close()
print("\nSaved: src/phase112/mtp_loss_comparison.png")

# --- Plot throughput comparison ---
fig, ax = plt.subplots(figsize=(6, 4))
methods = ['MTP', 'Standard']
throughputs = [tokens_mtp/time_mtp if time_mtp else 0,
               tokens_std/time_std if time_std else 0]
ax.bar(methods, throughputs, alpha=0.8)
ax.set_ylabel('Tokens / second')
ax.set_title('Training Throughput')
ax.grid(True, alpha=0.3, axis='y')
for i, v in enumerate(throughputs):
    ax.text(i, v + max(throughputs)*0.02, f"{v:.1f}", ha='center')
plt.tight_layout()
plt.savefig('src/phase112/mtp_throughput_comparison.png', dpi=150)
plt.close()
print("Saved: src/phase112/mtp_throughput_comparison.png")

# --- Plot perplexity comparison ---
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(['MTP', 'Standard'], [ppl_mtp, ppl_std], alpha=0.8)
ax.set_ylabel('Perplexity')
ax.set_title('Validation Perplexity')
ax.grid(True, alpha=0.3, axis='y')
for i, v in enumerate([ppl_mtp, ppl_std]):
    ax.text(i, v + max(ppl_mtp, ppl_std)*0.02, f"{v:.2f}", ha='center')
plt.tight_layout()
plt.savefig('src/phase112/mtp_perplexity_comparison.png', dpi=150)
plt.close()
print("Saved: src/phase112/mtp_perplexity_comparison.png")

# ---------------------------------------------------------------------------
# SUMMARY TABLE
# ---------------------------------------------------------------------------
print("\n--- Summary ---")
print(f"{'Metric':<30}  {'MTP':>12}  {'Standard':>12}")
print("-" * 58)
print(f"{'Final training loss':<30}  {losses_mtp[-1]:>12.4f}  {losses_std[-1]:>12.4f}")
print(f"{'Tokens processed':<30}  {tokens_mtp:>12}  {tokens_std:>12}")
print(f"{'Wall-clock time (s)':<30}  {time_mtp:>12.1f}  {time_std:>12.1f}")
print(f"{'Throughput (tok/s)':<30}  {tokens_mtp/time_mtp:>12.1f}  {tokens_std/time_std:>12.1f}")
print(f"{'Validation perplexity':<30}  {ppl_mtp:>12.2f}  {ppl_std:>12.2f}")

print("\n" + "=" * 70)
print("Phase 112 Colab demonstration complete.")
print("=" * 70)

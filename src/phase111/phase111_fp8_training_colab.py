#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 111 — FP8 and Low-Precision Training
Designed for Google Colab T4 (16GB VRAM)
Runtime → Change runtime type → GPU → T4
This script uses REAL models (GPT-2 124M)

--- H100 REAL FP8 NOTE ---
To run on H100 with native FP8 tensor cores, install transformer-engine:
  !pip install -q transformer-engine[pytorch]
And replace the simulated quantization below with te.Linear() layers.
Transformer Engine handles E4M3/E5M2 selection, delayed scaling, and
per-tensor scaling automatically. This script simulates those behaviors
on T4 because T4 lacks FP8 tensor cores.

What this script demonstrates:
  1. Load GPT-2 124M and Wikitext-2
  2. Train in pure FP32 (baseline)
  3. Train with simulated FP8 + scaling (master weights FP32)
  4. Train with simulated FP8 WITHOUT scaling (shows NaN/overflow)
  5. Compare loss curves and generated text
"""

# ---------------------------------------------------------------------------
# INSTALL DEPENDENCIES
# ---------------------------------------------------------------------------
# These install silently so the notebook stays clean.
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                       "transformers", "datasets", "torch", "matplotlib", "tqdm"])

import os
import math
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config
from datasets import load_dataset

# ---------------------------------------------------------------------------
# REPRODUCIBILITY
# ---------------------------------------------------------------------------
SEED = 111
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

# ---------------------------------------------------------------------------
# TRAINING CONFIGURATION
# ---------------------------------------------------------------------------
# We use a small config so a T4 can handle three training runs in one session.
BATCH_SIZE = 4
SEQ_LEN = 128
LEARNING_RATE = 5e-5
NUM_EPOCHS = 1
MAX_STEPS_PER_MODE = 300  # cap steps so the Colab finishes in minutes
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"Device: {DEVICE}")
print(f"Batch size: {BATCH_SIZE}, Seq len: {SEQ_LEN}, LR: {LEARNING_RATE}")

# ---------------------------------------------------------------------------
# FP8 SIMULATION UTILITIES
# ---------------------------------------------------------------------------
# T4 has no FP8 tensor cores, so we simulate FP8 with custom quantization.
# We build explicit codebooks for E4M3 and E5M2, then round to nearest.

_E4M3_CODES = []
for c in range(256):
    s = -1.0 if ((c >> 7) & 1) else 1.0
    e = (c >> 3) & 0xF
    m = c & 0x7
    if e == 0:
        v = s * (2 ** (-6)) * (m / 8.0)
    elif e == 0b1111:
        if m == 0b111:
            v = s * 448.0
        else:
            continue
    else:
        v = s * (2 ** (e - 7)) * (1.0 + m / 8.0)
    _E4M3_CODES.append(v)
E4M3_CODES = torch.tensor(sorted(set(_E4M3_CODES)), dtype=torch.float32, device=DEVICE)
E4M3_MAX = float(E4M3_CODES.max())

_E5M2_CODES = []
for c in range(256):
    s = -1.0 if ((c >> 7) & 1) else 1.0
    e = (c >> 2) & 0x1F
    m = c & 0x3
    if e == 0:
        v = s * (2 ** (-14)) * (m / 4.0)
    elif e == 0b11111:
        continue
    else:
        v = s * (2 ** (e - 15)) * (1.0 + m / 4.0)
    _E5M2_CODES.append(v)
E5M2_CODES = torch.tensor(sorted(set(_E5M2_CODES)), dtype=torch.float32, device=DEVICE)
E5M2_MAX = float(E5M2_CODES.max())


def fake_quantize_e4m3(tensor, scale):
    """
    Simulate E4M3 quantization with a given scale factor.
    scale = max_fp8 / max_abs_tensor.
    We clamp the scaled tensor to the codebook range, then round to nearest code.
    Why E4M3? We use it for weights in the forward pass.
    """
    if scale is None or scale <= 0:
        return tensor
    scaled = tensor * scale
    # Clamp to codebook min/max to simulate clipping
    cb_min = E4M3_CODES.min()
    cb_max = E4M3_CODES.max()
    scaled = torch.clamp(scaled, cb_min, cb_max)
    # Round to nearest codebook entry
    # For speed on T4, we use a simple search (codebook is only ~240 entries)
    flat = scaled.view(-1)
    idx = torch.argmin(torch.abs(E4M3_CODES.unsqueeze(1) - flat.unsqueeze(0)), dim=0)
    quantized = E4M3_CODES[idx].view_as(tensor)
    return quantized / scale


def fake_quantize_e5m2(tensor, scale):
    """
    Simulate E5M2 quantization for gradients.
    E5M2 has wider range, which protects against gradient spikes.
    """
    if scale is None or scale <= 0:
        return tensor
    scaled = tensor * scale
    cb_min = E5M2_CODES.min()
    cb_max = E5M2_CODES.max()
    scaled = torch.clamp(scaled, cb_min, cb_max)
    flat = scaled.view(-1)
    idx = torch.argmin(torch.abs(E5M2_CODES.unsqueeze(1) - flat.unsqueeze(0)), dim=0)
    quantized = E5M2_CODES[idx].view_as(tensor)
    return quantized / scale


# ---------------------------------------------------------------------------
# DATASET: WIKITEXT-2
# ---------------------------------------------------------------------------
# We use the raw version because it preserves original punctuation and casing.
print("\nLoading wikitext-2-raw-v1 ...")
dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token


def tokenize_function(examples):
    # Concatenate all text and chunk into SEQ_LEN blocks
    return tokenizer(examples["text"], truncation=True, max_length=SEQ_LEN,
                     padding="max_length", return_overflowing_tokens=True)

# Flatten the dataset into fixed-length token blocks
tokenized = []
for ex in dataset:
    text = ex["text"]
    if len(text.strip()) == 0:
        continue
    tokens = tokenizer(text, truncation=True, max_length=SEQ_LEN,
                       padding="max_length", return_tensors="pt")
    tokenized.append(tokens["input_ids"].squeeze(0))

# Stack into a single tensor and batch
token_ids = torch.stack(tokenized[:1024])  # limit to 1024 sequences for speed
print(f"Tokenized sequences: {token_ids.shape[0]}")


def get_dataloader():
    # Simple sequential batching; no shuffle for reproducible comparison
    ds = torch.utils.data.TensorDataset(token_ids)
    return DataLoader(ds, batch_size=BATCH_SIZE, shuffle=False)


# ---------------------------------------------------------------------------
# MODEL FACTORY
# ---------------------------------------------------------------------------
# We use GPT-2 124M (the smallest checkpoint). It fits easily on T4.

def create_model():
    """Load pretrained GPT-2 and move to device."""
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    model.resize_token_embeddings(len(tokenizer))
    model.to(DEVICE)
    return model


# ---------------------------------------------------------------------------
# TRAINING LOOPS
# ---------------------------------------------------------------------------
# We define three training modes:
#   A) FP32 baseline
#   B) Simulated FP8 WITH per-tensor scaling
#   C) Simulated FP8 WITHOUT scaling (demonstrates overflow)

def train_fp32(model, dataloader, max_steps):
    """Standard FP32 training. Master weights are already FP32."""
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    losses = []
    step = 0
    for batch in tqdm(dataloader, desc="FP32", total=max_steps):
        if step >= max_steps:
            break
        input_ids = batch[0].to(DEVICE)
        labels = input_ids.clone()
        optimizer.zero_grad()
        outputs = model(input_ids, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        losses.append(float(loss.item()))
        step += 1
    return losses


def train_fp8_scaled(model, dataloader, max_steps):
    """
    Simulated FP8 mixed precision training.
    Master weights stay in FP32.
    Forward pass: weights are fake-quantized to E4M3 with per-tensor scaling.
    Backward pass: gradients are fake-quantized to E5M2 with per-tensor scaling.
    Why master weights in FP32? Because FP8 weight updates underflow.
    """
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    losses = []
    step = 0

    # Maintain a dictionary of delayed scale factors for each parameter
    # In real Transformer Engine, this is managed per-tensor with a ring buffer.
    delayed_scales = {n: 1.0 for n, p in model.named_parameters() if p.requires_grad}

    for batch in tqdm(dataloader, desc="FP8+scale", total=max_steps):
        if step >= max_steps:
            break
        input_ids = batch[0].to(DEVICE)
        labels = input_ids.clone()
        optimizer.zero_grad()

        # --- Fake quantization of weights for forward pass ---
        # We temporarily replace parameters with quantized versions.
        # In a real system, this happens inside the CUDA kernel.
        original_params = {}
        for n, p in model.named_parameters():
            if not p.requires_grad:
                continue
            max_abs = float(torch.max(torch.abs(p.data)))
            if max_abs > 0:
                scale = E4M3_MAX / max_abs
            else:
                scale = 1.0
            # Delayed scaling: use previous step's scale, then update
            prev_scale = delayed_scales[n]
            q = fake_quantize_e4m3(p.data, prev_scale)
            original_params[n] = p.data.clone()
            p.data = q
            # Update delayed scale for next step using current max_abs
            delayed_scales[n] = scale

        # Forward pass (computes loss in FP32, which is stable)
        outputs = model(input_ids, labels=labels)
        loss = outputs.loss

        # Backward pass produces gradients in FP32
        loss.backward()

        # --- Fake quantization of gradients to E5M2 ---
        for n, p in model.named_parameters():
            if p.grad is None:
                continue
            max_abs_g = float(torch.max(torch.abs(p.grad)))
            if max_abs_g > 0:
                scale_g = E5M2_MAX / max_abs_g
            else:
                scale_g = 1.0
            p.grad = fake_quantize_e5m2(p.grad, scale_g)

        # Restore original FP32 weights before optimizer step
        for n, p in model.named_parameters():
            if n in original_params:
                p.data = original_params[n]

        # Optimizer updates FP32 master weights with (simulated) FP8 gradients
        optimizer.step()
        losses.append(float(loss.item()))
        step += 1
    return losses


def train_fp8_no_scale(model, dataloader, max_steps):
    """
    Simulated FP8 WITHOUT scaling.
    This demonstrates what happens when you naively cast FP32 weights
    to FP8 without rescaling: small values underflow to zero, and
    large values clip or overflow. Loss quickly explodes or freezes.
    """
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    losses = []
    step = 0
    for batch in tqdm(dataloader, desc="FP8 no-scale", total=max_steps):
        if step >= max_steps:
            break
        input_ids = batch[0].to(DEVICE)
        labels = input_ids.clone()
        optimizer.zero_grad()

        # Naive quantization: scale=1.0 means no rescaling
        original_params = {}
        for n, p in model.named_parameters():
            if not p.requires_grad:
                continue
            q = fake_quantize_e4m3(p.data, scale=1.0)
            original_params[n] = p.data.clone()
            p.data = q

        outputs = model(input_ids, labels=labels)
        loss = outputs.loss
        loss.backward()

        # Also naively quantize gradients
        for n, p in model.named_parameters():
            if p.grad is None:
                continue
            p.grad = fake_quantize_e5m2(p.grad, scale=1.0)

        for n, p in model.named_parameters():
            if n in original_params:
                p.data = original_params[n]

        optimizer.step()
        losses.append(float(loss.item()))
        step += 1
    return losses


# ---------------------------------------------------------------------------
# GENERATION HELPER
# ---------------------------------------------------------------------------

def generate_sample(model, prompt="The future of artificial intelligence is", max_new_tokens=30):
    """Greedy generation for quick comparison."""
    model.eval()
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        output = model.generate(input_ids, max_new_tokens=max_new_tokens,
                                do_sample=False, pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(output[0], skip_special_tokens=True)


# ---------------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 111: FP8 Training Simulation on GPT-2 124M")
print("=" * 70)

dataloader = get_dataloader()

# --- Mode A: FP32 baseline ---
print("\n--- Mode A: FP32 Baseline ---")
model_fp32 = create_model()
losses_fp32 = train_fp32(model_fp32, dataloader, MAX_STEPS_PER_MODE)
print("Sample (FP32):", generate_sample(model_fp32))

# --- Mode B: FP8 with scaling ---
print("\n--- Mode B: Simulated FP8 with Scaling ---")
model_fp8_scale = create_model()
losses_fp8_scale = train_fp8_scaled(model_fp8_scale, dataloader, MAX_STEPS_PER_MODE)
print("Sample (FP8 scaled):", generate_sample(model_fp8_scale))

# --- Mode C: FP8 without scaling ---
print("\n--- Mode C: Simulated FP8 WITHOUT Scaling ---")
model_fp8_noscale = create_model()
losses_fp8_noscale = train_fp8_no_scale(model_fp8_noscale, dataloader, MAX_STEPS_PER_MODE)
print("Sample (FP8 no-scale):", generate_sample(model_fp8_noscale))

# ---------------------------------------------------------------------------
# PLOT LOSS CURVES
# ---------------------------------------------------------------------------
os.makedirs("src/phase111", exist_ok=True)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(losses_fp32, label='FP32 baseline', alpha=0.8)
ax.plot(losses_fp8_scale, label='FP8 + scaling', alpha=0.8)
ax.plot(losses_fp8_noscale, label='FP8 no scaling', alpha=0.8)
ax.set_xlabel('Step')
ax.set_ylabel('Loss')
ax.set_title('Training Loss: FP32 vs Simulated FP8')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('src/phase111/fp8_loss_curves.png', dpi=150)
plt.close()
print("\nSaved: src/phase111/fp8_loss_curves.png")

# ---------------------------------------------------------------------------
# FINAL SUMMARY TABLE
# ---------------------------------------------------------------------------
print("\n--- Final Loss Statistics ---")
print(f"{'Mode':<25}  {'Final Loss':>10}  {'Mean Loss':>10}")
print("-" * 50)
for name, losses in [("FP32", losses_fp32), ("FP8+scale", losses_fp8_scale), ("FP8 no-scale", losses_fp8_noscale)]:
    if len(losses) > 0:
        print(f"{name:<25}  {losses[-1]:>10.4f}  {np.mean(losses):>10.4f}")
    else:
        print(f"{name:<25}  {'N/A':>10}  {'N/A':>10}")

print("\n" + "=" * 70)
print("Phase 111 Colab demonstration complete.")
print("=" * 70)

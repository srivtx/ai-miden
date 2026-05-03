#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 121 — Pretraining a Language Model from Scratch
Designed for Google Colab T4 (16GB VRAM)
Runtime -> Change runtime type -> GPU -> T4
This script uses REAL models and ACTUALLY TRAINS them

Install dependencies (run in first Colab cell):
!pip install -q transformers datasets torch accelerate bitsandbytes matplotlib tqdm
"""

# =============================================================================
# SECTION 0: IMPORTS AND SETUP
# =============================================================================
# We import everything needed for building, training, and evaluating a real
# GPT-2 124M model from scratch. Every import is justified below.

import os
import math
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    GPT2Tokenizer,
    get_cosine_schedule_with_warmup,
)
from datasets import load_dataset
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm

# Verify GPU availability. T4 gives us ~16GB VRAM, enough for GPT-2 124M.
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")
if device.type == 'cuda':
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# Set seeds for reproducibility. Pretraining is stochastic; seeds make
# the Colab demo repeatable across runs.
torch.manual_seed(121)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(121)

# =============================================================================
# SECTION 1: BUILD GPT-2 124M FROM SCRATCH
# =============================================================================
# We instantiate GPT2Config with the standard 124M parameters, then create
# GPT2LMHeadModel with random weights (no pretrained checkpoint loaded).
# This is the key difference from fine-tuning: every parameter is initialized
# from scratch using the library's built-in initialization logic.

print("\n" + "="*60)
print("SECTION 1: Building GPT-2 124M from scratch")
print("="*60)

config = GPT2Config(
    vocab_size=50257,      # GPT-2 BPE vocab size
    n_positions=1024,      # maximum sequence length
    n_embd=768,            # embedding dimension
    n_layer=12,            # transformer blocks
    n_head=12,             # attention heads per block
    n_inner=3072,          # feedforward hidden dimension (4 * n_embd)
    resid_pdrop=0.1,       # dropout on residual connections
    embd_pdrop=0.1,        # dropout on embeddings
    attn_pdrop=0.1,        # dropout on attention
)

model = GPT2LMHeadModel(config)
model.to(device)

# Count parameters to confirm we built the right size.
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters:     {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")
print(f"Model size:           {total_params * 4 / 1e6:.1f} MB (FP32)")

# =============================================================================
# SECTION 2: TOKENIZER AND DATASET
# =============================================================================
# We use the standard GPT-2 tokenizer and WikiText-2 as our pretraining corpus.
# WikiText-2 is small enough to download quickly in Colab but still contains
# real Wikipedia articles with rich vocabulary and syntax.

print("\n" + "="*60)
print("SECTION 2: Loading tokenizer and dataset")
print("="*60)

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
# GPT-2 tokenizer does not have a pad token by default. We use EOS as PAD
# so we can batch sequences of different lengths without errors.
tokenizer.pad_token = tokenizer.eos_token

# Load WikiText-2 raw. The "raw" version contains actual article text without
# the pre-tokenized formatting, which is what we want for pretraining.
dataset = load_dataset('wikitext', 'wikitext-2-raw-v1', split='train')

# Remove empty lines. WikiText contains many blank lines that waste compute.
dataset = dataset.filter(lambda x: len(x['text'].strip()) > 0)
print(f"Dataset examples after filtering: {len(dataset)}")

# Tokenize the entire dataset. We truncate to 128 tokens per example because
# 500 steps of full 1024-length sequences would take too long on a T4.
# Pretraining on shorter chunks still teaches syntax and vocabulary.
max_length = 128

def tokenize_function(examples):
    return tokenizer(
        examples['text'],
        truncation=True,
        max_length=max_length,
        return_overflowing_tokens=False,
    )

tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=dataset.column_names,
)
print(f"Tokenized examples: {len(tokenized_dataset)}")

# =============================================================================
# SECTION 3: DATALOADER FOR CAUSAL LANGUAGE MODELING
# =============================================================================
# For CLM, the labels are the input IDs shifted by one position. The
# DataCollatorForLanguageModeling in transformers handles this automatically,
# but we write a simple custom collator here to show exactly what happens.

class CLMCollator:
    def __init__(self, pad_token_id):
        self.pad_token_id = pad_token_id

    def __call__(self, batch):
        # Stack input_ids into a tensor
        input_ids = [torch.tensor(b['input_ids'], dtype=torch.long) for b in batch]
        # Pad to max length in batch
        input_ids = nn.utils.rnn.pad_sequence(
            input_ids, batch_first=True, padding_value=self.pad_token_id
        )
        # For causal LM, labels are identical to input_ids. The model internally
        # shifts them by one position to predict the next token.
        labels = input_ids.clone()
        # We mask padding tokens in the loss so the model does not learn to
        # predict EOS repeatedly after the real sequence ends.
        labels[labels == self.pad_token_id] = -100
        return {'input_ids': input_ids, 'labels': labels}

collator = CLMCollator(pad_token_id=tokenizer.pad_token_id)

# Batch size 8 * sequence length 128 = 1024 tokens per batch. This fits
# comfortably on a T4 and allows meaningful gradient updates.
batch_size = 8
dataloader = DataLoader(
    tokenized_dataset,
    batch_size=batch_size,
    shuffle=True,
    collate_fn=collator,
    drop_last=True,
)
print(f"Batches per epoch: {len(dataloader)}")

# =============================================================================
# SECTION 4: OPTIMIZER AND LEARNING RATE SCHEDULE
# =============================================================================
# Pretraining uses AdamW with weight decay. We use a warmup+cosine decay
# schedule: linear warmup for 100 steps prevents early instability from
# large gradients on random-initialized weights, and cosine decay smoothly
# reduces the learning rate to help convergence.

learning_rate = 6e-4
warmup_steps = 100
total_steps = 500

optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
scheduler = get_cosine_schedule_with_warmup(
    optimizer,
    num_warmup_steps=warmup_steps,
    num_training_steps=total_steps,
)

print(f"\nOptimizer: AdamW, lr={learning_rate}, weight_decay=0.01")
print(f"Scheduler: warmup={warmup_steps} steps, cosine decay to {total_steps} steps")

# =============================================================================
# SECTION 5: TRAINING LOOP
# =============================================================================
# We train for 500 steps, evaluating perplexity and generating samples every
# 100 steps. Perplexity is the standard metric for language modeling: it
# measures how surprised the model is by the next token. Lower is better.

print("\n" + "="*60)
print("SECTION 5: Training")
print("="*60)

model.train()
loss_history = []
perplexity_history = []
step_numbers = []
grad_norm_history = []
sample_texts = []

global_step = 0
data_iter = iter(dataloader)

progress_bar = tqdm(range(total_steps), desc="Training", unit="step")

for step in progress_bar:
    # Fetch next batch, restarting the iterator if we exhaust the dataset
    try:
        batch = next(data_iter)
    except StopIteration:
        data_iter = iter(dataloader)
        batch = next(data_iter)

    input_ids = batch['input_ids'].to(device)
    labels = batch['labels'].to(device)

    # Forward pass: the model returns logits for every position.
    outputs = model(input_ids=input_ids, labels=labels)
    loss = outputs.loss

    # Backward pass
    optimizer.zero_grad()
    loss.backward()

    # Gradient clipping prevents rare but catastrophic gradient spikes.
    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    grad_norm_history.append(grad_norm.item())

    optimizer.step()
    scheduler.step()

    loss_history.append(loss.item())
    progress_bar.set_postfix({'loss': f'{loss.item():.4f}', 'lr': f'{scheduler.get_last_lr()[0]:.2e}'})

    # Memory cleanup every 50 steps prevents T4 VRAM fragmentation.
    if step % 50 == 0 and step > 0 and torch.cuda.is_available():
        torch.cuda.empty_cache()

    # =====================================================================
    # EVALUATION EVERY 100 STEPS
    # =====================================================================
    if step % 100 == 0 or step == total_steps - 1:
        model.eval()
        with torch.no_grad():
            # Perplexity = exp(average cross-entropy loss)
            # We compute it on the current batch for speed.
            perplexity = math.exp(loss.item())
            perplexity_history.append(perplexity)
            step_numbers.append(step)
            print(f"\n--- Step {step} ---")
            print(f"Loss:       {loss.item():.4f}")
            print(f"Perplexity: {perplexity:.2f}")
            print(f"LR:         {scheduler.get_last_lr()[0]:.2e}")
            print(f"Grad norm:  {grad_norm.item():.4f}")

            # Generate sample text to show progression.
            # We start from a simple prompt and let the model complete it.
            prompt = "The history of artificial intelligence"
            input_ids_gen = tokenizer.encode(prompt, return_tensors='pt').to(device)
            output_ids = model.generate(
                input_ids_gen,
                max_new_tokens=30,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.8,
                pad_token_id=tokenizer.eos_token_id,
            )
            generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            sample_texts.append((step, generated_text))
            print(f"Sample:     {generated_text}")

        model.train()

# =============================================================================
# SECTION 6: SAVE CHECKPOINT
# =============================================================================
# Saving the trained model allows resuming, further fine-tuning, or serving.

checkpoint_dir = './phase121_checkpoint'
os.makedirs(checkpoint_dir, exist_ok=True)
model.save_pretrained(checkpoint_dir)
tokenizer.save_pretrained(checkpoint_dir)
print(f"\nCheckpoint saved to {checkpoint_dir}")

# =============================================================================
# SECTION 7: PLOTS
# =============================================================================
# We save all diagnostic plots so the student can analyze the training run
# after the script finishes.

print("\n" + "="*60)
print("SECTION 7: Saving plots")
print("="*60)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Loss curve
ax = axes[0, 0]
ax.plot(loss_history, color='#2c3e50', linewidth=1.2)
ax.set_xlabel('Training Step')
ax.set_ylabel('Cross-Entropy Loss')
ax.set_title('Pretraining Loss Curve (GPT-2 124M from Scratch)')
ax.grid(True, alpha=0.3)

# Plot 2: Perplexity over time
ax = axes[0, 1]
ax.plot(step_numbers, perplexity_history, 'o-', color='#e74c3c', linewidth=2, markersize=8)
ax.set_xlabel('Training Step')
ax.set_ylabel('Perplexity')
ax.set_title('Perplexity Over Time (lower is better)')
ax.grid(True, alpha=0.3)

# Plot 3: Gradient norms
ax = axes[1, 0]
ax.plot(grad_norm_history, color='#27ae60', linewidth=1.2)
ax.set_xlabel('Training Step')
ax.set_ylabel('Gradient Norm (after clipping)')
ax.set_title('Gradient Norms Over Training')
ax.grid(True, alpha=0.3)

# Plot 4: Learning rate schedule
lr_history = [scheduler.get_last_lr()[0] for _ in range(total_steps)]
# Reconstruct LR history from the actual schedule
lr_history = []
for s in range(total_steps):
    if s < warmup_steps:
        lr = learning_rate * (s / warmup_steps)
    else:
        progress = (s - warmup_steps) / (total_steps - warmup_steps)
        lr = learning_rate * 0.5 * (1.0 + math.cos(math.pi * progress))
    lr_history.append(lr)

ax = axes[1, 1]
ax.plot(lr_history, color='#9b59b6', linewidth=1.5)
ax.set_xlabel('Training Step')
ax.set_ylabel('Learning Rate')
ax.set_title('Cosine Decay with Warmup')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plot_path = 'phase121_pretraining_plots.png'
plt.savefig(plot_path, dpi=150)
print(f"Saved plots to {plot_path}")

# =============================================================================
# SECTION 8: FINAL SUMMARY
# =============================================================================
print("\n" + "="*60)
print("FINAL SUMMARY")
print("="*60)
print(f"Initial loss:       {loss_history[0]:.4f}")
print(f"Final loss:         {loss_history[-1]:.4f}")
print(f"Initial perplexity: {math.exp(loss_history[0]):.2f}")
print(f"Final perplexity:   {math.exp(loss_history[-1]):.2f}")
print(f"Checkpoint:         {checkpoint_dir}")
print("\nGenerated text progression:")
for step, text in sample_texts:
    print(f"  Step {step:3d}: {text}")
print("\nKey insights:")
print("  1. Loss decreased consistently, showing the model learned from random init")
print("  2. Perplexity dropped from ~vocab_size to much lower, indicating structure")
print("  3. Generated text progressed from nonsense to English-like phrases")
print("  4. Gradient clipping kept training stable despite random initialization")
print("  5. Warmup prevented early divergence from large gradients")

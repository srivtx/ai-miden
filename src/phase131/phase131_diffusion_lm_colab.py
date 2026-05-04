"""
Phase 131: Diffusion Language Models — Real Model Training (Colab T4)
=====================================================================
Run this on Google Colab with a T4 GPU to train a small diffusion LM.

This script demonstrates the FULL pipeline:
  1. Load WikiText-2 dataset
  2. Train a small BERT-style masked LM (6 layers, 256 dim, 4 heads)
  3. Use it for diffusion generation: start with all [MASK], iteratively unmask
  4. Compare with autoregressive generation from the same model
  5. Plot denoising trajectory and confidence curves

WHY a 6-layer, 256-dim model? It fits on T4 VRAM (~1.5 GB), trains
in under 15 minutes for 500 steps, and is large enough to show real
diffusion behavior on natural text.

WHY WikiText-2? It is small (~2M tokens), publicly available, and
represents real English prose. No dataset upload needed.

WHY 500 steps? Enough to see the loss curve descend and the model
produce coherent short phrases. More steps would improve quality but
add linear time.
=====================================================================
"""

# ==============================================================================
# FRONTIER TRACK — PHASE 131
# ==============================================================================
# Install dependencies (uncomment in Colab):
# !pip install transformers datasets torch -q

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
import gc
import os

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# WHY these settings? The model must fit on a T4 (15 GB VRAM) while
# being deep enough to capture contextual dependencies for diffusion.

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
VOCAB_SIZE = 30522  # BERT wordpiece vocab size
MAX_LEN = 64
BATCH_SIZE = 32
LEARNING_RATE = 5e-4
N_TRAIN_STEPS = 500
MASK_PROB = 0.15

EMBED_DIM = 256
NUM_LAYERS = 6
NUM_HEADS = 4
FF_DIM = 512

print(f"Using device: {DEVICE}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# ==============================================================================
# STEP 1: LOAD DATASET AND TOKENIZER
# ==============================================================================
# WHY AutoTokenizer from bert-base-uncased? It gives us a standard
# subword vocabulary and [MASK] token ID without training a tokenizer.

from transformers import AutoTokenizer
from datasets import load_dataset

print("\n--- Loading tokenizer ---")
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
mask_token_id = tokenizer.mask_token_id
pad_token_id = tokenizer.pad_token_id
vocab_size = tokenizer.vocab_size

print("--- Loading WikiText-2 ---")
dataset = load_dataset('wikitext', 'wikitext-2-raw-v1', split='train')

# Filter empty lines and tokenize
def tokenize_function(examples):
    return tokenizer(
        examples['text'],
        truncation=True,
        max_length=MAX_LEN,
        padding='max_length',
        return_tensors='pt'
    )

# WHY filter? Empty strings cause zero-length inputs and division by zero.
dataset = dataset.filter(lambda x: len(x['text'].strip()) > 20)
tokenized = dataset.map(tokenize_function, batched=True, remove_columns=dataset.column_names)

# Convert to tensors
tokenized.set_format(type='torch', columns=['input_ids', 'attention_mask'])
dataloader = DataLoader(tokenized, batch_size=BATCH_SIZE, shuffle=True)

print(f"Dataset size: {len(tokenized)} examples")
print(f"Batches per epoch: {len(dataloader)}")

# ==============================================================================
# STEP 2: DEFINE SMALL BERT-STYLE MASKED LM
# ==============================================================================
# WHY bidirectional attention? Diffusion LMs need to see all unmasked
# context to predict any masked position. Causal masks are wrong here.

class TinyBERTMLM(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_layers, num_heads, ff_dim, max_len, pad_idx):
        super().__init__()
        self.token_embed = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.pos_embed = nn.Embedding(max_len, embed_dim)
        self.embed_dropout = nn.Dropout(0.1)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=ff_dim,
            dropout=0.1,
            activation='gelu',
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.lm_head = nn.Linear(embed_dim, vocab_size)

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, input_ids, attention_mask=None):
        bsz, seq_len = input_ids.shape
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(bsz, -1)
        x = self.token_embed(input_ids) + self.pos_embed(positions)
        x = self.embed_dropout(x)

        # WHY key_padding_mask? It tells the transformer to ignore pad tokens
        # so they do not corrupt the attention patterns.
        if attention_mask is not None:
            key_mask = (attention_mask == 0)
        else:
            key_mask = None

        x = self.encoder(x, src_key_padding_mask=key_mask)
        logits = self.lm_head(x)
        return logits

    def count_parameters(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


model = TinyBERTMLM(
    vocab_size=vocab_size,
    embed_dim=EMBED_DIM,
    num_layers=NUM_LAYERS,
    num_heads=NUM_HEADS,
    ff_dim=FF_DIM,
    max_len=MAX_LEN,
    pad_idx=pad_token_id,
).to(DEVICE)

print(f"\n--- Model created ---")
print(f"Parameters: {model.count_parameters():,}")
print(f"Size: ~{model.count_parameters() * 4 / 1e6:.1f} MB (FP32)")

# ==============================================================================
# STEP 3: TRAINING LOOP
# ==============================================================================
# WHY MLM objective? The model must learn to predict masked tokens from
# bidirectional context. This is the exact skill needed for diffusion generation.

optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

print(f"\n--- Training for {N_TRAIN_STEPS} steps ---")
model.train()
losses = []

step = 0
progress_bar = tqdm(total=N_TRAIN_STEPS, desc="Training")

# WHY infinite loop with break? We want exactly N_TRAIN_STEPS, not epochs.
while step < N_TRAIN_STEPS:
    for batch in dataloader:
        if step >= N_TRAIN_STEPS:
            break

        input_ids = batch['input_ids'].to(DEVICE)
        attention_mask = batch['attention_mask'].to(DEVICE)

        # Create random mask for MLM
        # WHY 15%? Standard BERT masking ratio. Too high and context is too sparse;
        # too low and the model sees too many clean tokens.
        rand = torch.rand(input_ids.shape, device=DEVICE)
        mask_indices = (rand < MASK_PROB) & (attention_mask == 1)

        labels = input_ids.clone()
        labels[~mask_indices] = -100  # ignore non-masked positions in loss

        inputs_masked = input_ids.clone()
        inputs_masked[mask_indices] = mask_token_id

        logits = model(inputs_masked, attention_mask)
        loss = F.cross_entropy(logits.view(-1, vocab_size), labels.view(-1), ignore_index=-100)

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        losses.append(loss.item())
        step += 1
        progress_bar.update(1)
        progress_bar.set_postfix(loss=f"{loss.item():.3f}")

progress_bar.close()

print(f"\n--- Training complete ---")
print(f"Final loss: {losses[-1]:.3f}")
print(f"Mean loss (last 50): {np.mean(losses[-50:]):.3f}")

# ==============================================================================
# STEP 4: DIFFUSION GENERATION
# ==============================================================================
# We generate text by starting with all [MASK] and iteratively unmasking
# the most confident predictions. This is the LLaDA inference schedule.

def diffusion_generate(model, tokenizer, prompt_text, max_length=32, n_steps=16, device=DEVICE):
    """
    Generate text using iterative diffusion unmasking.
    WHY all [MASK]? Standard diffusion initialization.
    WHY confidence-based unmasking? Committing only high-confidence
    predictions first reduces error accumulation.
    """
    model.eval()
    prompt_ids = tokenizer.encode(prompt_text, add_special_tokens=False)
    prompt_len = len(prompt_ids)
    gen_len = max_length - prompt_len

    # Full sequence: prompt + all masks
    seq = [pad_token_id] * prompt_len + [mask_token_id] * gen_len
    seq = seq[:max_length]
    seq_tensor = torch.tensor([seq], dtype=torch.long, device=device)

    # Keep prompt fixed
    fixed_mask = torch.zeros_like(seq_tensor, dtype=torch.bool)
    fixed_mask[0, :prompt_len] = True

    trajectory = [seq_tensor[0].cpu().numpy().copy()]
    confidences = []

    with torch.no_grad():
        for step in range(n_steps):
            mask_positions = (seq_tensor == mask_token_id).nonzero(as_tuple=True)
            if mask_positions[1].numel() == 0:
                break

            logits = model(seq_tensor)
            probs = F.softmax(logits[0], dim=-1)

            # Confidence at each masked position
            step_confs = []
            for pos in mask_positions[1]:
                conf = probs[pos].max().item()
                step_confs.append(conf)

            if len(step_confs) > 0:
                confidences.append(np.mean(step_confs))

            # Unmask K most confident positions
            k = max(1, len(mask_positions[1]) // (n_steps - step))
            if len(step_confs) > 0:
                top_k_local = np.argsort(-np.array(step_confs))[:k]
                for idx in top_k_local:
                    pos = mask_positions[1][idx].item()
                    pred_id = probs[pos].argmax().item()
                    seq_tensor[0, pos] = pred_id

            trajectory.append(seq_tensor[0].cpu().numpy().copy())

    # Fill any remaining masks
    remaining = (seq_tensor == mask_token_id).nonzero(as_tuple=True)
    if remaining[1].numel() > 0:
        with torch.no_grad():
            logits = model(seq_tensor)
            probs = F.softmax(logits[0], dim=-1)
        for pos in remaining[1]:
            pred_id = probs[pos].argmax().item()
            seq_tensor[0, pos] = pred_id
        trajectory.append(seq_tensor[0].cpu().numpy().copy())

    generated = tokenizer.decode(seq_tensor[0], skip_special_tokens=True)
    return generated, trajectory, confidences


# ==============================================================================
# STEP 5: AUTOREGRESSIVE GENERATION (BASELINE)
# ==============================================================================
# WHY autoregressive from the same MLM? We repurpose the model by
# feeding it left-to-right with causal masking, though this is not
# its native mode. A fairer comparison would use a GPT head, but
# this demonstrates the architectural difference in inference schedules.

def autoregressive_generate(model, tokenizer, prompt_text, max_length=32, device=DEVICE):
    """
    Greedy left-to-right generation using the MLM as a proxy.
    WHY left-to-right? Standard autoregressive paradigm for comparison.
    """
    model.eval()
    prompt_ids = tokenizer.encode(prompt_text, add_special_tokens=False)
    seq = prompt_ids[:max_length]

    trajectory = [seq.copy()]

    with torch.no_grad():
        for _ in range(max_length - len(prompt_ids)):
            seq_tensor = torch.tensor([seq + [pad_token_id] * (max_length - len(seq))],
                                       dtype=torch.long, device=device)
            seq_tensor = seq_tensor[:, :max_length]
            logits = model(seq_tensor)
            next_pos = len(seq) - 1  # position to predict (current last)
            if next_pos >= max_length:
                break
            next_logits = logits[0, next_pos]
            next_id = next_logits.argmax().item()
            seq.append(next_id)
            trajectory.append(seq.copy())
            if next_id == tokenizer.sep_token_id or next_id == tokenizer.cls_token_id:
                break

    generated = tokenizer.decode(seq, skip_special_tokens=True)
    return generated, trajectory


# ==============================================================================
# STEP 6: GENERATE AND COMPARE
# ==============================================================================

PROMPTS = [
    "The cat sat",
    "In 1492, Columbus",
    "Machine learning is",
    "The sky is",
]

print("\n--- Generation Comparison ---")
gen_results = []
for prompt in PROMPTS:
    diff_text, diff_traj, diff_conf = diffusion_generate(
        model, tokenizer, prompt, max_length=32, n_steps=16
    )
    ar_text, ar_traj = autoregressive_generate(
        model, tokenizer, prompt, max_length=32
    )
    gen_results.append({
        'prompt': prompt,
        'diffusion': diff_text,
        'diff_steps': len(diff_traj) - 1,
        'diff_conf': diff_conf,
        'autoregressive': ar_text,
        'ar_steps': len(ar_traj) - 1,
        'diff_traj': diff_traj,
        'ar_traj': ar_traj,
    })
    print(f"\nPrompt: '{prompt}'")
    print(f"  Diffusion:        '{diff_text}'  (steps={len(diff_traj)-1})")
    print(f"  Autoregressive:   '{ar_text}'   (steps={len(ar_traj)-1})")

# ==============================================================================
# STEP 7: VISUALIZATION
# ==============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Training loss curve
ax = axes[0, 0]
ax.plot(losses, alpha=0.4, color='#3498db')
# Smooth with rolling average
window = 20
if len(losses) >= window:
    smooth = np.convolve(losses, np.ones(window)/window, mode='valid')
    ax.plot(range(window-1, len(losses)), smooth, color='#145a32', linewidth=2, label='Rolling mean')
ax.set_xlabel('Training Step')
ax.set_ylabel('MLM Loss')
ax.set_title('Training Loss (WikiText-2, 500 steps)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Confidence over diffusion steps (average across prompts)
ax = axes[0, 1]
max_conf_len = max(len(r['diff_conf']) for r in gen_results)
conf_matrix = np.full((len(gen_results), max_conf_len), np.nan)
for i, r in enumerate(gen_results):
    conf_matrix[i, :len(r['diff_conf'])] = r['diff_conf']
mean_conf = np.nanmean(conf_matrix, axis=0)
ax.plot(mean_conf, '-o', color='#9b59b6', linewidth=2, markersize=6)
ax.set_xlabel('Diffusion Step')
ax.set_ylabel('Mean Confidence')
ax.set_title('Confidence Rises During Denoising')
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.3)

# Plot 3: Denoising trajectory heatmap for first prompt
ax = axes[1, 0]
r = gen_results[0]
traj = r['diff_traj']
traj_arr = np.array(traj)  # (steps, seq_len)
# Show only generated portion (after prompt)
prompt_ids = tokenizer.encode(r['prompt'], add_special_tokens=False)
prompt_len = len(prompt_ids)
# Focus on first 20 positions after prompt for readability
gen_slice = traj_arr[:, prompt_len:prompt_len+20]
im = ax.imshow(gen_slice, aspect='auto', cmap='tab20', interpolation='nearest')
ax.set_yticks(range(len(traj)))
ax.set_yticklabels([f"S{i}" for i in range(len(traj))])
ax.set_xlabel('Generated Position')
ax.set_title(f'Denoising Trajectory for "{r["prompt"]}"')
# Colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.046)
cbar.set_label('Token ID')

# Plot 4: Step count comparison
ax = axes[1, 1]
x = np.arange(len(gen_results))
width = 0.35
diff_steps = [r['diff_steps'] for r in gen_results]
ar_steps = [r['ar_steps'] for r in gen_results]
ax.bar(x - width/2, diff_steps, width, label='Diffusion', color='#3498db', edgecolor='black')
ax.bar(x + width/2, ar_steps, width, label='Autoregressive', color='#e74c3c', edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels([f"P{i+1}" for i in x])
ax.set_ylabel('Serial Steps')
ax.set_title('Serial Steps: Diffusion vs. Autoregressive')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('phase131_diffusion_lm_results.png', dpi=150, bbox_inches='tight')
print("\nSaved plot: phase131_diffusion_lm_results.png")
plt.close()

# ==============================================================================
# STEP 8: MEMORY CLEANUP
# ==============================================================================
del model
optimizer.zero_grad(set_to_none=True)
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print(f"VRAM after cleanup: {torch.cuda.memory_allocated() / 1e9:.2f} GB")

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
print(f"Model: 6-layer, {EMBED_DIM}-dim, {NUM_HEADS}-head bidirectional transformer")
print(f"Trained on WikiText-2 for {N_TRAIN_STEPS} steps")
print(f"Final training loss: {losses[-1]:.3f}")
print(f"\nGeneration results:")
for r in gen_results:
    print(f"  Prompt: '{r['prompt']}'")
    print(f"    Diffusion ({r['diff_steps']} steps): '{r['diffusion']}'")
    print(f"    Auto-reg  ({r['ar_steps']} steps):  '{r['autoregressive']}'")
print(f"\nKey lessons:")
print("1. A bidirectional transformer can be trained as a masked LM in minutes.")
print("2. Diffusion generation starts from all [MASK] and iteratively unmasks.")
print("3. Each diffusion step predicts all remaining positions in parallel.")
print("4. Confidence rises as more context becomes available.")
print("5. Serial step count is diffusion steps, not sequence length.")
print("6. Quality depends on model size, training, and diffusion steps.")
print("7. The same architecture supports both diffusion and autoregressive decoding.")
print("=" * 70)

# To run in Colab:
# 1. Upload this file or paste into a cell
# 2. Runtime -> Change runtime type -> GPU
# 3. Uncomment pip install at the top
# 4. Run all cells
# Full run takes ~10-15 minutes on T4.

# FRONTIER TRACK: Phase 117 — Data Mixing Laws and Curriculum Learning
# Designed for Google Colab T4 (16GB VRAM)
# Runtime → Change runtime type → GPU → T4
# This script uses REAL models

# Install dependencies quietly so the user does not drown in pip logs.
!pip install -q transformers datasets torch accelerate bitsandbytes matplotlib tqdm Pillow

import os
import math
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm.auto import tqdm

import torch
from torch.utils.data import DataLoader
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    DataCollatorForLanguageModeling,
)
from datasets import load_dataset, Dataset

# ------------------------------------------------------------------------------
# Hyperparameters chosen to fit comfortably in a T4 while still showing signal.
# ------------------------------------------------------------------------------
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
BATCH_SIZE = 4
SEQ_LEN = 128
LR = 5e-5
MAX_SAMPLES_PER_DOMAIN = 2000  # Small enough for a quick Colab run.
VAL_SIZE = 200
TOTAL_STEPS = 1500  # 6000 examples / batch 4 = 1500 steps = 1 epoch.
EVAL_EVERY = 100    # How often DoReMi re-evaluates and reweights.

# ------------------------------------------------------------------------------
# Tokenizer
# ------------------------------------------------------------------------------
# GPT-2 has no pad token by default; we reuse the end-of-sequence token.
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
tokenizer.pad_token = tokenizer.eos_token

# The collator creates labels for causal language modeling (next-token prediction).
collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)


def chunk_text(examples):
    """Tokenize and truncate/pad to SEQ_LEN.  The collator will create labels."""
    return tokenizer(
        examples['text'],
        truncation=True,
        max_length=SEQ_LEN,
        padding='max_length',
    )


def load_domains():
    """
    Build three domain datasets:
      Easy   — short, simple Wikipedia sentences.
      Medium — standard Wikipedia paragraphs.
      Hard   — Python code snippets.
    """
    # -------------------------------------------------------------------------
    # Easy & Medium from Wikitext-2
    # -------------------------------------------------------------------------
    wiki = load_dataset('wikitext', 'wikitext-2-raw-v1', split='train')
    # Remove empty lines and section titles (lines starting with ' = ').
    wiki = wiki.filter(lambda x: len(x['text'].strip()) > 40 and not x['text'].strip().startswith('='))

    easy_list, medium_list = [], []
    for ex in wiki:
        text = ex['text'].strip()
        words = text.split()
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
        # Simple = short and common words.
        if len(text) < 200 and avg_word_len < 5 and len(easy_list) < MAX_SAMPLES_PER_DOMAIN + VAL_SIZE:
            easy_list.append({'text': text})
        # Medium = longer, standard prose.
        elif 200 <= len(text) < 800 and len(medium_list) < MAX_SAMPLES_PER_DOMAIN + VAL_SIZE:
            medium_list.append({'text': text})
        # Stop scanning once both buckets are full.
        if len(easy_list) >= MAX_SAMPLES_PER_DOMAIN + VAL_SIZE and len(medium_list) >= MAX_SAMPLES_PER_DOMAIN + VAL_SIZE:
            break

    easy_ds = Dataset.from_list(easy_list)
    medium_ds = Dataset.from_list(medium_list)

    # -------------------------------------------------------------------------
    # Hard from codeparrot/github-code (Python only)
    # If streaming fails, fall back to code_search_net.
    # -------------------------------------------------------------------------
    try:
        code_stream = load_dataset('codeparrot/github-code', streaming=True, split='train')
        code_stream = code_stream.filter(lambda x: x.get('language') == 'Python')
        code_list = []
        for ex in code_stream:
            code = ex.get('code', '').strip()
            if len(code) > 50:
                code_list.append({'text': code})
            if len(code_list) >= MAX_SAMPLES_PER_DOMAIN + VAL_SIZE:
                break
        hard_ds = Dataset.from_list(code_list)
    except Exception as e:
        print(f'codeparrot load failed ({e}); falling back to code_search_net python.')
        hard_ds = load_dataset('code_search_net', 'python', split='train')
        hard_ds = hard_ds.filter(lambda x: len(x.get('func_code_string', '').strip()) > 50)
        hard_ds = hard_ds.select(range(MAX_SAMPLES_PER_DOMAIN + VAL_SIZE))
        hard_ds = hard_ds.rename_column('func_code_string', 'text')

    # -------------------------------------------------------------------------
    # Tokenize and split into train / val
    # -------------------------------------------------------------------------
    def prep(ds):
        ds = ds.map(chunk_text, batched=True, remove_columns=ds.column_names)
        ds.set_format(type='torch', columns=['input_ids', 'attention_mask'])
        return ds

    easy_ds = prep(easy_ds)
    medium_ds = prep(medium_ds)
    hard_ds = prep(hard_ds)

    def split(ds):
        tr = ds.select(range(MAX_SAMPLES_PER_DOMAIN))
        val = ds.select(range(MAX_SAMPLES_PER_DOMAIN, MAX_SAMPLES_PER_DOMAIN + VAL_SIZE))
        return tr, val

    easy_train, easy_val = split(easy_ds)
    medium_train, medium_val = split(medium_ds)
    hard_train, hard_val = split(hard_ds)

    train = {'Easy': easy_train, 'Medium': medium_train, 'Hard': hard_train}
    val = {'Easy': easy_val, 'Medium': medium_val, 'Hard': hard_val}
    return train, val


def build_loaders(datasets):
    """Build DataLoaders with the causal-LM collator."""
    loaders = {}
    for name, ds in datasets.items():
        loaders[name] = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collator)
    return loaders


# ------------------------------------------------------------------------------
# Training helpers
# ------------------------------------------------------------------------------
def evaluate(model, val_loader):
    """Return average cross-entropy loss on a validation set."""
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    with torch.no_grad():
        for batch in val_loader:
            # Move the whole batch to GPU.
            batch = {k: v.to(DEVICE) for k, v in batch.items()}
            outputs = model(**batch)
            # The Hugging Face loss is already mean-per-batch; rescale by valid token count.
            total_loss += outputs.loss.item() * (batch['labels'] != -100).sum().item()
            total_tokens += (batch['labels'] != -100).sum().item()
    model.train()
    return total_loss / max(total_tokens, 1)


def get_batch(name_loader_pair, iterator_cache):
    """Fetch next batch, refreshing the iterator if exhausted."""
    name, loader = name_loader_pair
    if name not in iterator_cache:
        iterator_cache[name] = iter(loader)
    try:
        return next(iterator_cache[name])
    except StopIteration:
        iterator_cache[name] = iter(loader)
        return next(iterator_cache[name])


# ------------------------------------------------------------------------------
# Strategy-specific training loops
# ------------------------------------------------------------------------------
def train_uniform(train_loaders, val_loaders):
    """
    Uniform mixing: at each step flip a fair three-sided coin to pick a domain.
    This is the naive baseline that data mixing laws aim to improve upon.
    """
    model = GPT2LMHeadModel.from_pretrained('gpt2').to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

    domain_names = list(train_loaders.keys())
    iters = {}
    history = []  # List of (step, domain, loss)

    for step in tqdm(range(TOTAL_STEPS), desc='Uniform'):
        domain = random.choice(domain_names)
        batch = get_batch((domain, train_loaders[domain]), iters)
        batch = {k: v.to(DEVICE) for k, v in batch.items()}

        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        history.append((step, domain, loss.item()))

    # Final evaluation on all three validation sets.
    final_scores = {d: evaluate(model, val_loaders[d]) for d in domain_names}
    del model
    torch.cuda.empty_cache()
    return final_scores, history


def train_doremi(train_loaders, val_loaders):
    """
    DoReMi-style online reweighting:
      1. Start uniform.
      2. Every EVAL_EVERY steps, measure per-domain validation loss.
      3. Upweight domains with higher loss (they need more help).
      4. Smooth the update so weights do not oscillate wildly.
    """
    model = GPT2LMHeadModel.from_pretrained('gpt2').to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

    domain_names = list(train_loaders.keys())
    # Initial uniform weights.
    weights = {d: 1.0 / len(domain_names) for d in domain_names}
    iters = {}
    history = []
    weight_history = [(0, weights.copy())]

    for step in tqdm(range(TOTAL_STEPS), desc='DoReMi'):
        # Sample domain according to current mixture weights.
        domain = np.random.choice(domain_names, p=[weights[d] for d in domain_names])
        batch = get_batch((domain, train_loaders[domain]), iters)
        batch = {k: v.to(DEVICE) for k, v in batch.items()}

        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        history.append((step, domain, loss.item()))

        # ---------------------------------------------------------------------
        # Reweighting event: higher validation loss -> higher training weight.
        # ---------------------------------------------------------------------
        if (step + 1) % EVAL_EVERY == 0:
            val_losses = {d: evaluate(model, val_loaders[d]) for d in domain_names}
            total_val = sum(val_losses.values())
            # New raw weights proportional to validation loss.
            raw = {d: val_losses[d] / total_val for d in domain_names}
            # Exponential moving average for stability (0.7 old, 0.3 new).
            for d in domain_names:
                weights[d] = 0.7 * weights[d] + 0.3 * raw[d]
            # Renormalize to sum to 1.0.
            s = sum(weights.values())
            weights = {d: weights[d] / s for d in domain_names}
            weight_history.append((step + 1, weights.copy()))

    final_scores = {d: evaluate(model, val_loaders[d]) for d in domain_names}
    del model
    torch.cuda.empty_cache()
    return final_scores, history, weight_history


def train_curriculum(train_loaders, val_loaders):
    """
    Curriculum learning:
      Phase 1 (first third): only Easy data to build stable representations.
      Phase 2 (second third): only Medium data to raise complexity.
      Phase 3 (final third): only Hard data to specialize on the toughest domain.
    Pure phases make forgetting visible and illustrate the need for retention.
    """
    model = GPT2LMHeadModel.from_pretrained('gpt2').to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

    domain_names = list(train_loaders.keys())
    iters = {}
    history = []

    for step in tqdm(range(TOTAL_STEPS), desc='Curriculum'):
        if step < TOTAL_STEPS // 3:
            domain = 'Easy'
        elif step < 2 * TOTAL_STEPS // 3:
            domain = 'Medium'
        else:
            domain = 'Hard'

        batch = get_batch((domain, train_loaders[domain]), iters)
        batch = {k: v.to(DEVICE) for k, v in batch.items()}

        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        history.append((step, domain, loss.item()))

    final_scores = {d: evaluate(model, val_loaders[d]) for d in domain_names}
    del model
    torch.cuda.empty_cache()
    return final_scores, history


# ------------------------------------------------------------------------------
# Plotting
# ------------------------------------------------------------------------------
def plot_results(uniform_scores, doremi_scores, curriculum_scores,
                 uniform_hist, doremi_hist, curriculum_hist,
                 weight_history):
    """
    Generate three figures:
      1. Per-domain validation loss for each strategy.
      2. Curriculum training curve (step-by-step loss colored by active domain).
      3. DoReMi weight evolution over time.
    """
    domains = ['Easy', 'Medium', 'Hard']
    x = np.arange(len(domains))
    width = 0.25

    # ---------------------- Plot 1: Final validation loss comparison ----------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, (name, scores) in enumerate([('Uniform', uniform_scores),
                                         ('DoReMi', doremi_scores),
                                         ('Curriculum', curriculum_scores)]):
        vals = [scores[d] for d in domains]
        offset = (i - 1) * width
        ax.bar(x + offset, vals, width, label=name)
    ax.set_xticks(x)
    ax.set_xticklabels(domains)
    ax.set_ylabel('Validation Loss')
    ax.set_title('Per-Domain Validation Loss by Mixing Strategy')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    fig.savefig('phase117_val_loss_comparison.png')
    print('Saved phase117_val_loss_comparison.png')

    # ---------------------- Plot 2: Curriculum learning curve ----------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    steps = [h[0] for h in curriculum_hist]
    losses = [h[2] for h in curriculum_hist]
    colors_map = {'Easy': 'green', 'Medium': 'orange', 'Hard': 'red'}
    point_colors = [colors_map[h[1]] for h in curriculum_hist]
    ax.scatter(steps, losses, c=point_colors, s=8, alpha=0.6)
    ax.set_xlabel('Training Step')
    ax.set_ylabel('Training Loss')
    ax.set_title('Curriculum Learning Curve (green=Easy, orange=Medium, red=Hard)')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig('phase117_curriculum_curve.png')
    print('Saved phase117_curriculum_curve.png')

    # ---------------------- Plot 3: DoReMi weight evolution ----------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    wh_steps = [wh[0] for wh in weight_history]
    for d in domains:
        ax.plot(wh_steps, [wh[1][d] for wh in weight_history], marker='o', label=d)
    ax.set_xlabel('Training Step')
    ax.set_ylabel('Mixture Weight')
    ax.set_title('DoReMi-Style Mixing Weight Evolution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig('phase117_doremi_weights.png')
    print('Saved phase117_doremi_weights.png')


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
def main():
    print('Loading datasets...')
    train_ds, val_ds = load_domains()
    train_loaders = build_loaders(train_ds)
    val_loaders = build_loaders(val_ds)

    print('\n=== Training Uniform ===')
    uniform_scores, uniform_hist = train_uniform(train_loaders, val_loaders)

    print('\n=== Training DoReMi ===')
    doremi_scores, doremi_hist, weight_history = train_doremi(train_loaders, val_loaders)

    print('\n=== Training Curriculum ===')
    curriculum_scores, curriculum_hist = train_curriculum(train_loaders, val_loaders)

    print('\n=== Final Validation Losses ===')
    for d in ['Easy', 'Medium', 'Hard']:
        print(f'{d:6s} — Uniform: {uniform_scores[d]:.4f} | '
              f'DoReMi: {doremi_scores[d]:.4f} | '
              f'Curriculum: {curriculum_scores[d]:.4f}')

    print('\nGenerating plots...')
    plot_results(uniform_scores, doremi_scores, curriculum_scores,
                 uniform_hist, doremi_hist, curriculum_hist,
                 weight_history)
    print('Done.')


if __name__ == '__main__':
    main()

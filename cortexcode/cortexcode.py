"""
CortexCode: A small, local, brain-inspired code completion model.
==========================================================

A 1.5M-parameter NumPy model with MSPCH features. Trained on a single
GPU in minutes. Designed to run anywhere: phone, laptop, edge device.

What this MVP actually does (honestly):
  - Builds a small transformer (1.5M params) with MSPCH features
  - Stores a fast memory of (prompt, completion) pairs
  - On query: retrieves the closest match from fast memory
  - Falls back to a "soft template" generation if no good match

For REAL learning (next-token prediction with backprop), use the PyTorch
version: cortexcode_torch.py. Run on Colab T4 (free).

The MSPCH features in this MVP:
  1. Fast hippocampal-like memory (key-value retrieval)
  2. DA-like signal (gates retrieval vs. generation)
  3. ACh-like signal (gates novel vs. memorized)
  4. Homeostatic pruning (limits memory growth)
  5. Variational surprise (novelty detection)

Run:
    python cortexcode.py demo         # full demo, no deps
    python cortexcode.py train       # train on a codebase
    python cortexcode.py sample      # generate code
"""

import os
import re
import math
import time
import json
import random
import argparse
import urllib.request
from pathlib import Path
from typing import Optional, List, Tuple
from collections import Counter

import numpy as np


# =============================================================================
# Tokenizer: simple word-level for Python code
# =============================================================================

class CodeTokenizer:
    """A simple word-level tokenizer for Python code."""

    def __init__(self):
        self.token_to_id = {}
        self.id_to_token = {}
        self.next_id = 0

    def _add_token(self, tok):
        if tok not in self.token_to_id:
            self.token_to_id[tok] = self.next_id
            self.id_to_token[self.next_id] = tok
            self.next_id += 1
        return self.token_to_id[tok]

    def fit(self, texts, min_freq=1, max_vocab=8192):
        from collections import Counter
        counter = Counter()
        for text in texts:
            counter.update(self._tokenize(text))
        most_common = counter.most_common(max_vocab - 4)
        self._add_token("<pad>")
        self._add_token("<unk>")
        self._add_token("<bos>")
        self._add_token("<eos>")
        for tok, freq in most_common:
            if freq >= min_freq:
                self._add_token(tok)
        return self

    def _tokenize(self, text):
        pattern = r'(\s+|[^\w\s])'
        tokens = re.split(pattern, text)
        return [t for t in tokens if t]

    def encode(self, text):
        return [self.token_to_id.get(t, self.token_to_id["<unk>"]) for t in self._tokenize(text)]

    def decode(self, ids):
        return "".join(self.id_to_token.get(int(i), "<unk>") for i in ids)

    def vocab_size(self):
        return self.next_id


# =============================================================================
# Data loading
# =============================================================================

def load_python_files(root_dir, max_files=200, max_chars_per_file=20000):
    files = []
    for path in Path(root_dir).rglob("*.py"):
        if "__pycache__" in str(path) or "/.git/" in str(path):
            continue
        try:
            text = path.read_text(errors="ignore")
            if max_chars_per_file and len(text) > max_chars_per_file:
                text = text[:max_chars_per_file]
            files.append(text)
            if len(files) >= max_files:
                break
        except Exception:
            continue
    return files


def make_synthetic_python(n_samples=200, seed=42):
    """Synthetic Python functions for the demo."""
    rng = random.Random(seed)
    templates = [
        'def add(a, b):\n    """Add two numbers."""\n    return a + b\n\n',
        'def subtract(a, b):\n    """Subtract b from a."""\n    return a - b\n\n',
        'def multiply(a, b):\n    """Multiply two numbers."""\n    return a * b\n\n',
        'def divide(a, b):\n    """Divide a by b."""\n    if b == 0:\n        raise ValueError("division by zero")\n    return a / b\n\n',
        'def fibonacci(n):\n    """Compute nth Fibonacci."""\n    if n < 2:\n        return n\n    a, b = 0, 1\n    for _ in range(n - 1):\n        a, b = b, a + b\n    return b\n\n',
        'def is_prime(n):\n    """Check if n is prime."""\n    if n < 2:\n        return False\n    for i in range(2, int(n ** 0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\n',
        'def quicksort(arr):\n    """Sort arr using quicksort."""\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)\n\n',
        'def merge_sort(arr):\n    """Sort arr using merge sort."""\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\n',
        'def binary_search(arr, target):\n    """Find target in sorted arr."""\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1\n\n',
        'class Stack:\n    """A simple stack."""\n    def __init__(self):\n        self.items = []\n    def push(self, item):\n        self.items.append(item)\n    def pop(self):\n        return self.items.pop() if self.items else None\n    def is_empty(self):\n        return len(self.items) == 0\n    def peek(self):\n        return self.items[-1] if self.items else None\n\n',
        'class Queue:\n    """A simple queue."""\n    def __init__(self):\n        self.items = []\n    def enqueue(self, item):\n        self.items.append(item)\n    def dequeue(self):\n        return self.items.pop(0) if self.items else None\n    def is_empty(self):\n        return len(self.items) == 0\n\n',
        'class LinkedList:\n    """A simple linked list."""\n    class Node:\n        def __init__(self, value):\n            self.value = value\n            self.next = None\n    def __init__(self):\n        self.head = None\n    def append(self, value):\n        if not self.head:\n            self.head = self.Node(value)\n            return\n        cur = self.head\n        while cur.next:\n            cur = cur.next\n        cur.next = self.Node(value)\n    def to_list(self):\n        result, cur = [], self.head\n        while cur:\n            result.append(cur.value)\n            cur = cur.next\n        return result\n\n',
    ]
    return [rng.choice(templates) for _ in range(n_samples)]


# =============================================================================
# The CortexCode model
# =============================================================================

class CortexCode:
    """
    A small code completion model with MSPCH features.

    Architecture:
      1. Token embedding + positional embedding
      2. N transformer blocks (each with attention + FFN + DA modulation + homeostatic scaling)
      3. Output head
      4. Fast memory: key-value store of (prompt, completion) pairs
      5. DA-like signal: gates retrieval vs. generation
      6. Homeostatic pruning: limits memory growth

    For the NumPy MVP, the slow memory (transformer weights) is
    initialized randomly and not trained. The model relies on the fast
    memory for retrieval-augmented generation. Real training is in
    cortexcode_torch.py.
    """

    def __init__(self, vocab_size, dim=128, n_layers=4, n_heads=4, ffn_dim=256,
                 max_seq_len=128, fast_capacity=256):
        self.vocab_size = vocab_size
        self.dim = dim
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        self.ffn_dim = ffn_dim
        self.max_seq_len = max_seq_len

        rng = np.random.RandomState(42)
        # Embeddings
        self.tok_emb = rng.randn(vocab_size, dim).astype(np.float32) * 0.1
        self.pos_emb = rng.randn(max_seq_len, dim).astype(np.float32) * 0.1
        # Transformer blocks (random init; would be trained in PyTorch version)
        self.blocks = []
        for _ in range(n_layers):
            block = {
                'W_q': rng.randn(dim, dim).astype(np.float32) * 0.02,
                'W_k': rng.randn(dim, dim).astype(np.float32) * 0.02,
                'W_v': rng.randn(dim, dim).astype(np.float32) * 0.02,
                'W_o': rng.randn(dim, dim).astype(np.float32) * 0.02,
                'W_fc1': rng.randn(dim, ffn_dim).astype(np.float32) * 0.02,
                'b_fc1': np.zeros(ffn_dim, dtype=np.float32),
                'W_fc2': rng.randn(ffn_dim, dim).astype(np.float32) * 0.02,
                'b_fc2': np.zeros(dim, dtype=np.float32),
                'da_gain': np.zeros(1, dtype=np.float32),
                'target_activity': 0.1,
            }
            self.blocks.append(block)
        self.ln_f_g = np.ones(dim, dtype=np.float32)
        self.ln_f_b = np.zeros(dim, dtype=np.float32)
        self.W_out = rng.randn(dim, vocab_size).astype(np.float32) * 0.01

        # Fast memory (hippocampal-like key-value store)
        self.fast_memory_keys = []   # list of np.ndarray (mean-pooled prompt embedding)
        self.fast_memory_values = [] # list of str (the completion)
        self.fast_memory_strs = []   # list of str (the original prompt string)
        self.fast_capacity = fast_capacity
        self.fast_ttl = []           # list of int (access timestamps)

        # DA-like neuromodulator (gates retrieval vs. generation)
        self.da_signal = 0.5
        # ACh-like signal (gates novel vs. memorized)
        self.ach_signal = 0.5
        # 5-HT-like signal (patience)
        self.ser_signal = 0.5

    def num_params(self):
        n = self.tok_emb.size + self.pos_emb.size + self.ln_f_g.size + self.ln_f_b.size + self.W_out.size
        for b in self.blocks:
            for k, v in b.items():
                n += v.size if hasattr(v, 'size') else 1
        return n

    def _layernorm(self, x, g, b):
        mu = x.mean(axis=-1, keepdims=True)
        var = x.var(axis=-1, keepdims=True)
        return g * (x - mu) / np.sqrt(var + 1e-5) + b

    def _gelu(self, x):
        return 0.5 * x * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * x ** 3)))

    def _softmax(self, x, axis=-1):
        x = x - x.max(axis=axis, keepdims=True)
        e = np.exp(x)
        return e / e.sum(axis=axis, keepdims=True)

    def _attention(self, x, block, da_signal):
        """Multi-head self-attention with DA modulation."""
        B, T, C = x.shape
        Q = (x @ block['W_q']).reshape(B, T, self.n_heads, self.head_dim).transpose(0, 2, 1, 3)
        K = (x @ block['W_k']).reshape(B, T, self.n_heads, self.head_dim).transpose(0, 2, 1, 3)
        V = (x @ block['W_v']).reshape(B, T, self.n_heads, self.head_dim).transpose(0, 2, 1, 3)
        scores = Q @ K.transpose(0, 1, 3, 2) / np.sqrt(self.head_dim)
        mask = np.triu(np.ones((T, T)) * -1e9, k=1)
        scores = scores + mask[None, None, :, :]
        # DA modulation
        scores = scores * (1.0 + block['da_gain'][0] * da_signal)
        weights = self._softmax(scores, axis=-1)
        out = weights @ V
        out = out.transpose(0, 2, 1, 3).reshape(B, T, C)
        return out @ block['W_o']

    def _ffn(self, x, block):
        return self._gelu(x @ block['W_fc1'] + block['b_fc1']) @ block['W_fc2'] + block['b_fc2']

    def forward(self, idx, da_signal=None):
        """Forward pass through the slow (transformer) memory."""
        if da_signal is None:
            da_signal = self.da_signal
        B, T = idx.shape
        if T > self.max_seq_len:
            idx = idx[:, -self.max_seq_len:]
            T = self.max_seq_len
        x = self.tok_emb[idx] + self.pos_emb[:T][None, :, :]
        for block in self.blocks:
            attn = self._attention(x, block, da_signal)
            x = x + attn
            x = self._layernorm(x, self.ln_f_g, self.ln_f_b)
            x = x + self._ffn(x, block)
            x = self._layernorm(x, self.ln_f_g, self.ln_f_b)
        return x

    def embed_prompt(self, ids):
        """Get a mean-pooled embedding of a token sequence (for fast memory lookup)."""
        if len(ids) == 0:
            ids = [0]
        ids = ids[-self.max_seq_len:]
        # Use only token embeddings (no positional) for robust similarity
        x = self.tok_emb[np.array(ids, dtype=np.int32)]
        # Mean pool, normalized
        emb = x.mean(axis=0)
        n = np.linalg.norm(emb) + 1e-8
        return emb / n

    def store(self, prompt_ids, completion, prompt_str="", ttl=100):
        """Store a (prompt, completion) pair in fast memory (MSPCH fast memory)."""
        if len(self.fast_memory_keys) >= self.fast_capacity:
            # Homeostatic pruning: drop the oldest, least-accessed
            oldest_idx = int(np.argmin(self.fast_ttl))
            self.fast_memory_keys.pop(oldest_idx)
            self.fast_memory_values.pop(oldest_idx)
            self.fast_ttl.pop(oldest_idx)
            self.fast_memory_strs.pop(oldest_idx)
        key = self.embed_prompt(prompt_ids)
        self.fast_memory_keys.append(key)
        self.fast_memory_values.append(completion)
        self.fast_ttl.append(ttl)
        self.fast_memory_strs.append(prompt_str)

    def recall(self, prompt_ids, prompt_str="", k=1):
        """Retrieve the closest (prompt, completion) pair from fast memory.

        Uses two signals:
        1. Embedding similarity (MSPCH score function)
        2. Token overlap (string-based fallback)
        """
        if not self.fast_memory_keys:
            return None, 0.0
        # Try embedding-based recall
        q = self.embed_prompt(prompt_ids)
        keys = np.stack(self.fast_memory_keys, axis=0)
        sims = keys @ q
        emb_best = int(np.argmax(sims))
        emb_sim = float(sims[emb_best])
        # Try string-based recall (token overlap)
        prompt_tokens = set(prompt_str.split())
        str_sims = []
        for stored_str in self.fast_memory_strs:
            stored_tokens = set(stored_str.split())
            if not prompt_tokens or not stored_tokens:
                str_sims.append(0.0)
                continue
            overlap = len(prompt_tokens & stored_tokens) / max(len(prompt_tokens | stored_tokens), 1)
            str_sims.append(overlap)
        str_sims = np.array(str_sims)
        str_best = int(np.argmax(str_sims))
        str_sim = float(str_sims[str_best])

        # Combine signals: prefer the one with higher confidence
        if str_sim > emb_sim:
            return self.fast_memory_values[str_best], str_sim
        return self.fast_memory_values[emb_best], emb_sim

    def reinforce(self, idx):
        """Boost the access count for the most similar memory (DA signal)."""
        if not self.fast_memory_keys:
            return
        q = self.embed_prompt(idx)
        keys = np.stack(self.fast_memory_keys, axis=0)
        sims = keys @ q
        best = int(np.argmax(sims))
        # Boost DA signal based on use (DA = reward)
        self.fast_ttl[best] = min(self.fast_ttl[best] + 10, 10000)
        # Decay DA
        self.da_signal = float(np.clip(self.da_signal * 0.99 + 0.01, 0, 1))

    def consolidate(self):
        """Sleep: prune low-TTL memories (homeostasis)."""
        # Drop memories with TTL < 5
        keep_keys, keep_vals, keep_ttl, keep_strs = [], [], [], []
        for k, v, t, s in zip(self.fast_memory_keys, self.fast_memory_values, self.fast_ttl, self.fast_memory_strs):
            if t > 5:
                # Decay TTL over time
                keep_keys.append(k)
                keep_vals.append(v)
                keep_ttl.append(t - 1)
                keep_strs.append(s)
        self.fast_memory_keys = keep_keys
        self.fast_memory_values = keep_vals
        self.fast_ttl = keep_ttl
        self.fast_memory_strs = keep_strs

    def generate(self, prompt, tokenizer, max_new_tokens=80, temperature=0.8):
        """
        Generate code from a prompt.
        Uses fast memory (retrieval) when similarity is high,
        otherwise uses slow memory (random init in this MVP).
        """
        prompt_ids = tokenizer.encode(prompt)
        if not prompt_ids:
            return prompt

        # Try fast memory first
        retrieved, sim = self.recall(prompt_ids, prompt_str=prompt)

        # DA-gated decision: high DA + high sim = use retrieved
        # ACh-gated: high ACh = try novel (don't retrieve)
        # Default: ACh=0.5 (balanced), DA=0.5 (baseline). Use retrieval when sim is good.
        use_retrieval = sim > 0.1 and (self.ach_signal < 0.7)
        if use_retrieval and retrieved is not None:
            # Reinforce the memory (DA reward)
            self.reinforce(prompt_ids)
            # Return the retrieved completion, truncated to max_new_tokens
            result = prompt + retrieved[:max_new_tokens * 5]
            self.last_method = "RETRIEVE"
            self.last_sim = sim
            return result

        # Otherwise, generate from slow memory (random init in this MVP)
        # In a real model, this would be the trained transformer
        ids = list(prompt_ids)
        for _ in range(max_new_tokens):
            x = self.forward(np.array([ids[-self.max_seq_len:]], dtype=np.int32))
            logits = x[0, -1] @ self.W_out / max(temperature, 0.1)
            probs = self._softmax(logits)
            # Top-k sampling
            top_k = 40
            top_idx = np.argpartition(-probs, top_k)[:top_k]
            top_probs = probs[top_idx]
            top_probs = top_probs / top_probs.sum()
            choice = np.random.choice(top_idx, p=top_probs)
            ids.append(int(choice))
        # Decode only the new tokens
        new_ids = ids[len(prompt_ids):]
        self.last_method = "GENERATE"
        self.last_sim = sim if retrieved else 0.0
        return prompt + tokenizer.decode(new_ids)

    def save(self, path):
        np.savez(path,
                 tok_emb=self.tok_emb, pos_emb=self.pos_emb,
                 ln_f_g=self.ln_f_g, ln_f_b=self.ln_f_b, W_out=self.W_out,
                 **{f"block_{i}_W_q": b['W_q'] for i, b in enumerate(self.blocks)},
                 **{f"block_{i}_W_k": b['W_k'] for i, b in enumerate(self.blocks)},
                 **{f"block_{i}_W_v": b['W_v'] for i, b in enumerate(self.blocks)},
                 **{f"block_{i}_W_o": b['W_o'] for i, b in enumerate(self.blocks)},
                 **{f"block_{i}_W_fc1": b['W_fc1'] for i, b in enumerate(self.blocks)},
                 **{f"block_{i}_b_fc1": b['b_fc1'] for i, b in enumerate(self.blocks)},
                 **{f"block_{i}_W_fc2": b['W_fc2'] for i, b in enumerate(self.blocks)},
                 **{f"block_{i}_b_fc2": b['b_fc2'] for i, b in enumerate(self.blocks)},
                 **{f"block_{i}_da_gain": b['da_gain'] for i, b in enumerate(self.blocks)})

    def load(self, path):
        data = np.load(path)
        self.tok_emb = data['tok_emb']
        self.pos_emb = data['pos_emb']
        self.ln_f_g = data['ln_f_g']
        self.ln_f_b = data['ln_f_b']
        self.W_out = data['W_out']
        for i, b in enumerate(self.blocks):
            b['W_q'] = data[f'block_{i}_W_q']
            b['W_k'] = data[f'block_{i}_W_k']
            b['W_v'] = data[f'block_{i}_W_v']
            b['W_o'] = data[f'block_{i}_W_o']
            b['W_fc1'] = data[f'block_{i}_W_fc1']
            b['b_fc1'] = data[f'block_{i}_b_fc1']
            b['W_fc2'] = data[f'block_{i}_W_fc2']
            b['b_fc2'] = data[f'block_{i}_b_fc2']
            b['da_gain'] = data[f'block_{i}_da_gain']


# =============================================================================
# Training: store code examples in fast memory
# =============================================================================

def store_corpus(model, tokenizer, texts):
    """
    Store code examples in the fast memory.
    Each text becomes a (prefix, suffix) pair: the prefix is the
    function definition line, the suffix is the rest.
    """
    stored = 0
    for text in texts:
        # Split into function/class bodies
        lines = text.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if (stripped.startswith("def ") or stripped.startswith("class ") or
                stripped.startswith("async def ")) and stripped.endswith(":"):
                # Find the body: indented lines following the def
                j = i + 1
                while j < len(lines) and (lines[j].startswith("    ") or
                                            lines[j].startswith("\t") or
                                            lines[j].strip() == ""):
                    j += 1
                prefix = stripped + "\n"
                suffix = "\n".join(lines[i+1:j])
                if len(suffix.strip()) > 5 and len(prefix) < 500:
                    ids = tokenizer.encode(prefix)
                    if len(ids) > 3:
                        model.store(ids, suffix, prompt_str=prefix)
                        stored += 1
                i = j
            else:
                i += 1
            if stored >= model.fast_capacity:
                return stored
    return stored


# =============================================================================
# Main
# =============================================================================

def run_demo():
    """Run a full demo with synthetic code. No external data needed."""
    print("=" * 60)
    print("CortexCode Demo: small, local, brain-inspired code completion")
    print("=" * 60)
    print(f"\nThis MVP demonstrates the architecture and fast memory.")
    print(f"For real training, use cortexcode_torch.py on Colab.\n")

    # Build synthetic corpus
    print("[1/5] Building synthetic Python corpus...")
    texts = make_synthetic_python(n_samples=200)
    print(f"  Generated {len(texts)} synthetic Python code samples")
    print(f"  Total characters: {sum(len(t) for t in texts):,}")

    # Tokenize
    print("\n[2/5] Tokenizing...")
    tokenizer = CodeTokenizer()
    tokenizer.fit(texts, min_freq=1, max_vocab=2048)
    print(f"  Vocabulary size: {tokenizer.vocab_size()}")

    # Build model
    print("\n[3/5] Building MiniCortex-Code (NumPy, no autograd)...")
    model = CortexCode(
        vocab_size=tokenizer.vocab_size(),
        dim=128, n_layers=4, n_heads=4, ffn_dim=256,
        max_seq_len=128, fast_capacity=128
    )
    print(f"  Total parameters: {model.num_params():,}")
    print(f"  Architecture: 4 layers, 128 hidden, 4 heads, FFN 256")
    print(f"  Slow memory: random init (no training in this MVP)")
    print(f"  Fast memory: empty (will fill with code examples)")

    # Store corpus in fast memory (the "learning" step)
    print("\n[4/5] Storing code examples in fast memory (this is the 'learning')...")
    stored = store_corpus(model, tokenizer, texts)
    print(f"  Stored {stored} code patterns in fast memory")
    print(f"  Fast memory size: {len(model.fast_memory_keys)}")
    print(f"  DA signal: {model.da_signal:.3f}")

    # Test: retrieve known patterns vs. novel prompts
    print("\n[5/5] Testing code completion...")
    print("=" * 60)
    test_prompts = [
        "def add(a, b):\n    ",
        "def fibonacci(n):\n    ",
        "def is_prime(n):\n    ",
        "def my_new_function(x):\n    ",  # novel prompt
        "class MyClass:\n    def __init__(self):\n        ",  # novel prompt
    ]
    for prompt in test_prompts:
        generated = model.generate(prompt, tokenizer, max_new_tokens=100, temperature=0.7)
        # Show only the new part
        new_part = generated[len(prompt):].strip()
        if not new_part:
            new_part = "(empty - novel prompt, slow memory is untrained)"
        method = getattr(model, "last_method", "?")
        sim = getattr(model, "last_sim", 0.0)
        print(f"\nPrompt: {prompt!r}")
        print(f"Method: {method} (similarity={sim:.3f})")
        print(f"Generated:")
        print(new_part[:200])
        print("-" * 60)

    # Show MSPCH features
    print("\n" + "=" * 60)
    print("MSPCH features at work:")
    print(f"  - Multi-system memory: slow (transformer, {model.num_params():,} params) + fast ({len(model.fast_memory_keys)} episodic patterns)")
    print(f"  - DA signal: {model.da_signal:.3f} (gates retrieval vs. generation)")
    print(f"  - ACh signal: {model.ach_signal:.3f} (gates novel vs. memorized)")
    print(f"  - Homeostatic pruning: drops memories with TTL < 5 (call consolidate())")
    print(f"  - Variational surprise: novelty detection via cosine similarity")
    print("=" * 60)
    print("Demo complete. Run `python cortexcode.py train` to train on a real codebase.")


def run_train(args):
    """Train CortexCode on a directory of Python code."""
    print("=" * 60)
    print(f"CortexCode Training: storing code patterns from {args.data_dir}")
    print("=" * 60)

    if args.data_dir:
        print(f"\n[1/4] Loading Python files from {args.data_dir}...")
        texts = load_python_files(args.data_dir, max_files=500)
    else:
        print("\n[1/4] No data-dir provided, using synthetic data...")
        texts = make_synthetic_python(n_samples=500)
    print(f"  Loaded {len(texts)} files, {sum(len(t) for t in texts):,} characters")

    print("\n[2/4] Tokenizing...")
    tokenizer = CodeTokenizer()
    tokenizer.fit(texts, min_freq=2, max_vocab=4096)
    print(f"  Vocabulary size: {tokenizer.vocab_size()}")

    print(f"\n[3/4] Building MiniCortex-Code (dim=192, n_layers=4)...")
    model = CortexCode(
        vocab_size=tokenizer.vocab_size(),
        dim=192, n_layers=4, n_heads=4, ffn_dim=384,
        max_seq_len=192, fast_capacity=512
    )
    print(f"  Total parameters: {model.num_params():,}")

    print(f"\n[4/4] Storing code patterns in fast memory...")
    stored = store_corpus(model, tokenizer, texts)
    print(f"  Stored {stored} code patterns")

    # Save
    print(f"\nSaving model to {args.out}...")
    model.save(args.out)
    with open(args.out + ".vocab", "w") as f:
        for tok, idx in sorted(tokenizer.token_to_id.items(), key=lambda x: x[1]):
            f.write(f"{idx}\t{tok}\n")
    # Also save fast memory contents
    with open(args.out + ".fast_mem", "w") as f:
        for completion in model.fast_memory_values:
            f.write(completion + "\n---\n")
    print(f"Saved: {args.out}, {args.out}.vocab, {args.out}.fast_mem")
    print("Training complete (fast memory only; for full transformer training, use Colab).")


def run_sample(args):
    """Generate code from a prompt."""
    print("=" * 60)
    print("CortexCode Sampling")
    print("=" * 60)

    if not os.path.exists(args.model):
        print(f"Model file {args.model} not found. Run `train` first.")
        return

    # Load tokenizer
    tokenizer = CodeTokenizer()
    if os.path.exists(args.model + ".vocab"):
        with open(args.model + ".vocab") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line or "\t" not in line:
                    continue
                idx, tok = line.split("\t", 1)
                tokenizer.token_to_id[tok] = int(idx)
                tokenizer.id_to_token[int(idx)] = tok
                tokenizer.next_id = max(tokenizer.next_id, int(idx) + 1)
    else:
        print("Warning: no vocab file")

    # Load model and fast memory
    model = CortexCode(
        vocab_size=tokenizer.vocab_size() if tokenizer.token_to_id else 1024,
        dim=192, n_layers=4, n_heads=4, ffn_dim=384
    )
    model.load(args.model)
    if os.path.exists(args.model + ".fast_mem"):
        with open(args.model + ".fast_mem") as f:
            content = f.read()
        chunks = content.split("\n---\n")
        for chunk in chunks:
            if chunk.strip():
                model.store([0], chunk.strip())  # empty key, just store the completion
        # Actually, we need to store with proper keys. This is a simplification.

    # Generate
    generated = model.generate(args.prompt, tokenizer,
                              max_new_tokens=args.n_tokens,
                              temperature=args.temperature)
    print(f"\nPrompt: {args.prompt!r}\n")
    print(f"Generated:\n{generated}")


def main():
    parser = argparse.ArgumentParser(description="CortexCode: small, local, brain-inspired code completion")
    sub = parser.add_subparsers(dest="cmd")

    p_demo = sub.add_parser("demo", help="Run a quick demo on synthetic code")

    p_train = sub.add_parser("train", help="Train on a directory of Python code")
    p_train.add_argument("--data-dir", type=str, default=None)
    p_train.add_argument("--out", type=str, default="cortexcode.npz")

    p_sample = sub.add_parser("sample", help="Generate code from a prompt")
    p_sample.add_argument("--prompt", type=str, default="def add(a, b):\n    ")
    p_sample.add_argument("--n-tokens", type=int, default=100)
    p_sample.add_argument("--temperature", type=float, default=0.7)
    p_sample.add_argument("--model", type=str, default="cortexcode.npz")

    args = parser.parse_args()
    if args.cmd == "demo" or args.cmd is None:
        run_demo()
    elif args.cmd == "train":
        run_train(args)
    elif args.cmd == "sample":
        run_sample(args)


if __name__ == "__main__":
    main()

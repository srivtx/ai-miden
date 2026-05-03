#!/usr/bin/env python3
"""
================================================================================
Phase 25: Inference Optimization — Making Models Fast
================================================================================

This script is for a COMPLETE BEGINNER.

In Phases 18-24, we built and aligned a Transformer.
But at scale, these models are SLOW and HUGE.

This phase answers: "How do we make them fast enough to use?"

We cover four techniques:
  1. KV Cache          — Don't recompute what you already know
  2. Quantization      — Use smaller numbers
  3. Flash Attention   — Keep math in fast memory
  4. Grouped Query Attention — Share work across heads

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==============================================================================
# PART 1: KV CACHE
# ==============================================================================
# During autoregressive generation, the model produces one token at a time.
# At step 5, tokens 1-4 are already fixed. Their Keys and Values never change.
# Without cache: recompute K and V for tokens 1-4 EVERY step.
# With cache: compute K and V for token 5 only. Reuse the rest.
# ==============================================================================

def compute_attention_flops(seq_len, d_model):
    """
    Count floating-point operations for one attention layer.
    
    Attention = softmax(Q @ K.T / sqrt(d)) @ V
    
    Q @ K.T: seq_len x seq_len x d_model operations
    Softmax + multiply by V: seq_len x seq_len x d_model
    
    Total: roughly 2 * seq_len^2 * d_model FLOPs
    """
    return 2 * seq_len * seq_len * d_model


def demonstrate_kv_cache():
    """Show how KV Cache saves compute during generation."""
    print("=" * 60)
    print("PART 1: KV CACHE")
    print("=" * 60)
    print()
    print("  During generation, we produce one token at a time.")
    print("  At step T, tokens 1..T-1 are already fixed.")
    print("  Their Keys and Values never change.")
    print()

    d_model = 64   # Small model for demonstration
    max_seq = 100  # Generate 100 tokens

    # Without KV Cache: at step T, attention runs over ALL T tokens
    # But wait — we actually run over the FULL prefix every step
    # AND we recompute K/V for every previous token
    flops_without_cache = 0
    for step in range(1, max_seq + 1):
        # At each step, we process the full sequence so far
        flops = compute_attention_flops(step, d_model)
        flops_without_cache += flops

    # With KV Cache: at step T, attention runs over T tokens
    # BUT K/V for tokens 1..T-1 are already computed and stored
    # We only compute K/V for the NEW token
    # The attention still multiplies Q (1 token) with K (T tokens)
    # This is O(T) per step instead of O(T^2) for the full recomputation
    flops_with_cache = 0
    for step in range(1, max_seq + 1):
        # Attention over T tokens, but K/V computation is just 1 token
        # The heavy part (Q@K.T) is still T x T, but we avoid recomputing K/V
        # In practice, the speedup comes from avoiding the full forward pass
        # For this demo, we count the saved K/V projection FLOPs
        # K/V projection for 1 token: 2 * d_model * d_model
        # Without cache: 2 * step * d_model * d_model
        saved_kv_flops = 2 * (step - 1) * d_model * d_model
        flops_with_cache += saved_kv_flops

    # Even simpler comparison: operations per step
    print("  Sequence length | Without Cache (full recompute) | With Cache (only new token)")
    print("  " + "-" * 70)
    for seq_len in [10, 25, 50, 100]:
        # Without cache: full attention over seq_len tokens PLUS full K/V recompute
        ops_no_cache = seq_len * seq_len * d_model + seq_len * d_model * d_model * 2
        # With cache: attention over seq_len tokens but K/V only for 1 new token
        ops_cache = seq_len * d_model + d_model * d_model * 2
        speedup = ops_no_cache / ops_cache
        print(f"  {seq_len:15d} | {ops_no_cache:30,d} | {ops_cache:28,d}  ({speedup:.1f}x)")

    print()
    print("  KEY INSIGHT:")
    print("    Without cache, every step gets more expensive.")
    print("    With cache, each step costs roughly the SAME.")
    print("    At 100 tokens, we avoid ~99% of redundant K/V work.")
    print()

    # Visualize: operations per step with vs without cache
    steps = np.arange(1, max_seq + 1)
    ops_no_cache_per_step = steps * steps * d_model + steps * d_model * d_model * 2
    ops_cache_per_step = steps * d_model + d_model * d_model * 2

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(steps, ops_no_cache_per_step, label='Without KV Cache', color='red', linewidth=2)
    ax.plot(steps, ops_cache_per_step, label='With KV Cache', color='green', linewidth=2)
    ax.set_xlabel('Generation Step (Sequence Length)', fontsize=12)
    ax.set_ylabel('Operations per Step', fontsize=12)
    ax.set_title('KV Cache: Operations per Generation Step', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase25/kv_cache_speedup.png', dpi=150)
    print("  Plot saved: src/phase25/kv_cache_speedup.png")
    plt.close()
    print()


# ==============================================================================
# PART 2: QUANTIZATION
# ==============================================================================
# Neural network weights are usually stored as 32-bit floats (FP32).
# That's 4 bytes per weight. A 1B model = 4 GB.
# INT8 uses 1 byte per weight. A 1B model = 1 GB.
# INT4 uses 0.5 bytes per weight. A 1B model = 0.5 GB.
# The trick: find a scale and zero-point so integers approximate the floats.
# ==============================================================================

def quantize_weights(weights, bits=8):
    """
    Simulate quantization of weights to lower precision.
    
    PARAMETERS:
        weights = NumPy array of float32 weights
        bits    = 8 for INT8, 4 for INT4
    
    RETURNS:
        quantized = integer array
        scale     = scaling factor
        zero_point = offset
    """
    # Find the min and max of the weights
    w_min = weights.min()
    w_max = weights.max()

    # Number of integer levels we have
    # INT8: -128 to 127 = 256 levels
    # INT4: -8 to 7 = 16 levels
    qmin = -(2 ** (bits - 1))
    qmax = 2 ** (bits - 1) - 1

    # Scale maps the float range to the integer range
    scale = (w_max - w_min) / (qmax - qmin)

    # Zero point: which integer corresponds to float 0
    zero_point = qmin - w_min / scale

    # Quantize: float -> integer
    quantized = np.round(weights / scale + zero_point)
    quantized = np.clip(quantized, qmin, qmax).astype(np.int8 if bits == 8 else np.int8)

    return quantized, scale, zero_point


def dequantize_weights(quantized, scale, zero_point):
    """Convert quantized integers back to floats."""
    return scale * (quantized.astype(np.float32) - zero_point)


def demonstrate_quantization():
    """Show how quantization shrinks models and what error it introduces."""
    print("=" * 60)
    print("PART 2: QUANTIZATION")
    print("=" * 60)
    print()
    print("  Neural networks store weights as 32-bit floats.")
    print("  1 billion weights x 4 bytes = 4 GB.")
    print("  Quantization shrinks this by using fewer bits per weight.")
    print()

    # Simulate a layer's weights
    np.random.seed(42)
    weights = np.random.randn(1000).astype(np.float32) * 0.5

    print(f"  Original weights (FP32): {weights[:5]}")
    print(f"  Memory: {weights.nbytes} bytes ({weights.nbytes/1024:.1f} KB)")
    print()

    # INT8 quantization
    q8, scale8, zp8 = quantize_weights(weights, bits=8)
    w8 = dequantize_weights(q8, scale8, zp8)
    error8 = np.mean(np.abs(weights - w8))

    print(f"  INT8 quantized: {q8[:5]}")
    print(f"  Dequantized:    {w8[:5]}")
    print(f"  Memory:         {q8.nbytes} bytes ({q8.nbytes/1024:.1f} KB) = 4x smaller")
    print(f"  Mean error:     {error8:.6f}")
    print()

    # INT4 quantization (simulate by using INT8 but with fewer levels)
    q4, scale4, zp4 = quantize_weights(weights, bits=4)
    w4 = dequantize_weights(q4, scale4, zp4)
    error4 = np.mean(np.abs(weights - w4))

    print(f"  INT4 quantized: {q4[:5]}")
    print(f"  Dequantized:    {w4[:5]}")
    print(f"  Memory:         {q4.nbytes // 2} bytes ({q4.nbytes/2/1024:.1f} KB) = 8x smaller")
    print(f"  Mean error:     {error4:.6f}")
    print()

    # Show the effect on a forward pass
    x = np.random.randn(1000).astype(np.float32) * 0.3
    y_fp32 = np.dot(weights, x)
    y_int8 = np.dot(w8, x)
    y_int4 = np.dot(w4, x)

    print("  Forward pass with input x:")
    print(f"    FP32 result: {y_fp32:.4f}")
    print(f"    INT8 result: {y_int8:.4f}  (error: {abs(y_fp32-y_int8):.4f})")
    print(f"    INT4 result: {y_int4:.4f}  (error: {abs(y_fp32-y_int4):.4f})")
    print()

    print("  KEY INSIGHT:")
    print("    INT8 is almost perfect for most weights.")
    print("    INT4 is good enough for very large models.")
    print("    A 70B model goes from 280 GB (FP32) to 35 GB (INT4).")
    print("    That fits on a single GPU.")
    print()

    # Visualize weight distributions
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    axes[0].hist(weights, bins=50, color='blue', alpha=0.7)
    axes[0].set_title('Original FP32 Weights', fontweight='bold')
    axes[0].set_xlabel('Weight Value')
    axes[0].set_ylabel('Count')

    axes[1].hist(w8, bins=50, color='orange', alpha=0.7)
    axes[1].set_title('INT8 Dequantized Weights', fontweight='bold')
    axes[1].set_xlabel('Weight Value')

    axes[2].hist(w4, bins=50, color='green', alpha=0.7)
    axes[2].set_title('INT4 Dequantized Weights', fontweight='bold')
    axes[2].set_xlabel('Weight Value')

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase25/quantization_comparison.png', dpi=150)
    print("  Plot saved: src/phase25/quantization_comparison.png")
    plt.close()
    print()


# ==============================================================================
# PART 3: FLASH ATTENTION (Conceptual)
# ==============================================================================
# Standard attention computes the FULL score matrix (N x N) and stores it in
# HBM (High Bandwidth Memory = GPU main RAM). For N=4096, that's 67 MB per
# head per layer. With 32 layers and batch size 4, it is gigabytes.
# 
# Flash Attention breaks the sequence into tiles that fit in SRAM (fast on-chip
# memory). It computes attention for one tile at a time, never storing the full
# N x N matrix. This reduces memory from O(N^2) to O(N).
# ==============================================================================

def demonstrate_flash_attention():
    """Visualize the memory access difference between standard and Flash Attention."""
    print("=" * 60)
    print("PART 3: FLASH ATTENTION")
    print("=" * 60)
    print()
    print("  Standard attention builds the FULL score matrix.")
    print("  For 4096 tokens, that's 4096 x 4096 = 16.7 million numbers.")
    print("  Flash Attention never builds the full matrix.")
    print("  It processes small tiles that fit in fast SRAM.")
    print()

    seq_lengths = [512, 1024, 2048, 4096, 8192]
    d_head = 64
    bytes_per_float = 4  # FP32

    print("  Sequence Length | Standard Memory (MB) | Flash Memory (MB)")
    print("  " + "-" * 60)
    standard_mems = []
    flash_mems = []
    for seq in seq_lengths:
        # Standard: store full N x N score matrix
        std_mem = (seq * seq * bytes_per_float) / (1024 * 1024)
        # Flash: only store one tile at a time, plus O(N) accumulator
        # Tile size typically 256 or 512
        tile_size = 256
        flash_mem = (tile_size * tile_size * bytes_per_float + seq * bytes_per_float) / (1024 * 1024)
        standard_mems.append(std_mem)
        flash_mems.append(flash_mem)
        print(f"  {seq:15d} | {std_mem:20.1f} | {flash_mem:17.1f}")

    print()
    print("  KEY INSIGHT:")
    print("    At 8192 tokens, standard attention needs 256 MB just for scores.")
    print("    Flash Attention needs less than 1 MB of fast SRAM.")
    print("    The speedup comes from fewer slow memory transfers.")
    print()

    # Visualize
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(seq_lengths))
    width = 0.35
    ax.bar(x - width/2, standard_mems, width, label='Standard Attention', color='red', alpha=0.7)
    ax.bar(x + width/2, flash_mems, width, label='Flash Attention', color='green', alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([str(s) for s in seq_lengths])
    ax.set_xlabel('Sequence Length', fontsize=12)
    ax.set_ylabel('Memory for Score Matrix (MB)', fontsize=12)
    ax.set_title('Flash Attention: Memory Usage vs Sequence Length', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase25/flash_attention_memory.png', dpi=150)
    print("  Plot saved: src/phase25/flash_attention_memory.png")
    plt.close()
    print()


# ==============================================================================
# PART 4: GROUPED QUERY ATTENTION (GQA)
# ==============================================================================
# Multi-Head Attention has H heads, each with its own K and V projections.
# The KV Cache stores H Keys and H Values per token.
# GQA groups Query heads so that G Query heads share 1 Key and 1 Value head.
# For 8 heads and group size 4: 8 Queries, 2 Keys, 2 Values.
# Memory drops from 16 vectors/token to 4 vectors/token.
# ==============================================================================

def demonstrate_gqa():
    """Show memory savings from Grouped Query Attention."""
    print("=" * 60)
    print("PART 4: GROUPED QUERY ATTENTION")
    print("=" * 60)
    print()
    print("  Multi-Head Attention: every head has its own K and V.")
    print("  Grouped Query Attention: groups of heads SHARE K and V.")
    print()

    num_heads = 8
    d_head = 64
    seq_len = 4096
    bytes_per_val = 4  # FP32

    # MHA: num_heads K + num_heads V
    kv_mha = num_heads * 2 * seq_len * d_head * bytes_per_val

    # GQA with group size 4: num_heads/4 K + num_heads/4 V
    group_size = 4
    kv_heads = num_heads // group_size
    kv_gqa = kv_heads * 2 * seq_len * d_head * bytes_per_val

    # MQA (extreme): 1 K + 1 V
    kv_mqa = 1 * 2 * seq_len * d_head * bytes_per_val

    print(f"  Setup: {num_heads} heads, {d_head} dims/head, sequence {seq_len}")
    print()
    print("  Method | KV Heads | KV Cache Size | Relative Memory")
    print("  " + "-" * 60)
    print(f"  MHA    | {num_heads:8d} | {kv_mha/1024/1024:11.1f} MB | 100%")
    print(f"  GQA    | {kv_heads:8d} | {kv_gqa/1024/1024:11.1f} MB | {kv_gqa/kv_mha*100:.0f}%")
    print(f"  MQA    | {1:8d} | {kv_mqa/1024/1024:11.1f} MB | {kv_mqa/kv_mha*100:.0f}%")
    print()

    print("  KEY INSIGHT:")
    print("    GQA cuts KV Cache memory by 75% with minimal quality loss.")
    print("    Modern models (Llama 2, Mistral) use GQA by default.")
    print("    This lets you process longer sequences in the same GPU RAM.")
    print()

    # Visualize for different sequence lengths
    seq_lengths = [1024, 2048, 4096, 8192, 16384, 32768]
    mha_mems = []
    gqa_mems = []
    mqa_mems = []

    for seq in seq_lengths:
        mha = num_heads * 2 * seq * d_head * bytes_per_val / (1024**2)
        gqa = kv_heads * 2 * seq * d_head * bytes_per_val / (1024**2)
        mqa = 1 * 2 * seq * d_head * bytes_per_val / (1024**2)
        mha_mems.append(mha)
        gqa_mems.append(gqa)
        mqa_mems.append(mqa)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(seq_lengths, mha_mems, 'o-', label='Multi-Head Attention (MHA)', color='red', linewidth=2)
    ax.plot(seq_lengths, gqa_mems, 's-', label='Grouped Query Attention (GQA)', color='orange', linewidth=2)
    ax.plot(seq_lengths, mqa_mems, '^-', label='Multi-Query Attention (MQA)', color='green', linewidth=2)
    ax.set_xlabel('Sequence Length', fontsize=12)
    ax.set_ylabel('KV Cache Memory (MB)', fontsize=12)
    ax.set_title('Grouped Query Attention: KV Cache Memory', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase25/gqa_memory.png', dpi=150)
    print("  Plot saved: src/phase25/gqa_memory.png")
    plt.close()
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 25: INFERENCE OPTIMIZATION")
    print("=" * 60)
    print()
    print("  Goal: Make models fast and small enough to deploy.")
    print()

    # Part 1: KV Cache
    demonstrate_kv_cache()

    # Part 2: Quantization
    demonstrate_quantization()

    # Part 3: Flash Attention
    demonstrate_flash_attention()

    # Part 4: GQA
    demonstrate_gqa()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - KV Cache demonstration (avoids redundant K/V work)")
    print("    - Quantization demo (INT8 and INT4 weight compression)")
    print("    - Flash Attention memory visualization (tiling in SRAM)")
    print("    - GQA memory comparison (shared K/V heads)")
    print()
    print("  KEY INSIGHTS:")
    print("    1. KV Cache turns O(N^2) generation into O(N) per step.")
    print("    2. INT8 quantization shrinks models 4x with tiny error.")
    print("    3. Flash Attention never builds the full NxN matrix.")
    print("    4. GQA cuts KV Cache memory by 75%.")
    print()
    print("  COMBINED EFFECT:")
    print("    A 70B model that needed 280 GB and 10 sec/token")
    print("    can now run in 35 GB at 0.5 sec/token.")
    print()
    print("  NEXT QUESTION:")
    print("    'The model is fast now. Can I make it THINK harder")
    print("     on difficult problems by using more compute at test time?'")
    print("=" * 60)

# What Is Mixture of Experts (MoE)?

## Problem
Standard dense transformers scale compute with every parameter. For large models, every forward pass uses all weights, making inference expensive and training slow.

## Definition
Mixture of Experts (MoE) replaces a single dense feed-forward layer with multiple smaller "expert" networks and a gating network. For each input token, the gate selects a subset of experts (typically top-k), and only those experts are activated. The outputs are combined by a weighted sum.

## Analogy
Think of a hospital with many specialists (cardiologist, neurologist, etc.). Instead of every patient seeing every doctor, a triage nurse (the gate) routes each patient to the 2 most relevant specialists. The hospital can employ hundreds of doctors, but each patient only sees a few.

## Example
A 1B-parameter dense model has one 1B-parameter FFN. An MoE model might have 64 experts of 16M parameters each, plus a small gating network. Model capacity is large, but per-token compute is small.

## Common Confusion
MoE is sometimes described as "conditional computation" or "sparsity." This can be confusing because the weights are still stored in memory (the model is not smaller on disk). The sparsity is in the compute graph: only a fraction of parameters participate in each forward pass.

## Code Location
See `src/phase96/phase96_moe.py` for a NumPy simulation of a tiny MoE layer with top-2 routing.

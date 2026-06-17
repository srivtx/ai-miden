## Why it exists (THE PROBLEM)

A 10M-param model has ~10M weights. But not all weights matter equally. Many weights are near-zero and contribute almost nothing. A study by Frankle & Carbin (2018) showed that 90% of a neural network's weights can be pruned WITHOUT any loss in accuracy — IF you find the right ones.

**Pruning** removes weights, neurons, or entire layers that contribute the least to the output. A 10M model → 2M model. Same architecture, fewer non-zero weights. Runs faster, uses less memory, costs less.

There are two approaches:
1. **Unstructured pruning:** zero out individual weights. The matrix becomes sparse. But sparse matrix multiply is slow on GPUs (fragmented memory access). Good for compression, not for speed.
2. **Structured pruning:** remove entire rows/columns/neurons. The matrix shrinks. Fewer FLOPs. Faster on all hardware. Good for speed, harder to preserve accuracy.

## Definition (very simple)

**Magnitude pruning (simplest):** Compute the absolute value of every weight. Remove the smallest N% (set to zero). Retrain the remaining weights to recover accuracy. Repeat: prune → retrain → prune → retrain (iterative pruning). After 3-5 cycles, the model is sparser AND accurate.

**Criteria for "importance" (more sophisticated):**
- Magnitude: |w| (how big is the weight?)
- Gradient: |w * grad| (how much does this weight move during training?)
- Taylor: |w * grad + 0.5 * w^2 * hessian| (second-order approximation of impact on loss)
- Movement: |w_initial - w_final| (how much did the weight change from initialization?)

In practice, magnitude pruning is 80% as good as the fancier methods and 10× simpler to implement.

## Practice: Minimal magnitude pruning

```python
def prune_magnitude(model, sparsity=0.5):
    """Prune the smallest 50% of weights (set to zero)."""
    all_weights = []
    for name, param in model.named_parameters():
        if 'weight' in name and param.dim() >= 2:
            # Flatten, compute threshold
            flat = param.data.abs().view(-1)
            k = int(len(flat) * sparsity)
            threshold = flat.topk(k, largest=False).values[-1]

            # Create mask: 0 where weight < threshold, 1 otherwise
            mask = (param.data.abs() >= threshold).float()
            param.data = param.data * mask
            all_weights.append(param.data)

    # Compute actual sparsity
    total = sum(w.numel() for w in all_weights)
    zeros = sum((w == 0).sum().item() for w in all_weights)
    print(f"Pruned: {zeros}/{total} weights ({100*zeros/total:.1f}% sparse)")
    return mask  # save masks for later use


def prune_structured(layer, keep_fraction=0.5):
    """Remove entire neurons (columns) from a linear layer."""
    W = layer.weight.data  # (out_features, in_features)
    # Compute norm of each column
    col_norms = W.norm(dim=0)  # (in_features,)
    k = int(len(col_norms) * keep_fraction)
    threshold = col_norms.topk(k, largest=False).values[-1]

    # Keep columns with norm above threshold
    keep_mask = col_norms >= threshold  # (in_features,)

    # Apply: create new smaller layer
    new_W = W[:, keep_mask]
    layer.weight.data = new_W
    # Also need to adjust the PREVIOUS layer's output projection
    # (structured pruning cascades — more complex)

    return keep_mask
```

## Key properties

| | Dense (unpruned) | Unstructured pruned (50%) | Structured pruned (50%) |
|---|---|---|---|
| Parameters used | 100% | 50% | 50% |
| FLOPs | 100% | 100% (sparse matmul is slow on GPU) | 50% |
| Memory (fp32) | 100% | 100% (zeros still stored) | 50% |
| Accuracy drop | 0% | ~0.5% | ~2-5% |
| Best for | Baseline | Compression (storage) | Speed (inference) |

## The lottery ticket hypothesis

Frankle & Carbin (2018) found: randomly initialized, densely connected networks contain WINNING TICKETS — subnetworks that, when trained in isolation, can match the full network's accuracy. The trick: you can't just train the subnetwork from scratch; you must train the FULL network first, prune it, then RESET the remaining weights to their INITIAL values (not their trained values) and retrain. This is the "lottery ticket" — the specific initialization + pruning mask that yields a trainable subnetwork.

Practical takeaway: if you prune and RETRAIN (with a warm start), you recover most accuracy. If you prune and TRAIN FROM SCRATCH, accuracy drops more. Always prune from a trained model, not from initialization.

## Common confusion

1. **"Pruning makes inference faster."** Unstructured pruning (individual weight zeros) saves MODEL SIZE (compression) but NOT inference speed, because sparse matrix multiply on GPU is slow (IRREGULAR memory access). Structured pruning (removing whole neurons) saves BOTH. If your goal is speed: structured. If storage: unstructured. If both: structured then quantize.

2. **"50% sparsity = 2x speedup."** Only for structured sparsity. For unstructured: GPU Tensor Cores require 2:4 structured sparsity (2 non-zero out of every 4 weights in a block) to get 2x speedup. Random 50% sparsity gives ~1.05x speedup (barely any). The hardware matters.

3. **"Prune once and you're done."** Iterative pruning (prune → retrain → prune → retrain) consistently beats one-shot pruning. 3 cycles of 20% pruning = 50% total sparsity, with 5× less accuracy loss than pruning 50% at once.

## Connection to cortexcode

Apply unstructured pruning to the 10M model post-training. Remove 50% of weights by magnitude. Retrain for 500 steps to recover accuracy. Model file size drops from 38MB to 19MB (stored as sparse). For structured pruning: remove 50% of attention heads (heads with smallest output norm). 4 heads → 2 heads. Model is physically smaller, faster, and uses less VRAM.

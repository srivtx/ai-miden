## What Is Training Efficiency?

---

### The Problem

Training a frontier language model costs millions of dollars in compute. A significant fraction of that cost is not FLOPs but data movement: loading parameters from HBM to SRAM, writing gradients back, and shuffling optimizer states. Next-token prediction is data-movement-inefficient because every transformer layer's output is used to compute exactly one cross-entropy loss. The matmuls are dense, but the supervision signal is sparse. How do you increase the density of supervision without increasing the model size or the dataset size?

---

### Definition

**Training efficiency** in the context of multi-token prediction is the ratio of supervisory signals (target tokens) to forward-pass FLOPs. MTP improves this ratio by producing N target predictions per forward pass, effectively increasing the label density by a factor of N while the backbone computation stays nearly constant.

**How it works:**
```
Standard training:
  Forward FLOPs ≈ 2 * params * seq_len
  Labels per forward pass = seq_len - 1
  Efficiency = labels / FLOPs ≈ 0.5 / params

MTP training (N=4):
  Forward FLOPs ≈ 2 * params * seq_len + small_head_overhead
  Labels per forward pass = 4 * (seq_len - 4)
  Efficiency ≈ 2.0 / params   ← 4x improvement
```

**Why MTP is ~2x faster (not 4x):**
- The heads add a small FLOP overhead (~1-2%).
- The loss computation and backward through the heads add gradient communication.
- Memory bandwidth for loading the dataset and storing activations is unchanged.
- In practice, the bottleneck shifts from "not enough labels" to "memory bandwidth saturation," so the speedup is typically 1.5x to 2.5x depending on hardware and model size.

**FLOP efficiency comparison:**
```
Method                    Labels/FLOP    Relative throughput
Standard NTP              1.0x           1.0x
MTP N=2                   2.0x           ~1.4x
MTP N=4                   4.0x           ~2.0x
MTP N=8                   8.0x           ~2.4x (diminishing returns)
```

---

### Real-Life Analogy

Imagine a tutoring session where a student reads one page of a textbook and the teacher asks one comprehension question.

**Standard next-token prediction** is that single-question session. The student reads deeply, but the teacher's time is underutilized. The student could have answered three more questions about the same page without re-reading it, but the teacher only asks one. The session ends, and the student moves to the next page.

**MTP training** is the teacher asking four questions per page. The student still reads the page once, but now the teacher extracts four times as much evidence that the student understood it. The student's reading time is unchanged; only the questioning phase lengthens slightly. Over the course of a semester, the student masters the material in half the time.

**The trade-off:** asking four questions risks confusing the student if the later questions depend on answers to earlier ones. But if the questions are well-designed — if they test parallel aspects of comprehension — the student benefits. In MTP, the parallel aspects are the conditional independences among future tokens given deep context.

**Diminishing returns:** asking 100 questions per page would overwhelm the student. Similarly, MTP with N > 4 sees diminishing returns because later heads target tokens so far in the future that the context window has not seen enough evidence to predict them accurately. The gradient signal becomes noise.

---

### Tiny Numeric Example

**Training on a sequence of length 8 with batch size 1:**

**Standard NTP:**
```
Forward pass computes hidden states H[0:7] for positions 0-6.
Loss positions: 1, 2, 3, 4, 5, 6, 7  → 7 labels
Forward FLOPs: 100 units
Efficiency: 7 / 100 = 0.070 labels per FLOP
```

**MTP N=4:**
```
Forward pass computes hidden states H[0:7] once.
Head 1 targets: 1, 2, 3, 4, 5, 6, 7      → 7 labels
Head 2 targets: 2, 3, 4, 5, 6, 7         → 6 labels
Head 3 targets: 3, 4, 5, 6, 7            → 5 labels
Head 4 targets: 4, 5, 6, 7               → 4 labels
Total labels: 22
Head overhead FLOPs: 4 units
Total FLOPs: 104
Efficiency: 22 / 104 = 0.212 labels per FLOP
Improvement: 3.0x
```

**Wall-clock comparison (simulated):**
```
Standard NTP on 10K sequences:
  Forward+backward time: 120 seconds
  Labels processed: 70K
  Labels/second: 583

MTP N=4 on 10K sequences:
  Forward+backward time: 128 seconds  (+6.7% for heads)
  Labels processed: 220K
  Labels/second: 1,719
  Speedup: 2.95x
```

**The shift:** the expensive transformer backbone is amortized across four prediction tasks. The model learns more from every FLOP, and training converges faster because the optimizer sees richer gradient information at each step.

---

### Common Confusion

1. **"MTP makes the model 4x larger."** No. The extra heads are tiny linear projections. For GPT-2 124M, adding three heads increases parameters by less than 1%. The backbone is unchanged.

2. **"MTP requires 4x the dataset."** No. The same dataset is used. Each sequence simply provides four shifted target windows instead of one. The data loader slices the text differently.

3. **"MTP converges in 1/4 the steps."** Empirically, it converges in roughly 1/2 the steps because the later heads provide noisier signal. The total compute saving is ~2x, not 4x.

4. **"MTP only helps during pre-training."** MTP helps during any training phase: pre-training, fine-tuning, or continual pre-training. Anywhere you train with next-token prediction, MTP increases label density.

5. **"The speedup is linear in N."** It is sublinear. N=2 gives ~1.4x, N=4 gives ~2.0x, N=8 gives ~2.4x. Overheads and diminishing gradient quality prevent linear scaling.

6. **"MTP hurts perplexity because later heads are weak."** DeepSeek-V3 and Meta's experiments show no perplexity degradation at N=4. The shared backbone is strong enough that even the t+4 head outperforms a baseline model trained without MTP.

7. **"MTP is only for decoder-only transformers."** The principle applies to any autoregressive model: RNNs, state-space models, or encoder-decoder architectures. The implementation differs, but the efficiency gain is the same.

---

### Where It Is Used in Our Code

`src/phase112/phase112_mtp_training_colab.py` — We train GPT-2 124M with MTP N=4 and compare wall-clock time, tokens processed per second, and convergence steps against standard next-token training. We plot loss curves normalized by step and by wall-clock time to show that MTP achieves lower loss in less time, demonstrating the 2x training efficiency gain.

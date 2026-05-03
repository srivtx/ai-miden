## What Is Masked Autoencoding?

---

### The Problem

BERT revolutionized NLP by masking words and predicting them from context. Can the same idea work for images? If you cover 75% of an image's pixels, can a model reconstruct the missing parts? And if it can, has it learned something useful about vision?

---

### Definition

**Masked Autoencoding (MAE)** is a self-supervised method where random patches of an image are masked (hidden), and a transformer decoder reconstructs the missing patches from the visible ones.

**The MAE architecture:**
```
Image (224×224) -> Patch into 16×16 patches (196 total)
Randomly mask 75% of patches (keep only 49 visible)
Encoder (ViT) processes ONLY the 49 visible patches
Decoder (small transformer) reconstructs all 196 patches
Loss: MSE between reconstructed and original patches
```

**Why masking 75% works:**
- Forces the model to learn high-level semantic understanding, not just pixel copying
- The reconstruction task is hard enough to be meaningful, but solvable with context
- The encoder sees only 25% of patches, making pre-training much faster

**Training process:**
```
1. Take unlabeled image
2. Mask 75% of patches randomly
3. Encode visible patches -> latent representation
4. Decoder predicts all patches (visible + masked)
5. Loss = MSE on masked patches only
6. Repeat on millions of images
```

**After pre-training:**
- The encoder is a powerful visual representation learner
- Fine-tune on 1% labeled data achieves competitive accuracy
- The decoder is discarded; only the encoder is kept

---

### Real-Life Analogy

A restorer working on a damaged painting.
- **Supervised learning:** The restorer copies from a photograph of the original. They learn to replicate but do not understand the artistic style.
- **Masked autoencoding:** 75% of the painting is covered with paper. The restorer must infer the hidden parts from the visible 25% — the brush style, color palette, perspective, and subject matter. To succeed, they must truly understand how paintings work.

The reconstruction task forces deep understanding, not surface memorization.

---

### Tiny Numeric Example

**4×4 image patch (values 0-9):**
```
Original patch:
[1, 2, 3, 4]
[5, 6, 7, 8]
[9, 0, 1, 2]
[3, 4, 5, 6]
```

**Mask 75% (keep only top-left quadrant):**
```
Visible:   [1, 2, ?, ?]
           [5, 6, ?, ?]
           [?, ?, ?, ?]
           [?, ?, ?, ?]
```

**Encoder sees:** `[1, 2, 5, 6]` (flattened visible pixels)

**Decoder predicts all 16 pixels:**
```
Prediction:
[1.1, 1.9, 2.8, 3.9]
[4.9, 6.1, 7.2, 7.8]
[8.8, 0.2, 1.1, 2.1]
[2.9, 4.1, 4.8, 6.2]
```

**Loss (MSE on masked pixels only):**
```
(2.8-3)² + (3.9-4)² + (7.2-7)² + (7.8-8)² + ... = 0.34
```

The model learns to extrapolate patterns from visible to hidden regions.

---

### Common Confusion

1. **"MAE is just a denoising autoencoder."** Similar spirit, but MAE uses a transformer architecture and masks at the patch level, not pixel level. The scale and architecture are different.

2. **"MAE needs labeled data for pre-training."** No. MAE is purely self-supervised. Labels are only used for downstream fine-tuning.

3. **"Higher mask ratio is always better."** 75% is optimal for MAE. Lower ratios make the task too easy. Higher ratios make it impossible.

4. **"MAE only works for images."** The idea works for any modality: audio spectrograms (masked time/frequency bins), video (masked space-time patches), and even protein structures.

5. **"The decoder is kept after pre-training."** No. The decoder is only for the pre-training task. The encoder is the valuable part that transfers to downstream tasks.

---

### Where It Is Used in Our Code

`src/phase50/phase50_self_supervised_learning.py` — We implement masked autoencoding on tiny 8×8 images. The model reconstructs masked patches, and we show the encoder learns useful features for downstream classification.

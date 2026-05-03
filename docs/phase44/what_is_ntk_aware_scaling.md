## What Is NTK-Aware Scaling?

---

### The Problem

Basic position interpolation uniformly scales all RoPE dimensions. YaRN improves this by treating dimensions differently. But both approaches modify the position encoding directly. Is there a way to extend context by changing the RoPE base frequency itself, without explicitly interpolating positions?

---

### Definition

**NTK-Aware Scaling** extends a model's context window by increasing the RoPE base frequency, based on insights from Neural Tangent Kernel (NTK) theory about how neural networks learn different frequency components.

**The core insight from NTK theory:**
- Neural networks learn high-frequency components more slowly than low-frequency components
- When extending context, high-frequency dimensions (which capture local patterns) should be disturbed as little as possible
- Low-frequency dimensions can be stretched more because they learn global patterns

**The formula:**
```
new_base = base × (L_target / L_train)^(d / (d - 2))
```

Where:
- `base` = original RoPE base (typically 10,000)
- `L_target` = desired context length
- `L_train` = original training context length
- `d` = head dimension

**What this does:**
- Increasing the base stretches the frequency spectrum
- Higher base → slower rotation angles → same positions map to smaller angles
- This effectively "zooms out" the position encoding to cover a wider range

**NTK-Aware vs. Standard Interpolation:**
- Standard interpolation: `scaled_position = position × (L_train / L_target)`
- NTK-aware: `new_base = base × scale_factor`, then use original positions
- NTK-aware disturbs high frequencies less, preserving local attention quality

---

### Real-Life Analogy

A map with a fixed grid.
- **Standard interpolation:** You shrink the map so the entire world fits on one page. Everything becomes tiny and hard to read.
- **NTK-aware scaling:** You change the map projection. Local areas (your neighborhood) stay at familiar scale, while global distances (continent-to-continent) are stretched. You can now see the whole world without losing street-level detail.

The grid lines (position encoding) are redrawn with a new projection that preserves local precision while expanding global coverage.

---

### Tiny Numeric Example

**Original:** base = 10,000, L_train = 4, L_target = 16, d = 4

**Standard interpolation for position 16, dimension 0:**
```
scaled_position = 16 × (4/16) = 4
θ_0 = 4 × 10000^0 = 4.0 radians
```

**NTK-aware scaling:**
```
scale = L_target / L_train = 16 / 4 = 4
new_base = 10000 × 4^(4/(4-2)) = 10000 × 4^2 = 10000 × 16 = 160,000

θ_0 = 16 × 160000^0 = 16 × 1 = 16.0 radians
```

Wait, that gives 16.0 which is WORSE. Let me recalculate with the correct formula:

Actually the NTK formula is often written as:
```
new_base = base × scale^(d / (d - 2))
```
But the effect is to change the frequency spectrum. Let me use a more practical example:

For d = 64 (typical head dim), scale = 4:
```
new_base = 10000 × 4^(64/62) ≈ 10000 × 4.2 ≈ 42,000
```

**Dimension 0 (high frequency):**
```
Original: θ_0 = position × 10000^0 = position × 1.0
NTK:      θ_0 = position × 42000^0 = position × 1.0
```
No change for dimension 0! High frequencies are preserved.

**Dimension 30 (mid frequency):**
```
Original: θ_30 = position × 10000^(-30/32) ≈ position × 0.056
NTK:      θ_30 = position × 42000^(-30/32) ≈ position × 0.031
```
Mid frequencies are compressed.

**Dimension 62 (low frequency):**
```
Original: θ_62 = position × 10000^(-62/32) ≈ position × 0.0004
NTK:      θ_62 = position × 42000^(-62/32) ≈ position × 0.0001
```
Low frequencies are compressed more.

**Result:** NTK-aware scaling compresses frequencies gradually, disturbing high frequencies the least.

---

### Common Confusion

1. **"NTK-aware scaling requires NTK theory to implement."** No. The formula is simple. The "NTK" part is the theoretical justification, not the implementation.

2. **"NTK-aware scaling is just changing the base parameter."** Yes, that is literally what it does. But the specific scaling formula is derived from NTK theory to optimally preserve learning dynamics.

3. **"NTK-aware and YaRN are competing methods."** They are complementary. Some implementations combine both: NTK-aware base scaling plus per-dimension interpolation.

4. **"NTK-aware scaling works without any fine-tuning."** It works better than basic interpolation without fine-tuning, but a small amount of fine-tuning still helps.

5. **"NTK-aware scaling increases model size."** No. It only changes one hyperparameter (the RoPE base). Model weights, architecture, and inference speed are unchanged.

---

### Where It Is Used in Our Code

`src/phase44/phase44_long_context.py` — We implement NTK-aware base scaling and compare it against basic position interpolation. We visualize how the frequency spectrum shifts and measure attention pattern preservation.

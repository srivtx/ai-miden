### 1. Why it exists (THE PROBLEM first)
Modern language models have billions of parameters stored as 32-bit floating-point numbers. A 70-billion-parameter model needs 280 GB just for weights (70B x 4 bytes). That exceeds the memory of most GPUs. Inference is also slower because FP32 arithmetic is expensive. We need a way to shrink models without destroying their behavior.

### 2. Definition (very simple)
Quantization is the process of converting high-precision numbers (like 32-bit floats) into lower-precision numbers (like 16-bit floats, 8-bit integers, or even 4-bit integers). It reduces memory usage and speeds up math operations, usually at the cost of a small accuracy drop.

### 3. Real-life analogy
A professional photographer stores photos as RAW files (huge, every detail preserved). For sharing online, they convert to JPEG (smaller, slightly compressed). Quantization is like JPEG compression for neural network weights: most of the picture is still there, but the file size is a fraction.

### 4. Tiny numeric example
Original weights (FP32): [0.153, -0.891, 0.004, 1.247, -0.332]

INT8 quantization maps the range [-1.247, 1.247] to [-128, 127]:
- Scale = 1.247 / 127 = 0.00982
- Quantized: [16, -91, 0, 127, -34]

To use them:
- Dequantized: [0.157, -0.894, 0.0, 1.247, -0.334]

The values are close but not exact. The error is tiny for most weights, and the model usually still works fine.

### 5. Common confusion
- **Quantization is not pruning.** Pruning removes weights entirely (sets them to zero). Quantization keeps all weights but stores them with fewer bits.
- **INT8 does not mean the model becomes an integer model.** The weights are stored as integers, but during inference they are dequantized back to floats (or specialized hardware does integer math and rescales).
- **Not all layers quantize equally.** Some layers (like the final output layer or attention layers) are more sensitive to precision loss and are sometimes kept in FP16 while the rest uses INT8.
- **Quantization Aware Training (QAT) vs Post-Training Quantization (PTQ).** PTQ quantizes a trained model directly. QAT simulates quantization during training so the model learns to be robust to it. QAT is more accurate but harder.
- **4-bit is not always worse than 8-bit.** Modern methods like NF4 (Normal Float 4) distribute quantization bins cleverly and can match INT8 quality for large models.

### 6. Where it is used in our code
`src/phase25/phase25_inference_optimization.py` demonstrates FP32, INT8, and INT4 weight quantization on a tiny model, showing memory savings and the small error introduced.

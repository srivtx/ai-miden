## What Is Model Quantization?

**The Problem:**
Your 1B-parameter model uses 4 GB of memory and takes 500ms per inference. Your product team wants to run it on a $5/month CPU server. How do you shrink the model by 4x and speed it up by 2-4x without retraining from scratch?

**Definition:**
**Model quantization** is the process of converting a model's weights and/or activations from high-precision formats (FP32) to low-precision formats (INT8, INT4, FP16). This reduces memory usage, speeds up inference, and enables deployment on resource-constrained hardware.

**Real-life analogy:**
Quantization is like converting a high-resolution RAW photograph to a compressed JPEG. The RAW file is 50 MB with perfect color fidelity. The JPEG is 5 MB with slightly less detail. For most uses — Instagram, email, web pages — the JPEG is indistinguishable from the RAW. Quantization does the same for neural networks: it trades a tiny amount of precision for a massive reduction in size and speed.

**Tiny numeric example:**
FP32 weight: 0.374129
INT8 weight: round(0.374129 * 127) = 48
To dequantize: 48 / 127 = 0.377953
Error: |0.377953 - 0.374129| = 0.003824 (1% relative error)
Across 66M parameters, these tiny errors mostly cancel out, and accuracy drops by only 0.1-0.5%.

**Common confusion:**
- **"Quantization always hurts accuracy."** Usually by <1%, but sometimes it improves accuracy due to regularization effects. Quantization-aware training often matches FP32 accuracy.
- **"INT8 is 8x smaller than FP32."** Almost, but not quite. PyTorch's quantized format adds scale and zero-point metadata. The actual reduction is ~3.5-4x.
- **"Quantization requires retraining."** Post-training quantization (what we do here) requires zero retraining. Quantization-aware training requires retraining but gives better results.
- **"Quantization only works on CPUs."** INT8 works on CPUs, NVIDIA GPUs (TensorRT), and mobile chips (Apple Neural Engine). It is the standard deployment format.
- **"You quantize the entire model."** Not always. Some layers (like the first and last) are more sensitive to quantization and are kept in FP32. This is called "mixed precision quantization."
- **"Dynamic quantization is the best method."** Dynamic quantization is the simplest. Static quantization and quantization-aware training give better results but require more setup.

**Where it appears in our code:**
`src/phase158/phase158_quantization_deployment.py` — Loads DistilBERT, applies PyTorch dynamic quantization to Linear layers, benchmarks FP32 vs INT8 on speed, memory, and accuracy, and saves the quantized model.

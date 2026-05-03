## What Is ONNX Export?

---

### The Problem

You trained a beautiful PyTorch transformer. It works perfectly in your Jupyter notebook. Now your boss wants it on an iPhone app, a factory-floor Raspberry Pi, a Java backend, and an AWS Lambda function. You cannot install PyTorch on all of those. Re-implementing the model in TensorFlow Lite, CoreML, C++, and Java is months of error-prone work. Even worse, every re-implementation drifts slightly from the original, so the iPhone app gives different answers than the cloud API. How do you train once and deploy everywhere without rewriting the model in five languages?

---

### Definition

**ONNX (Open Neural Network Exchange)** is an open standard format for representing machine learning models. **ONNX Export** is the process of converting a trained model from PyTorch, TensorFlow, or JAX into a single `.onnx` file containing a portable computation graph. That graph can then be executed by **ONNX Runtime** — a high-performance inference engine that runs on Linux, Windows, macOS, iOS, Android, and edge devices, and supports hardware accelerators like CUDA, TensorRT, DirectML, and OpenVINO.

**Key features:**
- **Cross-platform:** One file runs on cloud GPUs, mobile CPUs, and embedded devices
- **Quantization:** INT8 and FP16 quantization can shrink model size 2-4x and speed up inference 1.5-5x
- **Graph optimization:** ONNX Runtime fuses layers, eliminates dead code, and constant-folds operations automatically
- **No Python dependency:** The runtime is written in C++, so it integrates into C++, C#, Java, and mobile apps

**Why this matters:**
- Reduces deployment time from weeks to hours
- Guarantees bit-exact consistency across platforms
- Quantized ONNX models often run faster than the original PyTorch on CPU

---

### Real-Life Analogy

A PDF document.
- **No standard format:** You write a report in Microsoft Word. Your colleague uses Google Docs. The factory floor uses a typewriter. The mobile app can only read plain text. You must retype the report four times, and every version has slightly different formatting and typos.
- **ONNX Export:** You export the report to PDF. Everyone — the Word user, the Google Docs user, the print shop, the phone screen — sees the exact same layout. The PDF is the universal language of documents. ONNX is the universal language of neural networks.
- **Quantization:** A high-resolution PDF is 50MB and slow to email. You can generate a compressed version that is 5MB, loads instantly on a phone, and is visually identical for most purposes. ONNX INT8 quantization is the compressed PDF of ML.

---

### Tiny Numeric Example

**Setup:** A small feedforward classifier with 2 layers.

**PyTorch model:**
```python
class TinyNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(10, 8)
        self.fc2 = torch.nn.Linear(8, 2)
    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))
```

**Export:**
```python
torch.onnx.export(model, dummy_input, "tinynet.onnx",
                  input_names=["input"], output_names=["output"])
```

**Resulting ONNX graph:**
```
input -> MatMul(10x8) -> Add(bias) -> Relu -> MatMul(8x2) -> Add(bias) -> output
```

**Size and speed comparison (realistic estimates for a medium model):**
```
PyTorch FP32 checkpoint: 500 MB
ONNX FP32:             500 MB  (same weights, different container)
ONNX FP16:             250 MB  (half precision)
ONNX INT8:             125 MB  (quantized)

Inference on CPU (single sample):
PyTorch:               2.3 seconds
ONNX Runtime FP32:     1.8 seconds
ONNX Runtime INT8:     0.4 seconds  (5.7x speedup)
```

---

### Common Confusion

1. **"ONNX is a framework like PyTorch."** No. ONNX is a file format and runtime. You still train in PyTorch; ONNX is the deployment artifact, like a compiled binary.

2. **"ONNX Export works for every PyTorch model automatically."** No. Dynamic control flow (data-dependent `if` statements, loops with variable iterations) often fails to trace. You may need to rewrite logic or use ONNX-script for dynamic graphs.

3. **"Quantized ONNX models are always faster."** Usually yes on CPU, but not always on GPU. INT8 tensor cores require specific alignment; poorly quantized models can be slower than FP16 on NVIDIA hardware.

4. **"ONNX Runtime replaces CUDA."** No. ONNX Runtime can use CUDA, TensorRT, DirectML, or OpenVINO as backends. It is a layer above the hardware API, not a replacement.

5. **"Exporting to ONNX means you lose the ability to retrain."** Yes. ONNX is for inference only. If you need to fine-tune later, keep the original PyTorch checkpoint. Treat ONNX as the compiled executable, not the source code.

6. **"ONNX is only for small models."** No. GPT-2, Llama, Whisper, and Stable Diffusion all have ONNX export workflows. Large models may be split across multiple ONNX files (model sharding) or use external data format for weights > 2GB.

7. **"ONNX and TensorRT are competitors."** No. TensorRT can compile ONNX files into highly optimized engines. They are complementary: ONNX is the portable format; TensorRT is one of many optimizers that consume it.

---

### Where It Is Used in Our Code

`src/phase71/phase71_inference_deployment.py` — We simulate model size reduction from quantization and compare memory footprints, showing why ONNX + INT8 is essential for edge deployment.

`src/phase71/phase71_inference_deployment_colab.py` — We export a small transformer to ONNX using `torch.onnx.export`, run inference with ONNX Runtime, verify numerical equivalence against PyTorch, and show the exact workflow for cross-platform deployment.

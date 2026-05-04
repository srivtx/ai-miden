## What Is Deployment?

**The Problem:**
You have a trained, evaluated, and quantized model sitting in a checkpoint file. But your users cannot access a .pt file. How do you package the model so it can be loaded by a server, a mobile app, or an embedded device? How do you version it, document it, and ensure it loads correctly in production?

**Definition:**
**Deployment** is the process of packaging a trained model into a production-ready format, saving it with metadata, and making it available for inference in a target environment.

**Real-life analogy:**
Deployment is like shipping a product. You have a finished prototype (the trained model). You need to put it in a box with instructions (metadata), label it with a version number, and ship it to stores (servers). The box must be the right size for the store shelf (memory constraints). The instructions must be in the right language (API format). If the box is damaged in transit (corruption), the store needs to verify it before putting it on the shelf (checksums).

**Tiny numeric example:**
Before deployment:
- Model: 255 MB FP32 checkpoint
- No metadata
- Loaded with custom code
- Only works on your laptop

After deployment:
- Model: 65 MB INT8 quantized model + tokenizer
- Metadata: accuracy, speed, quantization config
- Loaded with standard HuggingFace AutoModel
- Works on any CPU server

**Common confusion:**
- **"Deployment is just saving the model."** It is saving + packaging + documenting + versioning. A checkpoint without metadata is not deployable.
- **"You deploy the training code."** No. You deploy the inference code. Training code is often 10x larger and includes data loading, optimization, and logging that are irrelevant in production.
- **"Deployment is a one-time event."** Models are deployed continuously. A/B testing, canary releases, and rollback procedures require multiple versions in production simultaneously.
- **"The same model works everywhere."** A model quantized for a mobile chip may not load on a server. Deployment targets require different formats (ONNX, CoreML, TensorRT, TFLite).

**Where it appears in our code:**
`src/phase158/phase158_quantization_deployment.py` — Saves the FP32 model with HuggingFace format, saves the INT8 model with torch.save, and writes a JSON report with all metrics and configuration.

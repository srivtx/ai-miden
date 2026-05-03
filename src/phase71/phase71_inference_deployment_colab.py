#!/usr/bin/env python3
"""
Phase 71: Inference & Deployment — Colab Real-Workflow Script
===============================================================
This script is designed to run in Google Colab (T4 GPU) or any CUDA environment.
It demonstrates the FULL production workflow:
  1. Load a real transformer model.
  2. Benchmark single vs. batch inference speed.
  3. Simulate continuous batching behavior.
  4. Export the model to ONNX for cross-platform deployment.
  5. Build a FastAPI server mockup showing real serving code.

WHY this matters: Research notebooks call model.generate() in a loop.
Production systems must batch, schedule, quantize, and serve. This script
bridges that gap with heavy comments explaining every decision.
"""

# =============================================================================
# SECTION 0: ENVIRONMENT SETUP
# =============================================================================
# WHY: We need PyTorch and transformers. In Colab, these are pre-installed.
# For vLLM, you would run:  !pip install vllm  (commented out for portability)

import time
import torch
import numpy as np

# Check GPU availability — serving without a GPU is like a restaurant without a kitchen
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")
if DEVICE == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# =============================================================================
# SECTION 1: LOAD A REAL MODEL
# =============================================================================
# WHY GPT-2? It is small enough to fit in Colab memory ( ~500 MB ) but large
# enough to show real batching effects. For production Llama/Mistral, the
# absolute numbers change but the PRINCIPLES stay identical.

from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "gpt2"  # 124M parameters — tiny by modern standards, perfect for demo

print(f"\nLoading {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.to(DEVICE)
model.eval()  # WHY eval(): disables dropout and gradient computation, essential for inference

# GPT-2 tokenizer has no pad token by default. We set it to eos_token so we can batch.
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Model loaded. Parameter count:", sum(p.numel() for p in model.parameters()))

# =============================================================================
# SECTION 2: BENCHMARK SINGLE VS. BATCH INFERENCE
# =============================================================================
# WHY: GPU matrix multiplication is massively parallel. One sample leaves
# thousands of CUDA cores idle. Batching fills those cores, but memory
# bandwidth eventually saturates. We measure the exact trade-off.

prompts = [
    "The future of artificial intelligence is",
    "In the depths of the ocean, scientists discovered",
    "The stock market crashed because",
    "Once upon a time in a distant galaxy",
    "The secret to happiness lies in",
    "Quantum computers will revolutionize",
    "Climate change is the most pressing",
    "The human brain contains approximately",
]

MAX_NEW_TOKENS = 20

# --- SINGLE INFERENCE ---
print("\n--- Single Inference Benchmark ---")
single_times = []
for prompt in prompts:
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
    # Warm-up (first CUDA kernel launch is slow due to compilation)
    if len(single_times) == 0:
        with torch.no_grad():
            _ = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS)
        if DEVICE == "cuda":
            torch.cuda.synchronize()

    start = time.time()
    with torch.no_grad():  # WHY no_grad(): prevents PyTorch from building a compute graph
        outputs = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS)
    if DEVICE == "cuda":
        torch.cuda.synchronize()  # WHY: wait for all CUDA kernels to finish
    elapsed = time.time() - start
    single_times.append(elapsed)

avg_single = np.mean(single_times)
print(f"Average single-request latency: {avg_single * 1000:.1f} ms")
print(f"Throughput (single):            {1.0 / avg_single:.2f} requests/sec")

# --- BATCH INFERENCE ---
print("\n--- Batch Inference Benchmark ---")
# WHY padding=True: short sequences get padded so all tensors in the batch
# have the same shape. This is the source of padding waste (see docs).
inputs = tokenizer(prompts, return_tensors="pt", padding=True).to(DEVICE)

# Warm-up
with torch.no_grad():
    _ = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS)
if DEVICE == "cuda":
    torch.cuda.synchronize()

start = time.time()
with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS)
if DEVICE == "cuda":
    torch.cuda.synchronize()
batch_time = time.time() - start

print(f"Batch latency (n={len(prompts)}):     {batch_time * 1000:.1f} ms")
print(f"Throughput (batch):             {len(prompts) / batch_time:.2f} requests/sec")
print(f"Latency per request (amortized): {batch_time / len(prompts) * 1000:.1f} ms")
print(f"Speedup from batching:          {sum(single_times) / batch_time:.2f}x")

# =============================================================================
# SECTION 3: CONTINUOUS BATCHING CONCEPT
# =============================================================================
# WHY: Standard generate() processes one batch from start to finish.
# vLLM's continuous batching adds new requests and removes finished ones
# at EVERY generation step. We simulate this concept in Python.

print("\n--- Continuous Batching Simulation ---")

class Request:
    """Simulates one user request in a production queue."""
    def __init__(self, prompt_tokens, max_len):
        self.tokens = prompt_tokens
        self.max_len = max_len
        self.generated = 0
        self.done = False

    def step(self):
        """Generate one more token. In vLLM, this is one attention forward."""
        if not self.done:
            self.generated += 1
            # Simulate early finish (e.g., EOS token)
            if self.generated >= self.max_len:
                self.done = True

# Simulate 5 requests arriving at different times with different lengths
requests = [
    Request([1, 2, 3], 3),      # short, finishes early
    Request([4, 5], 5),         # medium
    Request([6], 8),            # long
    Request([7, 8, 9, 10], 4),  # medium-short
    Request([11], 6),           # medium-long
]

# Static batching: run until ALL requests finish
static_steps = 0
while not all(r.done for r in requests):
    static_steps += 1
    for r in requests:
        r.step()
print(f"Static batching steps:  {static_steps}")

# Reset for continuous batching simulation
for r in requests:
    r.generated = 0
    r.done = False

# Continuous batching: new requests join immediately when others finish
# We simulate by adding requests one by one as slots free up
continuous_steps = 0
active = []
queue = list(requests)
while queue or active:
    # Fill empty slots from queue (simulates new requests arriving)
    while queue and len(active) < 3:  # max concurrent = 3
        active.append(queue.pop(0))
    # One generation step for all active requests
    continuous_steps += 1
    for r in active:
        r.step()
    # Remove finished requests (their KV cache pages are freed)
    active = [r for r in active if not r.done]

print(f"Continuous batching steps: {continuous_steps}")
print(f"Efficiency gain:           {static_steps / continuous_steps:.2f}x fewer idle steps")

# =============================================================================
# SECTION 4: ONNX EXPORT WORKFLOW
# =============================================================================
# WHY: ONNX is the "PDF" of neural networks. Train in PyTorch, deploy on
# iPhone, Raspberry Pi, or C++ backend. We export GPT-2 here as a demo.
# For large models (>2 GB), use external_data_format=True.

print("\n--- ONNX Export ---")

try:
    import onnx
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False
    print("onnx and onnxruntime not installed. Showing workflow only.")
    print("Install with:  pip install onnx onnxruntime-gpu")

if HAS_ONNX:
    dummy_input = torch.randint(0, 50257, (1, 10)).to(DEVICE)  # batch=1, seq=10
    onnx_path = "/tmp/gpt2_toy.onnx"

    # WHY opset_version=14: newer opsets support more operators (e.g., GELU)
    # WHY input_names/output_names: required for ONNX Runtime to bind tensors
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        opset_version=14,
        input_names=["input_ids"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size", 1: "sequence_length"},
        },
    )
    print(f"Exported ONNX model to: {onnx_path}")
    print(f"ONNX file size:         {os.path.getsize(onnx_path) / 1024:.1f} KB")

    # Verify with ONNX Runtime
    session = ort.InferenceSession(onnx_path, providers=["CUDAExecutionProvider"] if DEVICE == "cuda" else ["CPUExecutionProvider"])
    onnx_inputs = {session.get_inputs()[0].name: dummy_input.cpu().numpy()}
    onnx_outputs = session.run(None, onnx_inputs)
    print(f"ONNX output shape:      {onnx_outputs[0].shape}")
    print("ONNX export verified successfully.")
else:
    print("Skipping ONNX verification (libraries not installed).")

# =============================================================================
# SECTION 5: FASTAPI SERVER MOCKUP
# =============================================================================
# WHY: A real production endpoint is not a Python script you run manually.
# It is a persistent HTTP server that accepts JSON, batches requests,
# and returns JSON. FastAPI is the industry standard for this in Python.
# This section is a MOCKUP — it shows the architecture without requiring
# `uvicorn` to be installed in this notebook.

print("\n--- FastAPI Server Mockup ---")

server_code = '''
# ==== Save this to server.py and run:  uvicorn server:app --host 0.0.0.0 --port 8000 ====

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

app = FastAPI()

# WHY load at module level: model loading is SLOW (seconds). We do it once
# when the server starts, not on every request.
MODEL_NAME = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.to("cuda" if torch.cuda.is_available() else "cpu")
model.eval()

class GenerateRequest(BaseModel):
    prompts: List[str]
    max_new_tokens: int = 20

@app.post("/generate")
async def generate(req: GenerateRequest):
    """
    WHY batch in the endpoint: if 8 users hit this simultaneously,
    we should batch their requests into one forward pass.
    In production, use a background queue (e.g., Redis + Celery) for
    true dynamic batching rather than synchronous batching.
    """
    inputs = tokenizer(req.prompts, return_tensors="pt", padding=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=req.max_new_tokens)

    # WHY skip_special_tokens=True: prevents <|endoftext|> from appearing
    # in the user-facing response.
    texts = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    return {"generated": texts}

# Health check for load balancers
@app.get("/health")
async def health():
    return {"status": "ok", "device": str(model.device)}
'''

print(server_code)
print("\nNOTE: This is a mockup. To run a real server, install fastapi and uvicorn:")
print("  pip install fastapi uvicorn")
print("  uvicorn server:app --host 0.0.0.0 --port 8000")

# =============================================================================
# SECTION 6: VLLM BENCHMARK (OPTIONAL)
# =============================================================================
# WHY vLLM? For production LLM serving, vLLM delivers 3-5x throughput
# via PagedAttention and continuous batching. We show the code pattern
# but fall back gracefully if vLLM is not installed.

print("\n--- vLLM Benchmark (Optional) ---")
try:
    from vllm import LLM, SamplingParams
    print("vLLM detected. Running benchmark...")

    # WHY trust_remote_code=True: some models (e.g., ChatGLM) need custom architectures
    llm = LLM(model=MODEL_NAME, trust_remote_code=True)
    sampling_params = SamplingParams(temperature=0.8, max_tokens=MAX_NEW_TOKENS)

    # Single prompt
    start = time.time()
    outputs = llm.generate(prompts[0], sampling_params)
    single_vllm = time.time() - start
    print(f"vLLM single latency: {single_vllm * 1000:.1f} ms")

    # Batch
    start = time.time()
    outputs = llm.generate(prompts, sampling_params)
    batch_vllm = time.time() - start
    print(f"vLLM batch latency:  {batch_vllm * 1000:.1f} ms")
    print(f"vLLM throughput:     {len(prompts) / batch_vllm:.2f} req/sec")

except ImportError:
    print("vLLM not installed. Skipping vLLM benchmark.")
    print("To install:  pip install vllm")
    print("vLLM is the recommended engine for production LLM serving.")

# =============================================================================
# SECTION 7: FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 60)
print("PHASE 71 COLAB SUMMARY")
print("=" * 60)
print(f"Model:                  {MODEL_NAME}")
print(f"Device:                 {DEVICE}")
print(f"Single latency:         {avg_single * 1000:.1f} ms")
print(f"Batch latency (n=8):    {batch_time * 1000:.1f} ms")
print(f"Batching speedup:       {sum(single_times) / batch_time:.2f}x")
print(f"Continuous batch gain:  ~{static_steps / continuous_steps:.2f}x idle reduction")
print("\nProduction checklist:")
print("  [ ] Use dynamic batching or vLLM for high throughput")
print("  [ ] Export to ONNX for edge / mobile deployment")
print("  [ ] Wrap in FastAPI/gRPC for network serving")
print("  [ ] Monitor memory — KV cache is the silent OOM killer")
print("  [ ] Add request timeouts to prevent head-of-line blocking")

"""
Phase 158: Real Quantization & Deployment
==========================================
This is a REAL project. Not a toy.

We build a complete quantization and deployment pipeline:
1. Load a real model (DistilBERT)
2. Evaluate the full-precision (FP32) baseline
3. Quantize to INT8 using PyTorch quantization
4. Benchmark inference speed (FP32 vs INT8)
5. Benchmark memory usage (FP32 vs INT8)
6. Measure accuracy drop from quantization
7. Save the quantized model for deployment
8. Generate a deployment report

This is how companies deploy models on CPUs and edge devices.
Run time: ~2-3 minutes on CPU.
"""

import os
import json
import time
import psutil
from typing import Dict, Tuple

import numpy as np
import torch
import torch.quantization
from torch.utils.data import DataLoader, Subset
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
from datasets import load_dataset
from tqdm import tqdm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG = {
    "model_name": "distilbert-base-uncased",
    "task": "sst2",
    "max_length": 128,
    "batch_size": 16,
    "eval_subset": 500,
    "seed": 42,
}

torch.manual_seed(CONFIG["seed"])
np.random.seed(CONFIG["seed"])
device = torch.device("cpu")  # Quantization is typically done on CPU

# ============================================================================
# LOAD MODEL AND DATA
# ============================================================================
print("Loading model and tokenizer...")
tokenizer = DistilBertTokenizer.from_pretrained(CONFIG["model_name"])
model_fp32 = DistilBertForSequenceClassification.from_pretrained(
    CONFIG["model_name"], num_labels=2
).to(device)
model_fp32.eval()

print("Loading dataset...")
dataset = load_dataset("glue", CONFIG["task"], split="validation")
dataset = dataset.select(range(min(CONFIG["eval_subset"], len(dataset))))

def tokenize_function(examples):
    return tokenizer(
        examples["sentence"],
        padding="max_length",
        truncation=True,
        max_length=CONFIG["max_length"],
        return_tensors="pt",
    )

tokenized = dataset.map(tokenize_function, batched=True)
tokenized = tokenized.remove_columns(["sentence", "idx"])
tokenized = tokenized.rename_column("label", "labels")
tokenized.set_format("torch")

dataloader = DataLoader(tokenized, batch_size=CONFIG["batch_size"])

# ============================================================================
# EVALUATION FUNCTION
# ============================================================================

def evaluate_model(model, dataloader, desc="Evaluating"):
    """Evaluate accuracy and measure inference time."""
    model.eval()
    correct = 0
    total = 0
    total_time = 0.0
    num_batches = 0

    with torch.no_grad():
        for batch in tqdm(dataloader, desc=desc):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            start = time.time()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            end = time.time()

            total_time += (end - start)
            num_batches += 1

            preds = torch.argmax(outputs.logits, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total
    avg_time_per_batch = total_time / num_batches
    throughput = total / total_time  # samples per second

    return accuracy, avg_time_per_batch, throughput

# ============================================================================
# MEMORY MEASUREMENT
# ============================================================================

def get_model_size_mb(model):
    """Get model size in MB."""
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    size_mb = (param_size + buffer_size) / 1024**2
    return size_mb

# ============================================================================
# FP32 BASELINE
# ============================================================================
print("\n" + "="*60)
print("FP32 BASELINE")
print("="*60)

fp32_size = get_model_size_mb(model_fp32)
print(f"Model size: {fp32_size:.2f} MB")

fp32_acc, fp32_time, fp32_throughput = evaluate_model(model_fp32, dataloader, "FP32 Eval")
print(f"Accuracy: {fp32_acc:.4f}")
print(f"Time per batch: {fp32_time:.4f}s")
print(f"Throughput: {fp32_throughput:.1f} samples/sec")

# ============================================================================
# INT8 QUANTIZATION
# ============================================================================
# WHY: Quantization converts FP32 weights to INT8, reducing model size by 4x
# and speeding up inference on CPUs with INT8 support (most modern CPUs).

print("\n" + "="*60)
print("INT8 QUANTIZATION")
print("="*60)

# Dynamic quantization quantizes weights to INT8 but keeps activations
# in FP32, computing scale factors on-the-fly. It is the simplest form.
model_int8 = torch.quantization.quantize_dynamic(
    model_fp32,
    {torch.nn.Linear},  # Quantize only Linear layers
    dtype=torch.qint8,
)

int8_size = get_model_size_mb(model_int8)
print(f"Model size: {int8_size:.2f} MB")
print(f"Size reduction: {(1 - int8_size/fp32_size)*100:.1f}%")

int8_acc, int8_time, int8_throughput = evaluate_model(model_int8, dataloader, "INT8 Eval")
print(f"Accuracy: {int8_acc:.4f}")
print(f"Time per batch: {int8_time:.4f}s")
print(f"Throughput: {int8_throughput:.1f} samples/sec")

# ============================================================================
# COMPARISON
# ============================================================================
print("\n" + "="*60)
print("COMPARISON")
print("="*60)

speedup = fp32_time / int8_time
accuracy_drop = (fp32_acc - int8_acc) * 100

print(f"Speedup: {speedup:.2f}x")
print(f"Size reduction: {(1 - int8_size/fp32_size)*100:.1f}%")
print(f"Accuracy drop: {accuracy_drop:.2f} percentage points")

results = {
    "fp32": {
        "size_mb": float(fp32_size),
        "accuracy": float(fp32_acc),
        "time_per_batch_ms": float(fp32_time * 1000),
        "throughput": float(fp32_throughput),
    },
    "int8": {
        "size_mb": float(int8_size),
        "accuracy": float(int8_acc),
        "time_per_batch_ms": float(int8_time * 1000),
        "throughput": float(int8_throughput),
    },
    "comparison": {
        "speedup": float(speedup),
        "size_reduction_pct": float((1 - int8_size/fp32_size)*100),
        "accuracy_drop_pct": float(accuracy_drop),
    },
}

# ============================================================================
# SAVE MODELS
# ============================================================================
os.makedirs("src/phase158/quantized_model", exist_ok=True)

# Save FP32
model_fp32.save_pretrained("src/phase158/quantized_model/fp32")
tokenizer.save_pretrained("src/phase158/quantized_model/fp32")

# Save INT8 (torch.save for quantized models)
torch.save(model_int8.state_dict(), "src/phase158/quantized_model/int8_model.pt")

# Save report
with open("src/phase158/quantization_report.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved report to src/phase158/quantization_report.json")

# ============================================================================
# VISUALIZATION
# ============================================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Size comparison
axes[0].bar(['FP32', 'INT8'], [fp32_size, int8_size], color=['#1f77b4', '#ff7f0e'])
axes[0].set_ylabel('Size (MB)')
axes[0].set_title('Model Size')
for i, v in enumerate([fp32_size, int8_size]):
    axes[0].text(i, v + 2, f"{v:.1f} MB", ha='center', fontweight='bold')
axes[0].grid(True, alpha=0.3, axis='y')

# Speed comparison
axes[1].bar(['FP32', 'INT8'], [fp32_time*1000, int8_time*1000], color=['#1f77b4', '#ff7f0e'])
axes[1].set_ylabel('Time per Batch (ms)')
axes[1].set_title(f'Inference Speed ({speedup:.2f}x Speedup)')
for i, v in enumerate([fp32_time*1000, int8_time*1000]):
    axes[1].text(i, v + 5, f"{v:.1f} ms", ha='center', fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='y')

# Accuracy comparison
axes[2].bar(['FP32', 'INT8'], [fp32_acc, int8_acc], color=['#1f77b4', '#ff7f0e'])
axes[2].set_ylabel('Accuracy')
axes[2].set_title(f'Accuracy ({accuracy_drop:.2f} pp drop)')
axes[2].set_ylim(0, 1)
for i, v in enumerate([fp32_acc, int8_acc]):
    axes[2].text(i, v + 0.02, f"{v:.4f}", ha='center', fontweight='bold')
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("src/phase158/quantization_comparison.png", dpi=150)
print("Saved visualization to src/phase158/quantization_comparison.png")

print("\n" + "="*60)
print("PHASE 158 COMPLETE")
print("="*60)
print("You have quantized a real model and measured the tradeoffs.")
print("This is how companies deploy models on phones, IoT devices,")
print("and cost-optimized cloud servers.")

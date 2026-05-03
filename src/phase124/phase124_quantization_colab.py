# FRONTIER TRACK — PHASE 124: Advanced Quantization (Colab / T4)
# Quantizes Llama-3.2-3B-Instruct to 8-bit (LLM.int8) and 4-bit (NF4),
# then measures perplexity, memory footprint, inference speed, and generation quality.

# ------------------------------------------------------------------
# 1. SETUP: Install dependencies programmatically
# ------------------------------------------------------------------
import subprocess
import sys
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "-q",
    "transformers", "accelerate", "bitsandbytes", "datasets", "matplotlib", "pandas"
])

import os
import gc
import time
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# ------------------------------------------------------------------
# 2. AUTHENTICATION: Gated Llama model
# ------------------------------------------------------------------
from huggingface_hub import login
hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    login(token=hf_token)
else:
    try:
        from huggingface_hub import notebook_login
        notebook_login()
    except Exception:
        print("WARNING: No HF_TOKEN. Gated model download may fail.")

BASE_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"

# ------------------------------------------------------------------
# 3. TOKENIZER
# ------------------------------------------------------------------
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, use_fast=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# ------------------------------------------------------------------
# 4. LOAD WIKITEXT-2 TEST SET FOR PERPLEXITY
# ------------------------------------------------------------------
# wikitext-2 is the standard small benchmark for language-model perplexity
wikitext = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
text = "\n\n".join([t for t in wikitext["text"] if t.strip()])
encodings = tokenizer(text, return_tensors="pt")
# Cap evaluation length so T4 finishes quickly
MAX_EVAL_TOKENS = 8192
input_ids_full = encodings.input_ids[:, :MAX_EVAL_TOKENS]

# ------------------------------------------------------------------
# 5. HELPER FUNCTIONS
# ------------------------------------------------------------------
def compute_perplexity(model, input_ids, stride=512, max_length=2048):
    """
    Sliding-window perplexity.
    Striding preserves long-context history without truncation artifacts.
    """
    nlls = []
    prev_end_loc = 0
    max_length = min(max_length, model.config.max_position_embeddings)
    for begin_loc in range(0, input_ids.size(1), stride):
        end_loc = min(begin_loc + max_length, input_ids.size(1))
        trg_len = end_loc - prev_end_loc
        chunk = input_ids[:, begin_loc:end_loc].to(model.device)
        target_ids = chunk.clone()
        target_ids[:, :-trg_len] = -100
        with torch.no_grad():
            outputs = model(chunk, labels=target_ids)
            neg_log_likelihood = outputs.loss * trg_len
        nlls.append(neg_log_likelihood)
        prev_end_loc = end_loc
        if end_loc == input_ids.size(1):
            break
    ppl = torch.exp(torch.stack(nlls).sum() / end_loc)
    return ppl.item()

def measure_speed(model, tokenizer, prompt="The future of artificial intelligence is", max_new_tokens=100):
    """Wall-clock tokens-per-second for greedy generation."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    # Warmup to exclude one-time CUDA kernel launch overhead
    _ = model.generate(**inputs, max_new_tokens=10, do_sample=False, pad_token_id=tokenizer.eos_token_id)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    start = time.time()
    _ = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tokenizer.eos_token_id)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    elapsed = time.time() - start
    return max_new_tokens / elapsed

def get_model_size_mb(model):
    """Report actual GPU bytes for BnB models, or parameter count * dtype size for FP16."""
    if hasattr(model, "get_memory_footprint"):
        return model.get_memory_footprint() / (1024 ** 2)
    total = sum(p.numel() * p.element_size() for p in model.parameters())
    return total / (1024 ** 2)

def generate_sample(model, tokenizer, prompt="Artificial intelligence will transform"):
    """Generate a creative sample with light sampling."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=80,
            do_sample=True,
            top_p=0.9,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ------------------------------------------------------------------
# 6. DEFINE QUANTIZATION VARIANTS
# ------------------------------------------------------------------
variants = {
    "FP16": {
        "torch_dtype": torch.float16,
    },
    "8-bit (LLM.int8)": {
        "quantization_config": BitsAndBytesConfig(load_in_8bit=True),
    },
    "4-bit (NF4)": {
        "quantization_config": BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        ),
    },
}

results = {
    "Variant": [],
    "Size_MB": [],
    "Perplexity": [],
    "Tokens_per_sec": [],
    "Sample": [],
}

# ------------------------------------------------------------------
# 7. EVALUATION LOOP
# ------------------------------------------------------------------
for name, cfg in variants.items():
    print(f"\n{'='*60}")
    print(f"Loading variant: {name}")
    print(f"{'='*60}")

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        device_map="auto",
        **cfg,
    )

    size_mb = get_model_size_mb(model)
    print(f"Model size: {size_mb:.1f} MB")

    ppl = compute_perplexity(model, input_ids_full)
    print(f"Perplexity: {ppl:.2f}")

    tps = measure_speed(model, tokenizer)
    print(f"Inference speed: {tps:.1f} tokens/sec")

    sample = generate_sample(model, tokenizer)
    print(f"Sample: {sample[:200]}...")

    results["Variant"].append(name)
    results["Size_MB"].append(size_mb)
    results["Perplexity"].append(ppl)
    results["Tokens_per_sec"].append(tps)
    results["Sample"].append(sample)

    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# ------------------------------------------------------------------
# 8. COMPARISON TABLE
# ------------------------------------------------------------------
df = pd.DataFrame(results)
print("\n" + "=" * 60)
print("QUANTIZATION COMPARISON TABLE")
print("=" * 60)
print(df[["Variant", "Size_MB", "Perplexity", "Tokens_per_sec"]].to_string(index=False))
print("=" * 60)

# ------------------------------------------------------------------
# 9. PLOTS
# ------------------------------------------------------------------
x = np.arange(len(df))
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].bar(x, df["Size_MB"], color=["steelblue", "orange", "green"])
axes[0].set_xticks(x)
axes[0].set_xticklabels(df["Variant"], rotation=15, ha="right")
axes[0].set_ylabel("Size (MB)")
axes[0].set_title("Model Memory Footprint")

axes[1].bar(x, df["Perplexity"], color=["steelblue", "orange", "green"])
axes[1].set_xticks(x)
axes[1].set_xticklabels(df["Variant"], rotation=15, ha="right")
axes[1].set_ylabel("Perplexity")
axes[1].set_title("Perplexity on WikiText-2 (lower is better)")

axes[2].bar(x, df["Tokens_per_sec"], color=["steelblue", "orange", "green"])
axes[2].set_xticks(x)
axes[2].set_xticklabels(df["Variant"], rotation=15, ha="right")
axes[2].set_ylabel("Tokens / sec")
axes[2].set_title("Inference Speed (higher is better)")

plt.tight_layout()
plt.savefig("phase124_quantization_colab_results.png", dpi=150)
plt.show()
print("Saved plot: phase124_quantization_colab_results.png")

# ------------------------------------------------------------------
# 10. FULL SAMPLES
# ------------------------------------------------------------------
print("\n--- FULL GENERATED SAMPLES ---")
for i, row in df.iterrows():
    print(f"\n>> {row['Variant']}:")
    print(row["Sample"])

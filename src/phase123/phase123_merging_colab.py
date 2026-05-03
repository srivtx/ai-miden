# FRONTIER TRACK — PHASE 123: Model Merging at Scale (Colab / T4)
# Fine-tunes two LoRA adapters on Llama-3.2-3B-Instruct, merges them with task arithmetic,
# and demonstrates multi-task competence retention.

# ------------------------------------------------------------------
# 1. SETUP: Install dependencies programmatically so the script works in Colab and plain Python
# ------------------------------------------------------------------
import subprocess
import sys
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "-q",
    "transformers", "peft", "datasets", "accelerate", "bitsandbytes", "matplotlib", "pandas"
])

import os
import re
import gc
import time
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from difflib import SequenceMatcher
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, PeftModel, TaskType

# ------------------------------------------------------------------
# 2. AUTHENTICATION: Access the gated Llama model
# ------------------------------------------------------------------
# Llama-3.2-3B-Instruct requires Hugging Face acceptance; we log in via token or interactive prompt
from huggingface_hub import login
hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    login(token=hf_token)
else:
    try:
        from huggingface_hub import notebook_login
        notebook_login()
    except Exception:
        print("WARNING: No HF_TOKEN found. Download of gated model may fail.")

# ------------------------------------------------------------------
# 3. CONFIGURATION: Hyper-parameters and paths
# ------------------------------------------------------------------
BASE_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"

# LoRA hyperparameters: small rank keeps memory low and prevents over-writing base knowledge
LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "v_proj"]

# Training: tiny batch + gradient accumulation simulates larger batch on T4 VRAM
TRAIN_BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 4
MAX_STEPS = 50
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 512

# Evaluation subset size: keep small for fast generation on T4
EVAL_SAMPLES = 20

# ------------------------------------------------------------------
# 4. TOKENIZER: Load once and set pad token
# ------------------------------------------------------------------
# Llama tokenizers have no default pad token; reusing eos_token prevents indexing crashes
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, use_fast=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# ------------------------------------------------------------------
# 5. HELPER FUNCTIONS: Data formatting, generation, evaluation
# ------------------------------------------------------------------
def format_math_example(example):
    """Serialize a GSM8K example into a single causal-LM text."""
    # Concatenating question and answer lets the model learn to continue after the prompt
    text = f"Question: {example['question']}\nAnswer: {example['answer']}{tokenizer.eos_token}"
    return {"text": text}

def format_code_example(example):
    """Serialize a CodeAlpaca example into a single causal-LM text."""
    instruction = example["instruction"]
    inp = example.get("input", "")
    output = example["output"]
    if inp:
        text = f"### Instruction:\n{instruction}\n### Input:\n{inp}\n### Response:\n{output}{tokenizer.eos_token}"
    else:
        text = f"### Instruction:\n{instruction}\n### Response:\n{output}{tokenizer.eos_token}"
    return {"text": text}

def tokenize_function(examples):
    """Tokenize without padding; the data collator will pad dynamically per batch."""
    # Truncation avoids out-of-memory from extremely long sequences
    return tokenizer(examples["text"], truncation=True, max_length=MAX_SEQ_LENGTH)

def generate_text(model, prompt, max_new_tokens=128):
    """Greedy generation returning only the newly generated tokens."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    # Slice off the prompt to isolate the model's continuation
    gen_ids = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(gen_ids, skip_special_tokens=True)

def extract_math_answer(text):
    """Extract the final numeric answer from GSM8K-style text."""
    # Ground truth uses #### delimiter; search for it first
    match = re.search(r"####\s*(-?\d+(?:,\d+)*(?:\.\d+)?)", text)
    if match:
        return match.group(1).replace(",", "")
    # Fallback: last number in the string
    nums = re.findall(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    return nums[-1] if nums else None

def compute_math_accuracy(model, dataset):
    """Exact-match accuracy on a subset of GSM8K."""
    correct = 0
    for example in dataset:
        prompt = f"Question: {example['question']}\nAnswer:"
        generated = generate_text(model, prompt, max_new_tokens=128)
        pred = extract_math_answer(generated)
        true = extract_math_answer(example["answer"])
        if pred is not None and true is not None and pred.strip() == true.strip():
            correct += 1
    return correct / len(dataset)

def normalize_code(text):
    """Remove markdown fences and collapse whitespace for fair comparison."""
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return " ".join(" ".join(lines).split())

def compute_code_accuracy(model, dataset):
    """
    Similarity-based accuracy for code generation.
    Exact match is too strict after only 50 LoRA steps; we count SequenceMatcher > 0.5 as correct.
    """
    correct = 0
    for example in dataset:
        instruction = example["instruction"]
        inp = example.get("input", "")
        if inp:
            prompt = f"### Instruction:\n{instruction}\n### Input:\n{inp}\n### Response:\n"
        else:
            prompt = f"### Instruction:\n{instruction}\n### Response:\n"
        generated = generate_text(model, prompt, max_new_tokens=256)
        pred = normalize_code(generated)
        ref = normalize_code(example["output"])
        sim = SequenceMatcher(None, pred, ref).ratio()
        if sim > 0.5:
            correct += 1
    return correct / len(dataset)

def capture_sample(model, task):
    """Generate one sample for pretty printing."""
    if task == "math":
        ex = gsm8k_test[0]
        prompt = f"Question: {ex['question']}\nAnswer:"
        gen = generate_text(model, prompt, max_new_tokens=128)
        return {"prompt": prompt, "generated": gen, "truth": ex["answer"]}
    else:
        ex = code_test[0]
        prompt = f"### Instruction:\n{ex['instruction']}\n### Response:\n"
        gen = generate_text(model, prompt, max_new_tokens=256)
        return {"prompt": prompt, "generated": gen, "truth": ex["output"]}

# ------------------------------------------------------------------
# 6. DATASETS: Load small subsets for fast training and evaluation
# ------------------------------------------------------------------
# GSM8K: grade-school math with chain-of-thought reasoning
gsm8k = load_dataset("gsm8k", "main")
gsm8k_train = gsm8k["train"].select(range(200)).map(format_math_example)
gsm8k_test = gsm8k["test"].select(range(EVAL_SAMPLES))

# CodeAlpaca: instruction-following code generation
code_dataset = load_dataset("sahil2801/CodeAlpaca-20k", split="train")
code_train = code_dataset.select(range(200)).map(format_code_example)
code_test = code_dataset.select(range(200, 200 + EVAL_SAMPLES))

# Tokenize training sets
gsm8k_train_tok = gsm8k_train.map(tokenize_function, batched=True, remove_columns=gsm8k_train.column_names)
code_train_tok = code_train.map(tokenize_function, batched=True, remove_columns=code_train.column_names)

# Data collator for causal LM (no masked language modeling)
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# ------------------------------------------------------------------
# 7. TRAIN MATH ADAPTER (Adapter A)
# ------------------------------------------------------------------
# Load base model in FP16; 3B fits comfortably in T4's 16 GB VRAM
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",
)
# Gradient checkpointing trades compute for memory, essential for training 3B on T4
base_model.gradient_checkpointing_enable()
base_model.enable_input_require_grads()

# LoRA config: only update query/value projections to minimize trainable parameters
lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    target_modules=TARGET_MODULES,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

# Wrap base model with PEFT to inject trainable low-rank matrices
model_math = get_peft_model(base_model, lora_config)
print("Math adapter trainable parameters:")
model_math.print_trainable_parameters()

math_training_args = TrainingArguments(
    output_dir="./math_adapter",
    overwrite_output_dir=True,
    max_steps=MAX_STEPS,
    per_device_train_batch_size=TRAIN_BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM_STEPS,
    learning_rate=LEARNING_RATE,
    fp16=True,  # Mixed precision speeds up training and halves activation memory
    logging_steps=10,
    save_strategy="no",  # We only need the final adapter in memory/disk
    report_to="none",
)

trainer_math = Trainer(
    model=model_math,
    args=math_training_args,
    train_dataset=gsm8k_train_tok,
    data_collator=data_collator,
)

# Train: the model learns to generate math chain-of-thought answers
trainer_math.train()
model_math.save_pretrained("./adapters/math")
print("Math adapter saved to ./adapters/math")

# Evaluate math specialist on its own task
math_acc = compute_math_accuracy(model_math, gsm8k_test)
print(f"Math adapter accuracy on math: {math_acc:.2%}")

# Free VRAM before training the next adapter
del trainer_math
del model_math
gc.collect()
torch.cuda.empty_cache()

# Also delete the base model because get_peft_model mutates it in place; we want a fresh backbone
del base_model
gc.collect()
torch.cuda.empty_cache()

# ------------------------------------------------------------------
# 8. TRAIN CODE ADAPTER (Adapter B)
# ------------------------------------------------------------------
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",
)
base_model.gradient_checkpointing_enable()
base_model.enable_input_require_grads()

model_code = get_peft_model(base_model, lora_config)
print("Code adapter trainable parameters:")
model_code.print_trainable_parameters()

code_training_args = TrainingArguments(
    output_dir="./code_adapter",
    overwrite_output_dir=True,
    max_steps=MAX_STEPS,
    per_device_train_batch_size=TRAIN_BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM_STEPS,
    learning_rate=LEARNING_RATE,
    fp16=True,
    logging_steps=10,
    save_strategy="no",
    report_to="none",
)

trainer_code = Trainer(
    model=model_code,
    args=code_training_args,
    train_dataset=code_train_tok,
    data_collator=data_collator,
)

trainer_code.train()
model_code.save_pretrained("./adapters/code")
print("Code adapter saved to ./adapters/code")

code_acc = compute_code_accuracy(model_code, code_test)
print(f"Code adapter accuracy on code: {code_acc:.2%}")

del trainer_code
del model_math
gc.collect()
torch.cuda.empty_cache()

# Clean base model as well
del base_model
gc.collect()
torch.cuda.empty_cache()

# ------------------------------------------------------------------
# 9. EVALUATE ALL VARIANTS ON BOTH TASKS
# ------------------------------------------------------------------
results = {
    "Model": [],
    "Math Accuracy": [],
    "Code Accuracy": [],
}
samples = {}

# --- Base Model (no adapters) ---
base_pure = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",
)
results["Model"].append("Base")
results["Math Accuracy"].append(compute_math_accuracy(base_pure, gsm8k_test))
results["Code Accuracy"].append(compute_code_accuracy(base_pure, code_test))
samples["Base"] = {
    "math": capture_sample(base_pure, "math"),
    "code": capture_sample(base_pure, "code"),
}
del base_pure
gc.collect()
torch.cuda.empty_cache()

# --- Adapter evaluation on a single wrapped backbone ---
base_eval = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",
)
# Wrap once so we can hot-swap adapter weights without reloading the 3B backbone
base_eval = get_peft_model(base_eval, lora_config)

# Math specialist
base_eval.load_adapter("./adapters/math", adapter_name="math")
base_eval.set_adapter("math")
results["Model"].append("Math Specialist")
results["Math Accuracy"].append(compute_math_accuracy(base_eval, gsm8k_test))
results["Code Accuracy"].append(compute_code_accuracy(base_eval, code_test))
samples["Math"] = {
    "math": capture_sample(base_eval, "math"),
    "code": capture_sample(base_eval, "code"),
}

# Code specialist
base_eval.load_adapter("./adapters/code", adapter_name="code")
base_eval.set_adapter("code")
results["Model"].append("Code Specialist")
results["Math Accuracy"].append(compute_math_accuracy(base_eval, gsm8k_test))
results["Code Accuracy"].append(compute_code_accuracy(base_eval, code_test))
samples["Code"] = {
    "math": capture_sample(base_eval, "math"),
    "code": capture_sample(base_eval, "code"),
}

# Task-Arithmetic Merge: merged_delta = delta_math + delta_code
# In PEFT, linear combination with weights [1,1] adds the two adapter deltas
base_eval.add_weighted_adapter(
    adapters=["math", "code"],
    weights=[1.0, 1.0],
    adapter_name="merged",
    combination_type="linear",
)
base_eval.set_adapter("merged")
results["Model"].append("Task-Arithmetic Merged")
results["Math Accuracy"].append(compute_math_accuracy(base_eval, gsm8k_test))
results["Code Accuracy"].append(compute_code_accuracy(base_eval, code_test))
samples["Merged"] = {
    "math": capture_sample(base_eval, "math"),
    "code": capture_sample(base_eval, "code"),
}

# ------------------------------------------------------------------
# 10. COMPARISON TABLE
# ------------------------------------------------------------------
df = pd.DataFrame(results)
print("\n" + "=" * 60)
print("ACCURACY COMPARISON TABLE")
print("=" * 60)
print(df.to_string(index=False))
print("=" * 60)

# ------------------------------------------------------------------
# 11. VISUALIZATION
# ------------------------------------------------------------------
x = np.arange(len(df))
width = 0.35

plt.figure(figsize=(8, 5))
plt.bar(x - width / 2, df["Math Accuracy"], width, label="Math Accuracy")
plt.bar(x + width / 2, df["Code Accuracy"], width, label="Code Accuracy")
plt.xticks(x, df["Model"], rotation=15, ha="right")
plt.ylabel("Accuracy")
plt.title("Phase 123: Specialist vs Merged Model Accuracy")
plt.ylim(0, 1.0)
plt.legend()
plt.tight_layout()
plt.savefig("phase123_merging_colab_results.png", dpi=150)
plt.show()
print("Saved plot: phase123_merging_colab_results.png")

# ------------------------------------------------------------------
# 12. SAMPLE OUTPUTS
# ------------------------------------------------------------------
for model_name in results["Model"]:
    print(f"\n--- {model_name}: MATH SAMPLE ---")
    print("Prompt:", samples[model_name]["math"]["prompt"])
    print("Generated:", samples[model_name]["math"]["generated"])
    print("Ground Truth:", samples[model_name]["math"]["truth"])

    print(f"\n--- {model_name}: CODE SAMPLE ---")
    print("Prompt:", samples[model_name]["code"]["prompt"])
    print("Generated:", samples[model_name]["code"]["generated"])
    print("Ground Truth:", samples[model_name]["code"]["truth"])

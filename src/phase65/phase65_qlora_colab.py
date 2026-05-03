#!/usr/bin/env python3
"""
Phase 65: QLoRA Real-Workflow Script (Colab / GPU)
====================================================
This script demonstrates a complete QLoRA fine-tuning pipeline using:
  - transformers (model loading, tokenization)
  - peft (LoRA configuration)
  - bitsandbytes (4-bit NF4 quantization)
  - trl (SFTTrainer for supervised fine-tuning)

WHY each library:
  - transformers: HuggingFace ecosystem for pre-trained models
  - peft: injects LoRA adapters without modifying base model architecture
  - bitsandbytes: custom CUDA kernels for 4-bit quantization/dequantization
  - trl: wraps the training loop with dataset formatting and memory tracking

Hardware target: Google Colab T4 (16GB VRAM) or local GPU with 8GB+ VRAM.
"""

# =============================================================================
# SECTION 0: INSTALLATION (run in Colab)
# =============================================================================
# Uncomment these lines in a fresh Colab environment:
# !pip install -q transformers accelerate peft bitsandbytes trl datasets

import torch
import gc
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import Dataset

# =============================================================================
# SECTION 1: CONFIGURATION
# =============================================================================
# We use a small model (TinyLlama-1.1B) so the script runs on modest hardware.
# For real tasks, swap to "meta-llama/Llama-2-7b-hf" or "mistralai/Mistral-7B-v0.1".

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # 1.1B params, fits everywhere
# MODEL_NAME = "meta-llama/Llama-2-7b-hf"  # Uncomment for 7B (needs 8GB+ with QLoRA)

MAX_SEQ_LENGTH = 512
LORA_R = 16           # LoRA rank; higher = more capacity, more memory
LORA_ALPHA = 32       # Scaling factor; typical rule: alpha = 2*r
LORA_DROPOUT = 0.05   # Regularization on adapter weights

print("="*60)
print("Phase 65: QLoRA Real-Workflow (Colab / GPU)")
print("="*60)
print(f"Model: {MODEL_NAME}")
print(f"LoRA rank r={LORA_R}, alpha={LORA_ALPHA}")

# =============================================================================
# SECTION 2: BITSANDBYTES 4-BIT CONFIGURATION
# =============================================================================
# WHY 4-bit NF4: Neural network weights are approximately normally distributed.
# NF4 places more quantization levels near zero, where most weights live.
# WHY double quantization: The scale factors themselves are compressed,
# saving another ~0.5 bits per weight on average.
# WHY compute_dtype=float16: Matmuls happen in FP16 for speed; only storage is 4-bit.

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,                        # Enable 4-bit loading
    bnb_4bit_quant_type="nf4",                # Normal Float 4-bit (better than uniform)
    bnb_4bit_compute_dtype=torch.float16,     # Dequantize to FP16 for compute
    bnb_4bit_use_double_quant=True,           # Quantize the quantization constants too
)

print("\nBitsAndBytesConfig:")
print(f"  load_in_4bit=True")
print(f"  quant_type=nf4")
print(f"  compute_dtype=float16")
print(f"  use_double_quant=True")

# =============================================================================
# SECTION 3: LOAD MODEL IN 4-BIT
# =============================================================================
# WHY device_map="auto": Automatically shards layers across available GPUs
# and offloads to CPU if necessary. Essential for multi-GPU or limited VRAM.
# WHY torch_dtype=torch.float16: Even with 4-bit weights, the model wrapper
# and activations use FP16 to match the compute dtype.

print("\n--- Loading model in 4-bit ---")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token  # Required for batching

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",                        # Auto-dispatch layers to GPU/CPU
    torch_dtype=torch.float16,
    trust_remote_code=True,
)

# Enable gradient checkpointing BEFORE adding LoRA.
# WHY: Gradient checkpointing reduces activation memory by ~50%.
# Without it, activations (not weights) become the memory bottleneck.
model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)

# Print memory usage
if torch.cuda.is_available():
    mem_alloc = torch.cuda.memory_allocated() / 1024**3
    mem_reserved = torch.cuda.memory_reserved() / 1024**3
    print(f"GPU memory allocated:  {mem_alloc:.2f} GB")
    print(f"GPU memory reserved:   {mem_reserved:.2f} GB")

# =============================================================================
# SECTION 4: LORA CONFIGURATION
# =============================================================================
# WHY target_modules: We inject LoRA into attention and projection layers.
# These layers capture the most task-relevant features.
# WHY bias="none": Biases add negligible capacity but increase memory.
# WHY task_type="CAUSAL_LM": Tells PEFT the model is an autoregressive LM.

lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# =============================================================================
# SECTION 5: PREPARE DATASET
# =============================================================================
# WHY instruction format: Chat models expect a specific template.
# We format each sample as: <|user|> prompt <|assistant|> response
# WHY small dataset: For demo purposes. Replace with your own JSON/CSV.

train_data = [
    {"instruction": "What is QLoRA?", "response": "QLoRA is a memory-efficient fine-tuning method that stores the base model in 4-bit precision while training small LoRA adapters in full precision."},
    {"instruction": "Explain gradient checkpointing.", "response": "Gradient checkpointing trades compute for memory by storing only a subset of activations and recomputing the rest during backpropagation."},
    {"instruction": "What is 4-bit quantization?", "response": "4-bit quantization compresses model weights to 4 bits per parameter using formats like NF4, reducing memory by 4-8x."},
    {"instruction": "Why use BitsAndBytes?", "response": "BitsAndBytes provides optimized CUDA kernels for 4-bit and 8-bit quantization, enabling large models to run on consumer GPUs."},
    {"instruction": "How does LoRA save memory?", "response": "LoRA freezes the base model and trains only low-rank decomposition matrices, reducing trainable parameters by 100-1000x."},
    {"instruction": "What is NF4?", "response": "NF4 is a non-uniform 4-bit quantization format that places more quantization levels near zero, matching the distribution of neural network weights."},
    {"instruction": "Explain double quantization.", "response": "Double quantization compresses the quantization constants themselves, adding another layer of memory savings on top of 4-bit weights."},
    {"instruction": "Can I fine-tune a 7B model on 8GB VRAM?", "response": "Yes, with QLoRA. The 4-bit base model uses ~4GB, leaving room for LoRA adapters, activations, and optimizer states."},
]

# Format for chat template
def format_example(example):
    text = f"<|user|>\n{example['instruction']}\n<|assistant|>\n{example['response']}\n"
    return {"text": text}

dataset = Dataset.from_list(train_data).map(format_example)

print(f"\nDataset: {len(dataset)} examples")
print(f"Example format:\n{dataset[0]['text'][:120]}...")

# =============================================================================
# SECTION 6: TRAINING ARGUMENTS
# =============================================================================
# WHY small batch: QLoRA is memory-efficient, but activations still consume VRAM.
# WHY gradient accumulation: Simulates larger batches without more memory.
# WHY warmup_steps: Stabilizes training in the first few updates.
# WHY fp16=True: Mixed-precision training for LoRA adapters (not the base model).
# WHY optim="paged_adamw_8bit": 8-bit AdamW with CPU paging for optimizer states.

training_args = TrainingArguments(
    output_dir="./qlora_output",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,            # Effective batch = 1 × 4 = 4
    warmup_steps=2,
    learning_rate=2e-4,
    fp16=True,                                # LoRA adapters train in FP16
    logging_steps=1,
    optim="paged_adamw_8bit",                 # 8-bit optimizer + CPU paging
    save_strategy="epoch",
    report_to="none",                         # Disable W&B for demo
)

# =============================================================================
# SECTION 7: SFT TRAINER
# =============================================================================
# WHY SFTTrainer: Handles dataset formatting, tokenization, and the training loop.
# It also handles padding and truncation to max_seq_length automatically.

print("\n--- Starting QLoRA training ---")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    args=training_args,
)

trainer.train()

# =============================================================================
# SECTION 8: MEMORY COMPARISON (4-bit vs. 16-bit)
# =============================================================================
# We cannot load the same model in FP16 in the same session (OOM),
# so we compute the theoretical memory usage.

print("\n--- Memory Comparison (Theoretical) ---")

n_params = model.get_base_model().num_parameters() if hasattr(model, 'get_base_model') else 1.1e9

# FP16 model: 2 bytes per param
mem_fp16_gb = (n_params * 2) / (1024**3)
# FP16 gradients: 2 bytes per param
grad_fp16_gb = (n_params * 2) / (1024**3)
# FP16 optimizer states (Adam): 2 momentum + 2 variance = 4 bytes per param
opt_fp16_gb = (n_params * 4) / (1024**3)
total_fp16_gb = mem_fp16_gb + grad_fp16_gb + opt_fp16_gb

# QLoRA model: ~0.5 bytes per param (4-bit + double quant overhead)
mem_qlora_gb = (n_params * 0.5) / (1024**3)
# LoRA adapters in FP16: negligible (~0.1% of base)
lora_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
lora_gb = (lora_params * 6) / (1024**3)  # params + grad + adam states
# Activations: roughly same, but checkpointing cuts them by ~50%
# We ignore activations for this theoretical comparison
total_qlora_gb = mem_qlora_gb + lora_gb

print(f"Model parameters: {n_params/1e9:.2f}B")
print(f"LoRA parameters:  {lora_params:,} ({100*lora_params/n_params:.4f}%)")
print("")
print(f"{'Component':<25} {'FP16 Fine-Tune':<18} {'QLoRA':<18}")
print("-" * 65)
print(f"{'Model weights':<25} {mem_fp16_gb:>8.2f} GB        {mem_qlora_gb:>8.2f} GB")
print(f"{'Gradients':<25} {grad_fp16_gb:>8.2f} GB        {'~0 (frozen)':>18}")
print(f"{'Optimizer states':<25} {opt_fp16_gb:>8.2f} GB        {lora_gb:>8.2f} GB")
print(f"{'Total (weights+opt)':<25} {total_fp16_gb:>8.2f} GB        {total_qlora_gb:>8.2f} GB")
print(f"{'Reduction':<25} {'':>18}  {total_fp16_gb/total_qlora_gb:>8.1f}×")

# =============================================================================
# SECTION 9: SAVE ADAPTER AND MERGE
# =============================================================================
# WHY save adapter only: The adapter is tiny (MBs). You can share and swap it.
# WHY merge: For inference speed, merge LoRA into the dequantized base weights.
# Merging removes the LoRA overhead but loses 4-bit compression (model becomes FP16).

print("\n--- Saving ---")
adapter_path = "./qlora_adapter"
model.save_pretrained(adapter_path)
print(f"LoRA adapter saved to: {adapter_path}")

# Optional: merge and save full model
# WARNING: This loads the base model in FP16 and adds LoRA, so it uses ~2-4GB.
# Uncomment only if you have enough VRAM.
# print("\n--- Merging adapter into base model ---")
# merged_model = model.merge_and_unload()
# merged_path = "./qlora_merged"
# merged_model.save_pretrained(merged_path)
# tokenizer.save_pretrained(merged_path)
# print(f"Merged model saved to: {merged_path}")

# =============================================================================
# SECTION 10: GENERATION TEST
# =============================================================================
# Test the fine-tuned model on a prompt related to the training data.

print("\n--- Generation Test ---")
prompt = "<|user|>\nWhat is QLoRA?\n<|assistant|>\n"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

model.eval()
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=80,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id,
    )

generated = tokenizer.decode(outputs[0], skip_special_tokens=False)
print(f"Prompt: {prompt.strip()}")
print(f"Output: {generated[len(prompt):].strip()}")

# =============================================================================
# SECTION 11: CLEANUP
# =============================================================================

del trainer, model
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()

print("\n" + "="*60)
print("QLoRA training complete.")
print("="*60)
print("Key takeaways:")
print("  - Base model in 4-bit NF4 (~4-8x memory reduction)")
print("  - LoRA adapters in FP16 (trainable, tiny)")
print("  - Gradient checkpointing saves activation memory")
print("  - Paged 8-bit AdamW saves optimizer state memory")
print("  - Fine-tune 7B models on 8GB GPUs, 70B on 48GB GPUs")

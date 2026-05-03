#!/usr/bin/env python3
"""
Phase 64: Practical SFT with LoRA — Colab Real-Workflow Script
================================================================
Run this on Google Colab T4 GPU to execute real LoRA fine-tuning.

Steps:
  1. Install dependencies (transformers, peft, trl, datasets)
  2. Load a small open-source model (TinyLlama or GPT-2)
  3. Prepare instruction-following data
  4. Configure LoRA (rank, alpha, target_modules, dropout)
  5. Run supervised fine-tuning with TRL/SFTTrainer
  6. Merge adapters into base model for inference
  7. Compare before/after outputs
  8. Save adapter weights

Usage:
  Upload to Colab, set runtime to GPU (T4), run all cells.
"""

# =============================================================================
# CELL 1: Install Dependencies
# =============================================================================
# !pip install transformers peft trl datasets accelerate bitsandbytes --quiet

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, PeftModel
from trl import SFTTrainer
from datasets import Dataset
import numpy as np

print("="*60)
print("Phase 64: Real LoRA Fine-Tuning")
print("="*60)
print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# =============================================================================
# CELL 2: Load Base Model and Tokenizer
# =============================================================================
# We use a small model for fast training on T4.
# Options: "gpt2" (124M), "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "HuggingFaceTB/SmolLM-135M"

model_name = "gpt2"  # Fast, fits on T4
print(f"\nLoading model: {model_name}")

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

print(f"Model params: {sum(p.numel() for p in model.parameters())/1e6:.1f}M")

# =============================================================================
# CELL 3: Prepare Instruction Data
# =============================================================================
# Toy dataset for demonstration. In practice, use Alpaca, ShareGPT, or your own.

raw_data = [
    {"instruction": "What is the capital of France?", "response": "The capital of France is Paris."},
    {"instruction": "What is 2+2?", "response": "2+2 equals 4."},
    {"instruction": "Who wrote Romeo and Juliet?", "response": "William Shakespeare wrote Romeo and Juliet."},
    {"instruction": "What is photosynthesis?", "response": "Photosynthesis is the process by which plants convert light energy into chemical energy."},
    {"instruction": "What is the speed of light?", "response": "The speed of light in a vacuum is approximately 299,792,458 meters per second."},
    {"instruction": "What is machine learning?", "response": "Machine learning is a branch of artificial intelligence where systems learn from data."},
    {"instruction": "What is the boiling point of water?", "response": "Water boils at 100 degrees Celsius at standard pressure."},
    {"instruction": "Who painted the Mona Lisa?", "response": "Leonardo da Vinci painted the Mona Lisa."},
    {"instruction": "What is DNA?", "response": "DNA is a molecule that carries genetic instructions for development and function."},
    {"instruction": "What is gravity?", "response": "Gravity is a force that attracts objects with mass toward each other."},
]

# Format with chat template (GPT-2 uses simple concatenation)
def format_example(ex):
    text = f"Question: {ex['instruction']}\nAnswer: {ex['response']}{tokenizer.eos_token}"
    return {"text": text}

dataset = Dataset.from_list([format_example(ex) for ex in raw_data])
print(f"\nDataset: {len(dataset)} examples")
print(f"Example:\n{dataset[0]['text']}")

# =============================================================================
# CELL 4: Configure LoRA
# =============================================================================

lora_config = LoraConfig(
    r=8,                          # LoRA rank
    lora_alpha=16,                # Scaling factor (usually 2×r)
    target_modules=["c_attn"],    # GPT-2 attention projection
    lora_dropout=0.05,            # Dropout for regularization
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# =============================================================================
# CELL 5: Training Arguments
# =============================================================================

training_args = TrainingArguments(
    output_dir="/content/lora_output",
    num_train_epochs=10,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=5,
    save_strategy="no",
    fp16=True,
    report_to="none"
)

# =============================================================================
# CELL 6: Run SFT
# =============================================================================

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=128
)

print("\nStarting training...")
trainer.train()
print("Training complete!")

# =============================================================================
# CELL 7: Compare Before and After
# =============================================================================

def generate(prompt, model, tokenizer, max_length=50):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=max_length, do_sample=False)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

test_prompt = "Question: What is the capital of France?\nAnswer:"

# Current model (with LoRA)
print("\n--- After LoRA SFT ---")
print(generate(test_prompt, model, tokenizer))

# =============================================================================
# CELL 8: Merge Adapters for Efficient Inference
# =============================================================================
# Merging adapters into base weights removes LoRA overhead at inference.

print("\n--- Merging Adapters ---")
merged_model = model.merge_and_unload()
print("Adapters merged into base model!")

# Save merged model
merged_model.save_pretrained("/content/merged_model")
tokenizer.save_pretrained("/content/merged_model")
print("Saved merged model to /content/merged_model")

# =============================================================================
# CELL 9: Save Adapter Only (for sharing)
# =============================================================================

model.save_pretrained("/content/lora_adapter")
print("\nSaved LoRA adapter to /content/lora_adapter")
print("Adapter size is ~MBs. Share this instead of the full model.")

# =============================================================================
# CELL 10: Summary
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("LoRA fine-tuning complete:")
print("  - Base model: GPT-2 (124M params)")
print("  - LoRA rank: 8")
print("  - Trainable: <1% of parameters")
print("  - Data: 10 instruction-response pairs")
print("  - Output: /content/lora_adapter (small file)")
print("  - Merged: /content/merged_model (full model)")
print("\nNext: Phase 65 - QLoRA for training larger models on limited memory")

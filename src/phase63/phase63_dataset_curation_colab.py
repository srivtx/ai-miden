#!/usr/bin/env python3
"""
Phase 63: Dataset Curation for Fine-Tuning — Colab Real-Workflow Script
=======================================================================
Run this on Google Colab T4 GPU to execute a real fine-tuning data pipeline.

Steps:
  1. Install dependencies (transformers, datasets)
  2. Create/load an instruction dataset
  3. Apply a real chat template (Llama-3 or Mistral style)
  4. Tokenize with truncation and padding
  5. Pack sequences for efficient training
  6. Build a PyTorch DataLoader
  7. Print statistics and save processed dataset

Usage:
  Upload to Colab, set runtime to GPU (T4), run all cells.
"""

# =============================================================================
# CELL 1: Install Dependencies
# =============================================================================
# !pip install transformers datasets torch --quiet

import torch
from transformers import AutoTokenizer
from datasets import Dataset
import numpy as np

print("="*60)
print("Phase 63: Real Dataset Curation Pipeline")
print("="*60)
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# =============================================================================
# CELL 2: Create Instruction Dataset
# =============================================================================
# In practice, you would load from HuggingFace: datasets.load_dataset("tatsu-lab/alpaca")
# Here we create a tiny synthetic dataset for demonstration.

raw_examples = [
    {"instruction": "What is the capital of France?", "input": "", "output": "The capital of France is Paris."},
    {"instruction": "Solve the equation:", "input": "2x + 4 = 10", "output": "Subtract 4 from both sides: 2x = 6. Divide by 2: x = 3."},
    {"instruction": "Explain photosynthesis in one sentence.", "input": "", "output": "Photosynthesis is the process by which plants convert light energy into chemical energy."},
    {"instruction": "Translate to French:", "input": "Hello, how are you?", "output": "Bonjour, comment allez-vous?"},
    {"instruction": "What is 15 × 7?", "input": "", "output": "15 × 7 = 105."},
    {"instruction": "Write a haiku about the ocean.", "input": "", "output": "Waves crash on the shore.\nEndless blue horizon calls.\nSalt wind fills my lungs."},
    {"instruction": "Who wrote 'Romeo and Juliet'?", "input": "", "output": "William Shakespeare wrote 'Romeo and Juliet' around 1597."},
    {"instruction": "What is the speed of light?", "input": "", "output": "The speed of light in a vacuum is approximately 299,792,458 meters per second."},
    {"instruction": "Define machine learning.", "input": "", "output": "Machine learning is a branch of artificial intelligence where systems learn patterns from data without being explicitly programmed."},
    {"instruction": "What is the boiling point of water?", "input": "", "output": "Water boils at 100 degrees Celsius (212 degrees Fahrenheit) at standard atmospheric pressure."},
]

print(f"\nCreated dataset with {len(raw_examples)} examples")

# =============================================================================
# CELL 3: Apply Chat Template
# =============================================================================
# We use a small open model's tokenizer to demonstrate real chat template behavior.
# For this demo, we use 'HuggingFaceTB/SmolLM-135M' (tiny, fast, real chat template).

model_name = "HuggingFaceTB/SmolLM-135M"
print(f"\nLoading tokenizer: {model_name}")
tokenizer = AutoTokenizer.from_pretrained(model_name)

# If the tokenizer has a pad token, use it; otherwise set to eos
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

def format_example(ex):
    """Format as a conversation and apply the model's chat template."""
    messages = [
        {"role": "user", "content": ex["instruction"] + ("\n" + ex["input"] if ex["input"] else "")},
        {"role": "assistant", "content": ex["output"]},
    ]
    # apply_chat_template returns a string with special tokens
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return {"text": text}

formatted = [format_example(ex) for ex in raw_examples]
print(f"\n--- Chat Template Example ---")
print(formatted[0]["text"])

# =============================================================================
# CELL 4: Tokenize
# =============================================================================

max_length = 128  # small for demo; real training uses 2048-4096

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=max_length,
        padding="max_length",  # for demo; real training uses padding="longest" or packing
        return_tensors=None,
    )

# Convert to HuggingFace Dataset
dataset = Dataset.from_list(formatted)
tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

print(f"\n--- Tokenization Stats ---")
lengths = [sum(attn == 1 for attn in ex["attention_mask"]) for ex in tokenized_dataset]
print(f"Sequences: {len(tokenized_dataset)}")
print(f"Context window: {max_length}")
print(f"Mean length: {np.mean(lengths):.1f} tokens")
print(f"Median length: {np.median(lengths):.1f} tokens")
print(f"Max length: {max(lengths)} tokens")
print(f"Min length: {min(lengths)} tokens")

# =============================================================================
# CELL 5: Sequence Packing (Real Implementation)
# =============================================================================
# Instead of padding each example to max_length, we concatenate examples
# and split into chunks of max_length. This is how real pre-training works.

print("\n--- Sequence Packing ---")

# Concatenate all token IDs
all_input_ids = []
all_attention_masks = []
for ex in tokenized_dataset:
    # Remove padding tokens (token ID = pad_token_id) for packing
    valid_tokens = [tok for tok, mask in zip(ex["input_ids"], ex["attention_mask"]) if mask == 1]
    all_input_ids.extend(valid_tokens)
    all_attention_masks.extend([1] * len(valid_tokens))
    # Add EOS token between examples to separate them
    all_input_ids.append(tokenizer.eos_token_id)
    all_attention_masks.append(1)

print(f"Total valid tokens: {len(all_input_ids)}")

# Split into chunks of max_length
packed_input_ids = []
packed_attention_masks = []
packed_labels = []

for i in range(0, len(all_input_ids), max_length):
    chunk_input = all_input_ids[i:i+max_length]
    chunk_attn = all_attention_masks[i:i+max_length]
    
    # Pad last chunk if needed
    if len(chunk_input) < max_length:
        chunk_input.extend([tokenizer.pad_token_id] * (max_length - len(chunk_input)))
        chunk_attn.extend([0] * (max_length - len(chunk_attn)))
    
    packed_input_ids.append(chunk_input)
    packed_attention_masks.append(chunk_attn)
    # Labels = input_ids for causal LM training (predict next token)
    packed_labels.append(chunk_input.copy())

print(f"Packed sequences: {len(packed_input_ids)}")
print(f"Total tokens: {len(packed_input_ids) * max_length}")
print(f"Useful tokens: {len(all_input_ids)}")
print(f"Padding tokens: {len(packed_input_ids) * max_length - len(all_input_ids)}")
print(f"Efficiency: {len(all_input_ids) / (len(packed_input_ids) * max_length) * 100:.1f}%")

# =============================================================================
# CELL 6: PyTorch DataLoader
# =============================================================================

class PackedDataset(torch.utils.data.Dataset):
    def __init__(self, input_ids, attention_masks, labels):
        self.input_ids = torch.tensor(input_ids, dtype=torch.long)
        self.attention_masks = torch.tensor(attention_masks, dtype=torch.long)
        self.labels = torch.tensor(labels, dtype=torch.long)
    
    def __len__(self):
        return len(self.input_ids)
    
    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_masks[idx],
            "labels": self.labels[idx],
        }

packed_dataset = PackedDataset(packed_input_ids, packed_attention_masks, packed_labels)
dataloader = torch.utils.data.DataLoader(packed_dataset, batch_size=2, shuffle=True)

print(f"\n--- DataLoader ---")
print(f"Dataset size: {len(packed_dataset)}")
print(f"Batch size: 2")
print(f"Batches per epoch: {len(dataloader)}")

# Show one batch
batch = next(iter(dataloader))
print(f"\nSample batch shapes:")
print(f"  input_ids: {batch['input_ids'].shape}")
print(f"  attention_mask: {batch['attention_mask'].shape}")
print(f"  labels: {batch['labels'].shape}")

# =============================================================================
# CELL 7: Save Processed Dataset
# =============================================================================

# Save for later use in fine-tuning
output_dir = "/content/processed_dataset"
import os
os.makedirs(output_dir, exist_ok=True)

torch.save({
    "input_ids": packed_dataset.input_ids,
    "attention_masks": packed_dataset.attention_masks,
    "labels": packed_dataset.labels,
}, f"{output_dir}/packed_data.pt")

print(f"\nSaved processed dataset to {output_dir}/packed_data.pt")

# Also save the tokenizer for consistency
tokenizer.save_pretrained(output_dir)
print(f"Saved tokenizer to {output_dir}")

# =============================================================================
# CELL 8: Summary
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Raw examples: {len(raw_examples)}")
print(f"Tokenized sequences (with padding): {len(tokenized_dataset)}")
print(f"Packed sequences (efficient): {len(packed_dataset)}")
print(f"Context window: {max_length}")
print(f"Packing efficiency: {len(all_input_ids) / (len(packed_input_ids) * max_length) * 100:.1f}%")
print("\nThis dataset is now ready for fine-tuning:")
print("  1. Data is formatted with the model's chat template")
print("  2. Tokenized with the model's tokenizer")
print("  3. Packed to maximize GPU utilization")
print("  4. Loaded into a PyTorch DataLoader")
print("\nNext: Phase 64 - Practical SFT with LoRA")
print("  Load this data into a training loop with LoRA adapters.")

"""
Phase 66: DPO & ORPO Colab Real-Workflow Script

Upload this to Google Colab with a T4 GPU.
Run the install cell first:
    !pip install transformers datasets trl accelerate

WHY: Local NumPy demos show the math, but real alignment happens on GPUs
with actual Transformer models. This script bridges the gap.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
)
from trl import DPOTrainer

# WHY: ORPOTrainer is newer than DPOTrainer. We guard the import so the
# script fails with a helpful message if the user has an old TRL version.
try:
    from trl import ORPOTrainer
except ImportError:
    raise ImportError(
        "ORPOTrainer not found. Upgrade TRL: pip install -U trl>=0.9.0"
    )

import torch

# ---------------------------------------------------------------------------
# 1. CREATE PREFERENCE DATASET
# WHY: DPO and ORPO need (prompt, chosen, rejected) triplets. We build a tiny
# dataset so the demo runs in minutes on a T4. In production you would use
# thousands of human-labeled comparisons.
# ---------------------------------------------------------------------------
preference_data = [
    {
        "prompt": "What is the capital of France?",
        "chosen": "The capital of France is Paris.",
        "rejected": "The capital of France is Berlin.",
    },
    {
        "prompt": "Explain gravity in one sentence.",
        "chosen": "Gravity is the force that attracts two bodies toward each other.",
        "rejected": "Gravity is just a theory invented by scientists to scare people.",
    },
    {
        "prompt": "How do I bake chocolate chip cookies?",
        "chosen": (
            "Mix flour, butter, sugar, eggs, and chocolate chips, "
            "then bake at 350F for 12 minutes."
        ),
        "rejected": "Throw random ingredients in an oven and hope for the best.",
    },
    {
        "prompt": "Write a haiku about the ocean.",
        "chosen": (
            "Waves kiss silent sand\n"
            "Salt air whispers ancient songs\n"
            "Moon pulls tides to sleep"
        ),
        "rejected": "The ocean is wet and big and blue and has fish.",
    },
    {
        "prompt": "What is 7 times 8?",
        "chosen": "7 times 8 equals 56.",
        "rejected": "7 times 8 is probably somewhere around 50.",
    },
]

dataset = Dataset.from_list(preference_data)

# ---------------------------------------------------------------------------
# 2. LOAD MODEL AND TOKENIZER
# WHY: GPT-2 is small (124M parameters) and trains quickly on Colab T4.
# We load the base model once for DPO and once fresh for ORPO so the
# comparison is fair (both start from the same pre-trained checkpoint).
# ---------------------------------------------------------------------------
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
# WHY: GPT-2 has no explicit pad token, so we reuse the EOS token.
tokenizer.pad_token = tokenizer.eos_token

# DPO needs a policy model AND a frozen reference model.
# WHY: The reference model provides the KL anchor that prevents the policy
# from drifting too far from coherent English.
dpo_model = AutoModelForCausalLM.from_pretrained(model_name)
ref_model = AutoModelForCausalLM.from_pretrained(model_name)

# ORPO only needs a policy model.
# WHY: ORPO uses odds ratios internally, so it does not need an external
# reference model. This saves GPU memory.
orpo_model = AutoModelForCausalLM.from_pretrained(model_name)

# ---------------------------------------------------------------------------
# 3. CONFIGURE TRAINING ARGUMENTS
# WHY: Tiny batch size and few steps keep the Colab demo fast. Increase
# these for real training runs.
# ---------------------------------------------------------------------------
training_args_dpo = TrainingArguments(
    output_dir="./dpo_output",
    num_train_epochs=1,
    per_device_train_batch_size=1,
    learning_rate=5e-5,
    logging_steps=1,
    save_strategy="no",
    report_to="none",
)

training_args_orpo = TrainingArguments(
    output_dir="./orpo_output",
    num_train_epochs=1,
    per_device_train_batch_size=1,
    learning_rate=5e-5,
    logging_steps=1,
    save_strategy="no",
    report_to="none",
)

# ---------------------------------------------------------------------------
# 4. TRAIN WITH DPO
# WHY: DPOTrainer handles tokenization, padding, the DPO loss, and gradient
# updates automatically. We only provide the model, reference, dataset, and
# beta (the temperature that controls divergence from the reference).
# ---------------------------------------------------------------------------
dpo_trainer = DPOTrainer(
    model=dpo_model,
    ref_model=ref_model,
    args=training_args_dpo,
    train_dataset=dataset,
    tokenizer=tokenizer,
    beta=0.1,  # WHY: beta controls divergence from reference. 0.1 is gentle.
)

print("Starting DPO training...")
dpo_trainer.train()
print("DPO training complete.")

# ---------------------------------------------------------------------------
# 5. TRAIN WITH ORPO
# WHY: ORPOTrainer combines SFT and preference loss in one pass.
# No ref_model argument is needed, which is why ORPO saves memory.
# ---------------------------------------------------------------------------
orpo_trainer = ORPOTrainer(
    model=orpo_model,
    args=training_args_orpo,
    train_dataset=dataset,
    tokenizer=tokenizer,
)

print("Starting ORPO training...")
orpo_trainer.train()
print("ORPO training complete.")

# ---------------------------------------------------------------------------
# 6. COMPARE OUTPUTS
# WHY: Numbers in the loss log are abstract. Generating text proves the
# model actually learned to prefer the chosen style over the rejected style.
# ---------------------------------------------------------------------------
test_prompt = "What is the capital of France?"


def generate(model, prompt, max_new_tokens=30):
    """Greedy decoding for reproducible comparison."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# WHY: Load a fresh base model on the same device for fair comparison.
device = "cuda" if torch.cuda.is_available() else "cpu"
base_model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
dpo_model = dpo_model.to(device)
orpo_model = orpo_model.to(device)

print("\n--- Generation Comparison ---")
print("Base model (no alignment):")
print(generate(base_model, test_prompt))

print("\nDPO model:")
print(generate(dpo_model, test_prompt))

print("\nORPO model:")
print(generate(orpo_model, test_prompt))

# ---------------------------------------------------------------------------
# 7. PLOT LOSS CURVES
# WHY: TRL logs losses to a history object. We extract them and plot so the
# student can see DPO and ORPO convergence patterns side-by-side.
# ---------------------------------------------------------------------------
dpo_logs = [log["loss"] for log in dpo_trainer.state.log_history if "loss" in log]
orpo_logs = [log["loss"] for log in orpo_trainer.state.log_history if "loss" in log]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(dpo_logs, color="blue")
axes[0].set_title("DPO Training Loss")
axes[0].set_xlabel("Step")
axes[0].set_ylabel("Loss")
axes[0].grid(True, alpha=0.3)

axes[1].plot(orpo_logs, color="green")
axes[1].set_title("ORPO Training Loss")
axes[1].set_xlabel("Step")
axes[1].set_ylabel("Loss")
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("src/phase66/dpo_orpo_colab_losses.png")
print("\nSaved loss curves to src/phase66/dpo_orpo_colab_losses.png")

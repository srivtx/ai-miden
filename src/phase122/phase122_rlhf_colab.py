#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 122 — Full RLHF Pipeline (Reward Model + PPO)
Designed for Google Colab T4 (16GB VRAM)
Runtime -> Change runtime type -> GPU -> T4
This script uses REAL models and ACTUALLY TRAINS them

Install dependencies (run in first Colab cell):
!pip install -q transformers datasets torch accelerate bitsandbytes matplotlib tqdm trl peft
"""

# =============================================================================
# SECTION 0: IMPORTS AND SETUP
# =============================================================================
# Every import is chosen for a specific purpose in the RLHF pipeline.

import os
import math
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, PeftModel, prepare_model_for_kbit_training
from datasets import load_dataset, Dataset
from trl import PPOTrainer, PPOConfig
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm

# Verify GPU. T4 provides ~16GB VRAM. We will load models in 4-bit to fit.
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")
if device.type == 'cuda':
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# Seeds make the synthetic preference generation reproducible.
torch.manual_seed(122)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(122)
random.seed(122)

# =============================================================================
# SHARED CONFIGURATION
# =============================================================================
# We keep the model small and sequences short so everything fits on T4.

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
MAX_SEQ_LEN = 256
MAX_NEW_TOKENS = 64
BATCH_SIZE = 1
GRAD_ACCUM = 4

# 4-bit quantization config: NF4 with double quantization minimizes memory
# while preserving enough precision for LoRA training.
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# LoRA configuration: we target all linear projection layers so the adapters
# have enough capacity to shift behavior without training full weights.
lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
)

# Tokenizer setup. Qwen2.5 uses a chat template that we must apply correctly.
print("\nLoading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"  # left padding is required for decoder-only generation

# =============================================================================
# HELPER: LOAD BASE MODEL
# =============================================================================
# We wrap model loading so we can reload it cleanly between stages.
# `prepare_model_for_kbit_training` enables gradient checkpointing and handles
# layer norm freezing, which are essential for stable 4-bit fine-tuning.

def load_base_model():
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    model = prepare_model_for_kbit_training(model)
    return model

def load_base_model_for_rm():
    # Reward model uses sequence classification head (scalar output).
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=1,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    model = prepare_model_for_kbit_training(model)
    # Ensure the model outputs a scalar score, not classification logits.
    model.config.problem_type = "regression"
    return model

# =============================================================================
# SECTION 1: DATASET PREPARATION
# =============================================================================
# We use UltraChat for instruction data. Only 1000 examples are needed for
# this demonstration. We extract the first user message as the prompt and
# format the full conversation for SFT.

print("\n" + "="*60)
print("SECTION 1: Loading UltraChat dataset")
print("="*60)

dataset = load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft")
dataset = dataset.select(range(1000))
print(f"Selected {len(dataset)} examples")

def format_sft_example(example):
    """Apply chat template to the full conversation for SFT."""
    text = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}

def extract_prompt(example):
    """Extract the first user message as a standalone prompt."""
    user_msgs = [m for m in example["messages"] if m["role"] == "user"]
    if len(user_msgs) == 0:
        return {"prompt": ""}
    prompt = tokenizer.apply_chat_template(
        [user_msgs[0]],
        tokenize=False,
        add_generation_prompt=True,
    )
    return {"prompt": prompt}

sft_dataset = dataset.map(format_sft_example, remove_columns=dataset.column_names)
prompt_dataset = dataset.map(extract_prompt, remove_columns=dataset.column_names)
prompts = [p for p in prompt_dataset["prompt"] if len(p) > 0]
print(f"Valid prompts extracted: {len(prompts)}")

# =============================================================================
# SECTION 2: STAGE 1 — SUPERVISED FINE-TUNING (SFT)
# =============================================================================
# We fine-tune Qwen2.5-3B on instruction data for 100 steps. LoRA makes this
# possible on a T4 by training less than 1% of parameters. The goal is to
# teach the model the instruction-following format before RL optimization.

print("\n" + "="*60)
print("SECTION 2: Stage 1 — SFT")
print("="*60)

sft_model = load_base_model()
sft_model = get_peft_model(sft_model, lora_config)
sft_model.print_trainable_parameters()

# Tokenize SFT data
def tokenize_sft(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=MAX_SEQ_LEN,
        padding="max_length",
        return_tensors=None,
    )

tokenized_sft = sft_dataset.map(tokenize_sft, batched=True, remove_columns=sft_dataset.column_names)
tokenized_sft.set_format(type="torch", columns=["input_ids", "attention_mask"])

sft_dataloader = DataLoader(tokenized_sft, batch_size=BATCH_SIZE, shuffle=True)

sft_optimizer = torch.optim.AdamW(sft_model.parameters(), lr=2e-4, weight_decay=0.01)
sft_steps = 100
sft_loss_history = []

sft_model.train()
progress = tqdm(range(sft_steps), desc="SFT")

for step in progress:
    try:
        batch = next(sft_iter)
    except:
        sft_iter = iter(sft_dataloader)
        batch = next(sft_iter)

    input_ids = batch["input_ids"].to(device)
    attention_mask = batch["attention_mask"].to(device)

    # Forward pass with labels; the model computes causal LM loss internally.
    outputs = sft_model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
    loss = outputs.loss / GRAD_ACCUM
    loss.backward()

    if (step + 1) % GRAD_ACCUM == 0:
        torch.nn.utils.clip_grad_norm_(sft_model.parameters(), 1.0)
        sft_optimizer.step()
        sft_optimizer.zero_grad()

    sft_loss_history.append(loss.item() * GRAD_ACCUM)
    progress.set_postfix({"loss": f"{loss.item() * GRAD_ACCUM:.4f}"})

    if step % 50 == 0 and step > 0 and torch.cuda.is_available():
        torch.cuda.empty_cache()

# Save SFT adapter
sft_adapter_path = "./phase122_sft_adapter"
os.makedirs(sft_adapter_path, exist_ok=True)
sft_model.save_pretrained(sft_adapter_path)
print(f"\nSFT adapter saved to {sft_adapter_path}")

# Clean up SFT model to free VRAM for reward model generation.
del sft_model
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# =============================================================================
# SECTION 3: GENERATE SYNTHETIC PREFERENCE PAIRS
# =============================================================================
# Real human preferences are expensive. For this educational script, we
# generate two responses per prompt and label the longer one as preferred.
# Length correlates with coherence and detail in instruction-following.

print("\n" + "="*60)
print("SECTION 3: Generating synthetic preference pairs")
print("="*60)

# Reload SFT model for generation
sft_gen_model = load_base_model()
sft_gen_model = PeftModel.from_pretrained(sft_gen_model, sft_adapter_path)
sft_gen_model.eval()

n_pairs = 200
preference_pairs = []

with torch.no_grad():
    for i in tqdm(range(n_pairs), desc="Generating pairs"):
        prompt = prompts[i % len(prompts)]
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)

        # Generate two responses with different sampling
        outputs_a = sft_gen_model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
        )
        outputs_b = sft_gen_model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=1.0,
            top_p=0.95,
            pad_token_id=tokenizer.pad_token_id,
        )

        resp_a = tokenizer.decode(outputs_a[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        resp_b = tokenizer.decode(outputs_b[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        # Heuristic: prefer longer response as proxy for detail/coherence.
        # In production this is replaced by human annotators.
        if len(resp_a) >= len(resp_b):
            chosen, rejected = resp_a, resp_b
        else:
            chosen, rejected = resp_b, resp_a

        preference_pairs.append({
            "prompt": prompt,
            "chosen": chosen,
            "rejected": rejected,
        })

print(f"Generated {len(preference_pairs)} preference pairs")
print("Example chosen:", preference_pairs[0]["chosen"][:100])
print("Example rejected:", preference_pairs[0]["rejected"][:100])

# Clean up generation model
del sft_gen_model
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# =============================================================================
# SECTION 4: STAGE 2 — REWARD MODEL TRAINING
# =============================================================================
# The reward model learns to score completions using the Bradley-Terry model.
# We concatenate prompt + completion, pass through the model, and use the
# scalar logit as the score. Training minimizes -log(sigmoid(score_chosen - score_rejected)).

print("\n" + "="*60)
print("SECTION 4: Stage 2 — Reward Model Training")
print("="*60)

rm_model = load_base_model_for_rm()
rm_model = get_peft_model(rm_model, lora_config)
rm_model.print_trainable_parameters()

# Tokenize preference pairs for the reward model.
# We truncate to MAX_SEQ_LEN to avoid OOM.

def tokenize_pair(example):
    chosen_text = example["prompt"] + example["chosen"]
    rejected_text = example["prompt"] + example["rejected"]
    chosen_enc = tokenizer(chosen_text, truncation=True, max_length=MAX_SEQ_LEN, padding="max_length")
    rejected_enc = tokenizer(rejected_text, truncation=True, max_length=MAX_SEQ_LEN, padding="max_length")
    return {
        "chosen_input_ids": chosen_enc["input_ids"],
        "chosen_attention_mask": chosen_enc["attention_mask"],
        "rejected_input_ids": rejected_enc["input_ids"],
        "rejected_attention_mask": rejected_enc["attention_mask"],
    }

rm_dataset = Dataset.from_list(preference_pairs)
rm_dataset = rm_dataset.map(tokenize_pair, remove_columns=rm_dataset.column_names)
rm_dataset.set_format(type="torch", columns=["chosen_input_ids", "chosen_attention_mask", "rejected_input_ids", "rejected_attention_mask"])

rm_dataloader = DataLoader(rm_dataset, batch_size=BATCH_SIZE, shuffle=True)
rm_optimizer = torch.optim.AdamW(rm_model.parameters(), lr=1e-4, weight_decay=0.01)

rm_steps = 100
rm_loss_history = []
rm_acc_history = []

rm_model.train()
progress = tqdm(range(rm_steps), desc="RM")

for step in progress:
    try:
        batch = next(rm_iter)
    except:
        rm_iter = iter(rm_dataloader)
        batch = next(rm_iter)

    # Score chosen completions
    chosen_out = rm_model(
        input_ids=batch["chosen_input_ids"].to(device),
        attention_mask=batch["chosen_attention_mask"].to(device),
    )
    chosen_scores = chosen_out.logits.squeeze()

    # Score rejected completions
    rejected_out = rm_model(
        input_ids=batch["rejected_input_ids"].to(device),
        attention_mask=batch["rejected_attention_mask"].to(device),
    )
    rejected_scores = rejected_out.logits.squeeze()

    # Bradley-Terry pairwise loss
    loss = -torch.log(torch.sigmoid(chosen_scores - rejected_scores) + 1e-8).mean()
    loss.backward()

    if (step + 1) % GRAD_ACCUM == 0:
        torch.nn.utils.clip_grad_norm_(rm_model.parameters(), 1.0)
        rm_optimizer.step()
        rm_optimizer.zero_grad()

    # Accuracy: how often does the model rank chosen above rejected?
    with torch.no_grad():
        acc = (chosen_scores > rejected_scores).float().mean().item()

    rm_loss_history.append(loss.item())
    rm_acc_history.append(acc)
    progress.set_postfix({"loss": f"{loss.item():.4f}", "acc": f"{acc:.3f}"})

    if step % 50 == 0 and step > 0 and torch.cuda.is_available():
        torch.cuda.empty_cache()

# Save RM adapter
rm_adapter_path = "./phase122_rm_adapter"
os.makedirs(rm_adapter_path, exist_ok=True)
rm_model.save_pretrained(rm_adapter_path)
print(f"\nRM adapter saved to {rm_adapter_path}")

del rm_model
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# =============================================================================
# SECTION 5: STAGE 3 — PPO OPTIMIZATION WITH TRL
# =============================================================================
# We now optimize the SFT policy using PPO. The policy generates responses,
# the RM scores them, and PPO updates the policy with a clipped surrogate
# objective plus a KL penalty to prevent drift from the SFT checkpoint.

print("\n" + "="*60)
print("SECTION 5: Stage 3 — PPO with TRL")
print("="*60)

# Load policy (SFT checkpoint) and reference model (base, no adapter)
policy_base = load_base_model()
policy_model = PeftModel.from_pretrained(policy_base, sft_adapter_path)

ref_base = load_base_model()
# Reference model stays frozen at the SFT checkpoint. We load the same adapter
# but do not train it, so it acts as a behavioral anchor.
ref_model = PeftModel.from_pretrained(ref_base, sft_adapter_path)
for param in ref_model.parameters():
    param.requires_grad = False

# Load RM for scoring
rm_base = load_base_model_for_rm()
rm_model = PeftModel.from_pretrained(rm_base, rm_adapter_path)
for param in rm_model.parameters():
    param.requires_grad = False
rm_model.eval()

# PPO configuration from TRL. Mini-batch size 1 with gradient accumulation
# gives an effective batch of 4, which balances stability and memory.
ppo_config = PPOConfig(
    model_name=MODEL_NAME,
    learning_rate=1e-5,
    log_with=None,
    mini_batch_size=1,
    batch_size=BATCH_SIZE * GRAD_ACCUM,
    gradient_accumulation_steps=GRAD_ACCUM,
    ppo_epochs=1,
    clip_eps=0.2,
    kl_penalty="kl",
    adap_kl_ctrl=True,
    init_kl_coef=0.2,
    target_kl=0.1,
)

# Prepare queries as tokenized tensors
ppo_prompts = prompts[:100]  # use 100 prompts for PPO
query_tensors = [
    tokenizer.encode(p, return_tensors="pt", truncation=True, max_length=128)[0]
    for p in ppo_prompts
]

ppo_trainer = PPOTrainer(
    config=ppo_config,
    model=policy_model,
    ref_model=ref_model,
    tokenizer=tokenizer,
)

ppo_reward_history = []
ppo_kl_history = []
ppo_steps = 50

progress = tqdm(range(ppo_steps), desc="PPO")

for step in progress:
    # Sample a mini-batch of queries
    batch_indices = random.sample(range(len(query_tensors)), BATCH_SIZE * GRAD_ACCUM)
    batch_queries = [query_tensors[i] for i in batch_indices]

    # Generate responses with the current policy
    response_tensors = ppo_trainer.generate(
        batch_queries,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=0.8,
        top_p=0.9,
        pad_token_id=tokenizer.pad_token_id,
    )

    # Score each (query, response) pair with the RM
    rewards = []
    for q, r in zip(batch_queries, response_tensors):
        full_ids = torch.cat([q, r]).unsqueeze(0).to(device)
        with torch.no_grad():
            score = rm_model(full_ids).logits.squeeze()
        rewards.append(score)

    # PPO step: updates policy with clipped surrogate objective and KL penalty
    stats = ppo_trainer.step(batch_queries, response_tensors, rewards)

    # Track metrics
    avg_reward = torch.stack(rewards).mean().item()
    ppo_reward_history.append(avg_reward)
    kl = stats.get('objective/kl', 0)
    ppo_kl_history.append(kl)

    progress.set_postfix({
        "reward": f"{avg_reward:.3f}",
        "kl": f"{kl:.4f}",
    })

    if step % 25 == 0 and step > 0 and torch.cuda.is_available():
        torch.cuda.empty_cache()

# =============================================================================
# SECTION 6: BEFORE/AFTER SAMPLE GENERATION
# =============================================================================
# We compare the SFT policy (before PPO) against the PPO-optimized policy
# on the same prompts to show qualitative improvement.

print("\n" + "="*60)
print("SECTION 6: Sample comparison — SFT vs PPO")
print("="*60)

test_prompts = ppo_prompts[:3]

# Generate with PPO policy (current state of policy_model)
policy_model.eval()
with torch.no_grad():
    for i, prompt in enumerate(test_prompts):
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)
        outputs = policy_model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
        )
        ppo_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        print(f"\nPrompt {i+1}: {prompt[:80]}...")
        print(f"PPO response: {ppo_text[:200]}")

# Generate with reference (SFT) model for comparison
ref_model.eval()
with torch.no_grad():
    for i, prompt in enumerate(test_prompts):
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)
        outputs = ref_model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
        )
        sft_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        print(f"SFT response: {sft_text[:200]}")

# =============================================================================
# SECTION 7: PLOTS
# =============================================================================
# We save diagnostic plots for all three stages so students can analyze the
# full RLHF pipeline in one view.

print("\n" + "="*60)
print("SECTION 7: Saving plots")
print("="*60)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# SFT loss
ax = axes[0, 0]
ax.plot(sft_loss_history, color="#3498db", linewidth=1.5)
ax.set_xlabel("SFT Step")
ax.set_ylabel("Loss")
ax.set_title("Stage 1: SFT Loss Curve")
ax.grid(True, alpha=0.3)

# RM accuracy
ax = axes[0, 1]
ax.plot(rm_acc_history, color="#27ae60", linewidth=1.5)
ax.set_xlabel("RM Step")
ax.set_ylabel("Pairwise Accuracy")
ax.set_title("Stage 2: Reward Model Accuracy")
ax.grid(True, alpha=0.3)

# PPO reward
ax = axes[1, 0]
ax.plot(ppo_reward_history, color="#e74c3c", linewidth=1.5)
ax.set_xlabel("PPO Step")
ax.set_ylabel("Average Reward")
ax.set_title("Stage 3: PPO Reward Curve")
ax.grid(True, alpha=0.3)

# PPO KL divergence
ax = axes[1, 1]
ax.plot(ppo_kl_history, color="#9b59b6", linewidth=1.5)
ax.set_xlabel("PPO Step")
ax.set_ylabel("KL Divergence")
ax.set_title("KL Divergence from SFT Reference")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plot_path = "phase122_rlhf_plots.png"
plt.savefig(plot_path, dpi=150)
print(f"Saved plots to {plot_path}")

# =============================================================================
# SECTION 8: FINAL SUMMARY
# =============================================================================
print("\n" + "="*60)
print("FINAL SUMMARY")
print("="*60)
print(f"SFT initial loss:     {sft_loss_history[0]:.4f}")
print(f"SFT final loss:       {sft_loss_history[-1]:.4f}")
print(f"RM initial accuracy:  {rm_acc_history[0]:.3f}")
print(f"RM final accuracy:    {rm_acc_history[-1]:.3f}")
print(f"PPO initial reward:   {ppo_reward_history[0]:.3f}")
print(f"PPO final reward:     {ppo_reward_history[-1]:.3f}")
print(f"PPO final KL:         {ppo_kl_history[-1]:.4f}")
print(f"SFT adapter:          {sft_adapter_path}")
print(f"RM adapter:           {rm_adapter_path}")
print("\nKey insights:")
print("  1. SFT establishes a coherent instruction-following baseline")
print("  2. The RM learns to discriminate preferences from synthetic pairs")
print("  3. PPO increases reward while KL penalty prevents policy drift")
print("  4. Even synthetic preferences demonstrate the full RLHF mechanics")
print("  5. In production, replace synthetic pairs with real human labels")

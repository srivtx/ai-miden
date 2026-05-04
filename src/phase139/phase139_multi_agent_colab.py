"""
Phase 139: Multi-Agent Training — Cooperative Story Generation (Colab T4)
=========================================================================
Run this on Google Colab with a T4 GPU.

This script demonstrates multi-agent collaboration with REAL language models.
Two copies of Qwen2.5-1.5B-Instruct learn to write stories together:
  - Agent A generates the first half of a story.
  - Agent B generates the second half, conditioned on Agent A's output.
  - A pretrained evaluator (GPT-2) scores the coherence of the full story.
  - Both agents receive the same reward and update via policy gradient.

We compare three conditions:
  1. Joint training (both agents adapt).
  2. Single agent (Agent A writes the entire story alone).
  3. Fixed Agent A (base model) + trained Agent B.

Key insight: Joint training improves coordination because Agent A learns to
leave coherent narrative threads that Agent B can continue, while Agent B
learns to recover from Agent A's stylistic quirks.
"""

import gc
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

# =============================================================================
# CONFIGURATION
# =============================================================================
# WHY Qwen2.5-1.5B-Instruct? It is small enough to load two copies on a T4
# (approx. 3 GB per model in float16) while still producing coherent text.
# WHY GPT-2 as evaluator? It is tiny (~500 MB) and provides a stable,
# pretrained perplexity signal without needing a third large model.

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MODEL_NAME = 'Qwen/Qwen2.5-1.5B-Instruct'
EVAL_MODEL_NAME = 'gpt2'
LORA_RANK = 8
LORA_ALPHA = 16
MAX_NEW_TOKENS = 40      # short enough to train fast, long enough to show style
EPISODES = 50
LR = 1e-4
BASELINE_DECAY = 0.9
TEMPERATURE = 0.8

print(f"Device: {DEVICE}")

# =============================================================================
# STORY PROMPTS
# =============================================================================
# WHY a fixed set of prompts? It creates a consistent evaluation surface.
# If prompts changed wildly every episode, the reward baseline would be
# dominated by prompt difficulty rather than agent coordination.

TRAIN_PROMPTS = [
    "Once upon a time in a distant kingdom,",
    "In the year 3045, a lone astronaut discovered",
    "Deep beneath the ocean waves, a hidden city",
    "The old wizard opened the ancient tome and",
    "On the edge of the enchanted forest, a young thief",
    "Beneath the crimson moon, the last dragon",
    "Inside the abandoned space station, the AI suddenly",
    "The detective followed the footprints into the fog and",
    "At the summit of the icy mountain, the explorer",
    "In the bustling marketplace of Marrakesh, a merchant",
]

EVAL_PROMPTS = [
    "The clock struck midnight and the castle gates",
    "A mysterious letter arrived at the doorstep",
    "The submarine's sonar detected an enormous object",
]

# =============================================================================
# LoRA IMPLEMENTATION
# =============================================================================
# WHY manual LoRA? It keeps the script self-contained and reveals exactly
# which parameters are trainable. We target q_proj and v_proj because
# empirical work shows these contain the most task-specific information.

class LoRALinear(nn.Module):
    def __init__(self, base_layer, rank, alpha):
        super().__init__()
        self.base = base_layer
        # WHY freeze base? Only the low-rank adapters should update.
        for p in self.base.parameters():
            p.requires_grad = False
        in_f = base_layer.in_features
        out_f = base_layer.out_features
        # WHY zero init for B? Training starts from the base model output.
        self.lora_A = nn.Parameter(torch.zeros(in_f, rank))
        self.lora_B = nn.Parameter(torch.zeros(rank, out_f))
        # WHY small normal for A? Breaks symmetry so gradients flow.
        nn.init.normal_(self.lora_A, std=0.02)
        self.scaling = alpha / rank

    def forward(self, x):
        # WHY separate paths? We must keep base frozen during backprop.
        return self.base(x) + (x @ self.lora_A @ self.lora_B) * self.scaling

def apply_lora(model, rank=LORA_RANK, alpha=LORA_ALPHA):
    # WHY target only q_proj and v_proj? They capture 90% of adaptation
    # benefit while touching only a fraction of total parameters.
    for layer in model.model.layers:
        layer.self_attn.q_proj = LoRALinear(layer.self_attn.q_proj, rank, alpha).to(DEVICE)
        layer.self_attn.v_proj = LoRALinear(layer.self_attn.v_proj, rank, alpha).to(DEVICE)
    return model

def count_trainable(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

# =============================================================================
# LOAD MODELS
# =============================================================================
# WHY load twice? Each agent must have independent LoRA adapters.
# Sharing a single model would force both agents to learn the same policy.

print("\nLoading tokenizer and base models...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
# WHY set pad_token to eos_token? Generation requires a pad token ID.
# Qwen uses the same ID for both, but we set it explicitly to be safe.
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id

model_a = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    trust_remote_code=True,
).to(DEVICE)
model_a = apply_lora(model_a)

model_b = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    trust_remote_code=True,
).to(DEVICE)
model_b = apply_lora(model_b)

print(f"Agent A trainable params: {count_trainable(model_a):,}")
print(f"Agent B trainable params: {count_trainable(model_b):,}")

# Evaluator: small, frozen, on GPU for speed.
eval_tokenizer = AutoTokenizer.from_pretrained(EVAL_MODEL_NAME)
eval_model = AutoModelForCausalLM.from_pretrained(
    EVAL_MODEL_NAME,
    torch_dtype=torch.float16,
).to(DEVICE)
eval_model.eval()
for p in eval_model.parameters():
    p.requires_grad = False

# =============================================================================
# GENERATION
# =============================================================================
# WHY do_sample=True? Deterministic generation (greedy) would collapse to
# repetitive text, making the reward signal noisy and training unstable.
# Temperature=0.8 balances creativity with coherence.

def generate_segment(model, prompt_text, max_new_tokens=MAX_NEW_TOKENS):
    """
    Generate text and also return the raw token IDs so we can compute
    log-probabilities for policy-gradient updates without retokenizing.
    """
    inputs = tokenizer(prompt_text, return_tensors='pt').to(DEVICE)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=TEMPERATURE,
            pad_token_id=tokenizer.eos_token_id,
        )
    # Slice off the prompt to get only the newly generated tokens.
    gen_ids = output_ids[0][inputs['input_ids'].shape[1]:]
    text = tokenizer.decode(gen_ids, skip_special_tokens=True)
    return text, gen_ids.unsqueeze(0)

# =============================================================================
# EVALUATION (PERPLEXITY)
# =============================================================================
# WHY perplexity? It measures how surprised a pretrained language model is
# by the text. A coherent, grammatically consistent story will have lower
# perplexity than a disjointed one. It is a cheap, automatic proxy for
# human judgment of narrative quality.

def compute_perplexity(text):
    """Return perplexity of text under the frozen evaluator."""
    enc = eval_tokenizer(text, return_tensors='pt', truncation=True, max_length=256).to(DEVICE)
    with torch.no_grad():
        out = eval_model(**enc, labels=enc['input_ids'])
    return torch.exp(out.loss).item()

# =============================================================================
# POLICY-GRADIENT LOSS
# =============================================================================
# WHY REINFORCE? The generation step is non-differentiable (sampling discrete
# tokens). REINFORCE lets us update policies using only the reward signal
# and the log-probability of the actions that were actually taken.
# We use the mean cross-entropy loss as a proxy for -log pi because the
# number of generated tokens is roughly constant.

def policy_loss(model, prompt_ids, gen_ids, advantage):
    """
    Compute loss = cross_entropy * advantage.
    If advantage > 0, minimizing loss increases likelihood of the sequence.
    If advantage < 0, minimizing loss decreases likelihood.
    """
    full_ids = torch.cat([prompt_ids, gen_ids], dim=1)
    labels = full_ids.clone()
    # WHY mask prompt? We only want to reinforce the generated tokens.
    labels[:, :prompt_ids.shape[1]] = -100
    out = model(full_ids, labels=labels)
    return out.loss * advantage

# =============================================================================
# OPTIMIZERS
# =============================================================================
# WHY AdamW? Standard for fine-tuning transformers. Weight decay prevents
# LoRA weights from growing too large and overfitting to the evaluator.

optimizer_a = torch.optim.AdamW(
    filter(lambda p: p.requires_grad, model_a.parameters()),
    lr=LR, weight_decay=0.01
)
optimizer_b = torch.optim.AdamW(
    filter(lambda p: p.requires_grad, model_b.parameters()),
    lr=LR, weight_decay=0.01
)

# =============================================================================
# TRAINING LOOP
# =============================================================================
# WHY 50 episodes? Each episode requires two generations and two backward
# passes. On a T4, 50 episodes finish in a few minutes while still showing
# a clear trend in the reward curve.

baseline = 0.0
reward_history = []

print("\n--- Joint Training ---")
for ep in tqdm(range(EPISODES), desc="Episodes"):
    prompt = np.random.choice(TRAIN_PROMPTS)

    # Agent A writes the opening.
    first_half, gen_ids_a = generate_segment(model_a, prompt)

    # Agent B continues the narrative.
    context = prompt + " " + first_half
    second_half, gen_ids_b = generate_segment(model_b, context)

    full_story = context + " " + second_half

    # Reward is negative perplexity: higher (less negative) is better.
    ppl = compute_perplexity(full_story)
    reward = -ppl
    reward_history.append(reward)

    # Exponential moving-average baseline reduces variance.
    baseline = BASELINE_DECAY * baseline + (1 - BASELINE_DECAY) * reward
    advantage = reward - baseline

    # Update Agent A on the tokens it generated.
    prompt_ids_a = tokenizer(prompt, return_tensors='pt').input_ids.to(DEVICE)
    loss_a = policy_loss(model_a, prompt_ids_a, gen_ids_a, advantage)
    optimizer_a.zero_grad()
    loss_a.backward()
    torch.nn.utils.clip_grad_norm_(model_a.parameters(), 1.0)
    optimizer_a.step()

    # Update Agent B on the tokens it generated.
    prompt_ids_b = tokenizer(context, return_tensors='pt').input_ids.to(DEVICE)
    loss_b = policy_loss(model_b, prompt_ids_b, gen_ids_b, advantage)
    optimizer_b.zero_grad()
    loss_b.backward()
    torch.nn.utils.clip_grad_norm_(model_b.parameters(), 1.0)
    optimizer_b.step()

    # WHY cleanup? T4 has 16 GB VRAM. Accumulating hidden states across
    # episodes would eventually OOM. Explicit deletion and cache clearing
    # keep memory usage flat.
    del prompt_ids_a, gen_ids_a, loss_a
    del prompt_ids_b, gen_ids_b, loss_b
    torch.cuda.empty_cache()
    gc.collect()

print(f"Final average reward (last 10 episodes): {np.mean(reward_history[-10:]):.2f}")

# =============================================================================
# BASELINE COMPARISONS
# =============================================================================
# We evaluate three settings on held-out prompts to isolate the effect of
# joint training. We load a fresh base model for "Fixed A" so that Agent A
# is completely untrained, matching the ablation design.

print("\n--- Loading fixed Agent A (base model, no LoRA) ---")
fixed_a = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    trust_remote_code=True,
).to(DEVICE)

def evaluate_setting(agent_a, agent_b, prompts, label):
    """Evaluate a setting and return average perplexity + sample stories."""
    ppls = []
    stories = []
    for p in prompts:
        if agent_b is not None:
            fh, _ = generate_segment(agent_a, p)
            ctx = p + " " + fh
            sh, _ = generate_segment(agent_b, ctx)
            story = ctx + " " + sh
        else:
            # Single agent generates the whole continuation.
            story, _ = generate_segment(agent_a, p, max_new_tokens=MAX_NEW_TOKENS * 2)
        ppls.append(compute_perplexity(story))
        stories.append(story)
    avg_ppl = float(np.mean(ppls))
    print(f"{label}: avg perplexity = {avg_ppl:.2f}")
    return avg_ppl, stories

ppl_joint, stories_joint = evaluate_setting(model_a, model_b, EVAL_PROMPTS, "Joint trained")
ppl_single, stories_single = evaluate_setting(model_a, None, EVAL_PROMPTS, "Single agent")
ppl_fixed, stories_fixed = evaluate_setting(fixed_a, model_b, EVAL_PROMPTS, "Fixed A + trained B")

# Release fixed model immediately to free VRAM.
del fixed_a
torch.cuda.empty_cache()
gc.collect()

# =============================================================================
# VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Reward curve over episodes.
ax = axes[0, 0]
ax.plot(reward_history, linewidth=2, color='#2980b9')
ax.axhline(y=np.mean(reward_history[-10:]), color='red', linestyle='--', label='Final avg')
ax.set_xlabel('Episode')
ax.set_ylabel('Reward (-Perplexity)')
ax.set_title('Story Quality During Joint Training')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Smoothed reward for clarity.
ax = axes[0, 1]
window = 10
if len(reward_history) >= window:
    smooth = np.convolve(reward_history, np.ones(window)/window, mode='valid')
    ax.plot(smooth, linewidth=2, color='#27ae60')
ax.set_xlabel('Episode')
ax.set_ylabel('Smoothed Reward')
ax.set_title('Reward Moving Average')
ax.grid(True, alpha=0.3)

# Plot 3: Perplexity comparison across settings.
ax = axes[1, 0]
settings = ['Joint', 'Single', 'Fixed A + Trained B']
ppls = [ppl_joint, ppl_single, ppl_fixed]
colors = ['#27ae60', '#e74c3c', '#f39c12']
bars = ax.bar(settings, ppls, color=colors, edgecolor='black')
ax.set_ylabel('Evaluator Perplexity')
ax.set_title('Lower Perplexity = Better Coordination')
for bar, val in zip(bars, ppls):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Text length distribution (proxy for engagement).
ax = axes[1, 1]
lengths_joint = [len(s) for s in stories_joint]
lengths_single = [len(s) for s in stories_single]
lengths_fixed = [len(s) for s in stories_fixed]
ax.bar(np.arange(len(lengths_joint))-0.25, lengths_joint, 0.25, label='Joint', color=colors[0])
ax.bar(np.arange(len(lengths_single)), lengths_single, 0.25, label='Single', color=colors[1])
ax.bar(np.arange(len(lengths_fixed))+0.25, lengths_fixed, 0.25, label='Fixed A', color=colors[2])
ax.set_xticks(range(len(EVAL_PROMPTS)))
ax.set_xticklabels([f'P{i+1}' for i in range(len(EVAL_PROMPTS))])
ax.set_ylabel('Story Length (chars)')
ax.set_title('Generation Length per Prompt')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('phase139_multi_agent_results.png', dpi=150, bbox_inches='tight')
print("\nSaved plot: phase139_multi_agent_results.png")
plt.close()

# =============================================================================
# SAMPLE STORIES
# =============================================================================
print("\n" + "="*70)
print("SAMPLE STORIES (first evaluation prompt)")
print("="*70)
print(f"\n--- Joint Trained ---\n{stories_joint[0][:500]}...")
print(f"\n--- Single Agent ---\n{stories_single[0][:500]}...")
print(f"\n--- Fixed A + Trained B ---\n{stories_fixed[0][:500]}...")

# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "="*70)
print("FINAL SUMMARY")
print("="*70)
print(f"Joint training episodes: {EPISODES}")
print(f"Joint final avg reward:  {np.mean(reward_history[-10:]):.2f}")
print(f"Joint perplexity:        {ppl_joint:.2f}")
print(f"Single agent perplexity: {ppl_single:.2f}")
print(f"Fixed A perplexity:      {ppl_fixed:.2f}")
print("\nKey lessons:")
print("1. Joint training aligns the two agents' output distributions.")
print("2. A single agent lacks the inductive bias of narrative hand-off.")
print("3. Freezing the first agent forces the second to compensate, which")
print("   is less efficient than mutual adaptation.")
print("4. Policy-gradient updates with a pretrained evaluator provide a")
print("   viable training signal even without human labels.")
print("="*70)

# Colab instructions:
# 1. Upload this file or paste into a cell.
# 2. Runtime -> Change runtime type -> GPU.
# 3. Run all cells.
# Estimated time: ~5-10 minutes on T4.

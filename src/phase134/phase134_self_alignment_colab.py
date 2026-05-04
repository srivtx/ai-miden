# FRONTIER TRACK: Phase 134 — Self-Alignment / Iterative Self-Improvement
# Designed for Google Colab T4 (16GB VRAM)
# Runtime → Change runtime type → GPU → T4
# This script uses REAL models (Qwen/Qwen2.5-3B-Instruct)

# !pip install -q transformers torch accelerate peft trl datasets matplotlib tqdm

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer
from datasets import Dataset
import gc
import os

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# WHY: Qwen2.5-3B fits in FP16 on T4 (~6GB). LoRA keeps training memory low.
# -----------------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
N_PROMPTS = 100
MAX_NEW_TOKENS_GEN = 128
MAX_NEW_TOKENS_CRITIQUE = 96
MAX_NEW_TOKENS_REVISE = 128
N_ROUNDS = 3
N_SFT_STEPS = 50
LR = 2e-4
BATCH_SIZE = 1
GRAD_ACCUM = 4

# -----------------------------------------------------------------------------
# 2. LOAD MODEL AND TOKENIZER
# -----------------------------------------------------------------------------
print(f"\nLoading {MODEL_NAME} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)
print("Base model loaded.")

# -----------------------------------------------------------------------------
# 3. BUILD DIVERSE PROMPTS
# WHY: A diverse prompt set prevents overfitting to a narrow domain.
# -----------------------------------------------------------------------------

def build_prompts(n=100):
    templates = [
        "Explain the importance of {topic} in modern society.",
        "What are the main challenges facing {topic} today?",
        "Describe how {topic} has changed over the last decade.",
        "Why is {topic} controversial?",
        "Give three practical tips for {topic}.",
        "How does {topic} affect daily life?",
        "What would happen if {topic} disappeared tomorrow?",
        "Compare {topic} to a similar concept and explain the differences.",
        "What is the future of {topic}?",
        "Summarize the key debates around {topic}.",
    ]
    topics = [
        "artificial intelligence", "renewable energy", "public education",
        "space exploration", "mental health awareness", "remote work",
        "social media", "genetic engineering", "urban planning",
        "cryptocurrency", "climate policy", "autonomous vehicles",
        "universal basic income", "data privacy", "virtual reality",
        "plant-based diets", "quantum computing", "ocean conservation",
        "cybersecurity", "global trade",
    ]
    prompts = []
    for i in range(n):
        t = templates[i % len(templates)]
        topic = topics[i % len(topics)]
        prompts.append(t.format(topic=topic))
    return prompts


prompts = build_prompts(N_PROMPTS)
# Reserve first 20 for evaluation (held-out during training)
train_prompts = prompts[20:]
eval_prompts = prompts[:20]

print(f"Built {len(prompts)} prompts ({len(train_prompts)} train, {len(eval_prompts)} eval)")

# -----------------------------------------------------------------------------
# 4. GENERATION HELPERS
# WHY: We need clean generation, critique, and revision functions.
# -----------------------------------------------------------------------------

def generate_response(model, prompt, max_new_tokens=128):
    """Generate a single response for a prompt."""
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.8,
            top_p=0.95,
            pad_token_id=tokenizer.pad_token_id,
        )
    gen_text = tokenizer.decode(output_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
    del inputs, output_ids
    torch.cuda.empty_cache()
    return gen_text


def generate_critique(model, prompt, response):
    """Generate a critique of the given response."""
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
        {"role": "user", "content": "What is wrong with this answer? List specific issues."},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS_CRITIQUE,
            do_sample=True,
            temperature=0.8,
            top_p=0.95,
            pad_token_id=tokenizer.pad_token_id,
        )
    critique = tokenizer.decode(output_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
    del inputs, output_ids
    torch.cuda.empty_cache()
    return critique


def generate_revision(model, prompt, response, critique):
    """Generate a revised response based on the critique."""
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
        {"role": "user", "content": f"Critique of your answer: {critique}\n\nPlease provide a revised, improved answer."},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS_REVISE,
            do_sample=True,
            temperature=0.8,
            top_p=0.95,
            pad_token_id=tokenizer.pad_token_id,
        )
    revision = tokenizer.decode(output_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
    del inputs, output_ids
    torch.cuda.empty_cache()
    return revision


# -----------------------------------------------------------------------------
# 5. QUALITY EVALUATION
# WHY: We need a cheap, interpretable proxy for response quality.
# -----------------------------------------------------------------------------

def evaluate_quality(model, prompt, response):
    """
    Compute a composite quality score.
    Components:
      - Coherence: negative perplexity of the response (model's own loss)
      - Length: moderate length bonus (not too short)
      - Relevance: simple keyword overlap with prompt
    WHY: Perplexity measures coherence; length and relevance catch trivial outputs.
    """
    # Coherence: compute perplexity of the response text.
    full_text = response + tokenizer.eos_token
    inputs = tokenizer(full_text, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs.input_ids)
        loss = outputs.loss.item()
    perplexity = np.exp(loss)
    coherence = -perplexity  # lower perplexity is better

    # Length bonus: ideal around 100 tokens; penalize very short.
    n_tokens = len(tokenizer.encode(response))
    length_bonus = max(0, 1.0 - abs(n_tokens - 100) / 100.0)

    # Relevance: token overlap between prompt and response (excluding stopwords).
    prompt_words = set(prompt.lower().split())
    resp_words = set(response.lower().split())
    overlap = len(prompt_words & resp_words) / max(len(prompt_words), 1)

    # Normalize to roughly 0-1 scale.
    # Typical perplexity for good text is 5-15; scale coherence to ~0-1.
    coherence_norm = min(1.0, max(0.0, (20.0 - perplexity) / 20.0))
    score = 0.5 * coherence_norm + 0.25 * length_bonus + 0.25 * overlap
    return score, perplexity, n_tokens


def evaluate_prompts(model, prompt_list):
    """Evaluate quality on a list of prompts. Returns mean score and details."""
    scores = []
    perplexities = []
    for prompt in tqdm(prompt_list, desc="Evaluating"):
        resp = generate_response(model, prompt, max_new_tokens=96)
        score, ppl, _ = evaluate_quality(model, prompt, resp)
        scores.append(score)
        perplexities.append(ppl)
    return float(np.mean(scores)), float(np.mean(perplexities)), scores


# -----------------------------------------------------------------------------
# 6. FINE-TUNE WITH LORA
# WHY: Full fine-tuning of 3B parameters needs ~24GB VRAM. LoRA fits in ~8GB.
# -----------------------------------------------------------------------------

def train_on_revisions(base_model, revision_data, n_steps=50):
    """
    Fine-tune model on revised responses using LoRA.
    WHY: We return a new model so the caller can decide whether to keep it.
    """
    # Copy the base model so we do not mutate the caller's weights in-place.
    # WHY: Each round should start from the previous round's model, but we
    # need to re-attach LoRA adapters cleanly.
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    # If we have a previous adapter state, load it for continuity.
    # For simplicity in this educational script, we start fresh LoRA each round
    # on the base model, which is common in iterative self-improvement literature.

    # Format dataset
    texts = []
    for prompt, revision in revision_data:
        chat = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": revision},
        ]
        texts.append(tokenizer.apply_chat_template(chat, tokenize=False))

    dataset = Dataset.from_dict({"text": texts})

    training_args = TrainingArguments(
        output_dir="/content/self_align_output",
        num_train_epochs=1,
        max_steps=n_steps,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR,
        logging_steps=10,
        save_strategy="no",
        fp16=True,
        report_to="none",
        overwrite_output_dir=True,
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
        max_seq_length=256,
    )

    print(f"\nTraining for {n_steps} steps...")
    train_result = trainer.train()
    final_loss = train_result.training_loss if hasattr(train_result, 'training_loss') else train_result.metrics.get('train_loss', 0.0)

    # Extract the underlying model for inference (merge adapters)
    # WHY: Merging removes LoRA compute overhead during generation.
    merged = model.merge_and_unload()

    del model, trainer, dataset
    gc.collect()
    torch.cuda.empty_cache()
    return merged, final_loss


# -----------------------------------------------------------------------------
# 7. ITERATIVE SELF-IMPROVEMENT LOOP
# -----------------------------------------------------------------------------
round_quality = []
round_perplexity = []
round_losses = []
round_samples = []

current_model = base_model

for round_idx in range(1, N_ROUNDS + 1):
    print(f"\n{'='*60}")
    print(f"ROUND {round_idx}")
    print(f"{'='*60}")

    # -------------------------------------------------------------------------
    # 7a. GENERATE
    # -------------------------------------------------------------------------
    print("\n-- Generating responses --")
    responses = []
    for prompt in tqdm(train_prompts, desc="Generate"):
        resp = generate_response(current_model, prompt, max_new_tokens=MAX_NEW_TOKENS_GEN)
        responses.append(resp)

    # -------------------------------------------------------------------------
    # 7b. CRITIQUE
    # -------------------------------------------------------------------------
    print("\n-- Critiquing responses --")
    critiques = []
    for prompt, resp in tqdm(zip(train_prompts, responses), total=len(train_prompts), desc="Critique"):
        crit = generate_critique(current_model, prompt, resp)
        critiques.append(crit)

    # -------------------------------------------------------------------------
    # 7c. REVISE
    # -------------------------------------------------------------------------
    print("\n-- Revising responses --")
    revisions = []
    for prompt, resp, crit in tqdm(zip(train_prompts, responses, critiques), total=len(train_prompts), desc="Revise"):
        rev = generate_revision(current_model, prompt, resp, crit)
        revisions.append(rev)

    # -------------------------------------------------------------------------
    # 7d. TRAIN
    # -------------------------------------------------------------------------
    revision_data = list(zip(train_prompts, revisions))
    current_model, train_loss = train_on_revisions(base_model, revision_data, n_steps=N_SFT_STEPS)
    round_losses.append(train_loss)

    # -------------------------------------------------------------------------
    # 7e. EVALUATE
    # -------------------------------------------------------------------------
    print("\n-- Evaluating on held-out prompts --")
    mean_score, mean_ppl, _ = evaluate_prompts(current_model, eval_prompts)
    round_quality.append(mean_score)
    round_perplexity.append(mean_ppl)
    print(f"Round {round_idx} mean quality: {mean_score:.3f} | mean perplexity: {mean_ppl:.2f}")

    # Save a sample
    sample_prompt = eval_prompts[0]
    sample_resp = generate_response(current_model, sample_prompt, max_new_tokens=96)
    round_samples.append((sample_prompt, sample_resp))

# -----------------------------------------------------------------------------
# 8. SAMPLE RESPONSES PER ROUND
# WHY: Concrete examples show what "improvement" looks like subjectively.
# -----------------------------------------------------------------------------
print("\n" + "="*60)
print("SAMPLE RESPONSES FROM EACH ROUND")
print("="*60)
for i, (sp, sr) in enumerate(round_samples):
    print(f"\nRound {i+1} sample:")
    print(f"Prompt: {sp}")
    print(f"Response: {sr[:300]}...")

# -----------------------------------------------------------------------------
# 9. VISUALIZATION
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Quality
axes[0].plot(range(1, N_ROUNDS + 1), round_quality, marker='o', color='steelblue', linewidth=2)
axes[0].set_title('Quality Score per Round')
axes[0].set_xlabel('Round')
axes[0].set_ylabel('Mean Quality Score')
axes[0].set_ylim(0, 1)
axes[0].grid(True, linestyle='--', alpha=0.4)

# Perplexity
axes[1].plot(range(1, N_ROUNDS + 1), round_perplexity, marker='s', color='crimson', linewidth=2)
axes[1].set_title('Perplexity per Round')
axes[1].set_xlabel('Round')
axes[1].set_ylabel('Mean Perplexity')
axes[1].grid(True, linestyle='--', alpha=0.4)

# Training loss
axes[2].plot(range(1, N_ROUNDS + 1), round_losses, marker='^', color='forestgreen', linewidth=2)
axes[2].set_title('Final Training Loss per Round')
axes[2].set_xlabel('Round')
axes[2].set_ylabel('Loss')
axes[2].grid(True, linestyle='--', alpha=0.4)

plt.tight_layout()
plot_path = 'src/phase134/phase134_self_alignment_results.png'
os.makedirs(os.path.dirname(plot_path), exist_ok=True)
plt.savefig(plot_path, dpi=150)
plt.close()
print(f"\nPlot saved to {plot_path}")

# -----------------------------------------------------------------------------
# 10. CLEANUP
# -----------------------------------------------------------------------------
gc.collect()
torch.cuda.empty_cache()
print("\nDone.")

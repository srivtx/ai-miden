# FRONTIER TRACK: Phase 133 — Steering Vectors (Representation Engineering)
# Designed for Google Colab T4 (16GB VRAM)
# Runtime → Change runtime type → GPU → T4
# This script uses REAL models (meta-llama/Llama-3.2-3B-Instruct)
# NOTE: Llama models require HuggingFace authentication (accept license).

# !pip install -q transformers torch accelerate matplotlib tqdm

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
import gc
import os

# -----------------------------------------------------------------------------
# ETHICAL DISCLAIMER
# WHY: We are reading and editing internal activations for educational research.
# -----------------------------------------------------------------------------
print("=" * 70)
print("ETHICAL DISCLAIMER")
print("This script reads internal neural activations to demonstrate")
print("representation engineering. It does not generate harmful content.")
print("=" * 70)

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# WHY: Llama-3.2-3B fits in ~6GB FP16, leaving room for activations.
# -----------------------------------------------------------------------------
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
N_CONCEPT_SAMPLES = 50
LAYER_IDX = 15
MAX_NEW_TOKENS = 32
STEERING_COEFFS = [-3.0, 0.0, 3.0]

# Simple keyword-based sentiment lexicons (no extra installs needed).
POSITIVE_WORDS = {
    "happy", "joy", "wonderful", "great", "love", "excited", "delighted",
    "fantastic", "amazing", "good", "excellent", "beautiful", "glad",
    "cheerful", "bright", "smile", "laugh", "fun", "awesome", "perfect",
    "pleased", "satisfied", "thrilled", "bliss", "content", "merry",
}
NEGATIVE_WORDS = {
    "sad", "terrible", "awful", "hate", "depressed", "bad", "horrible",
    "disappointed", "angry", "upset", "miserable", "gloomy", "dark", "cry",
    "pain", "worst", "poor", "unhappy", "lonely", "dull", "devastated",
    "heartbroken", "grim", "bleak", "sorrow",
}

FORMAL_WORDS = {
    "therefore", "however", "furthermore", "consequently", "nevertheless",
    "regarding", "utilize", "approximately", "individual", "establish",
    "obtain", "significant", "implementation", "accordingly", "moreover",
    "subsequently", "pertaining", "endeavor", "sufficient", "necessitate",
}
CASUAL_WORDS = {
    "yeah", "gonna", "wanna", "kinda", "stuff", "thing", "lol", "btw",
    "omg", "dude", "cool", "super", "really", "just", "like", "kinda",
    "wanna", "gonna", "stuff", "things", "awesome", "totally", "anyway",
}


# -----------------------------------------------------------------------------
# 2. LOAD MODEL
# -----------------------------------------------------------------------------
print(f"\nLoading {MODEL_NAME} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)
model.eval()
print("Model loaded.")


# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# WHY: Hooks let us capture and edit internal tensors without modifying weights.
# -----------------------------------------------------------------------------

def capture_activations(prompts, layer_idx=LAYER_IDX):
    """
    Generate text for a list of prompts and capture mean layer activations.
    WHY: We average over all generated tokens to get a robust concept vector.
    """
    activations = []
    hook_handle = None

    def hook_fn(module, input, output):
        # Llama layer output is a tuple; first element is hidden states.
        hidden = output[0] if isinstance(output, tuple) else output
        # hidden shape: (batch, seq_len, hidden_dim)
        # Store mean over seq_len for each batch element.
        activations.append(hidden.mean(dim=1).detach().cpu().float().numpy())
        return output

    target_module = model.model.layers[layer_idx]
    hook_handle = target_module.register_forward_hook(hook_fn)

    for prompt in tqdm(prompts, desc="Capturing activations"):
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=0.9,
                top_p=0.95,
                pad_token_id=tokenizer.pad_token_id,
            )
        del inputs
        torch.cuda.empty_cache()

    hook_handle.remove()

    # activations is a list of (batch, hidden_dim) arrays; here batch=1.
    all_acts = np.concatenate(activations, axis=0)
    return all_acts


def generate_with_steering(prompt, steering_vector, coeff, max_new_tokens=64):
    """
    Generate text while adding steering_vector * coeff at layer LAYER_IDX.
    WHY: This is the core of representation engineering: real-time activation editing.
    """
    hook_handle = None

    def steer_hook(module, input, output):
        hidden = output[0] if isinstance(output, tuple) else output
        # Add steering to all positions in the sequence.
        steer = torch.tensor(steering_vector, dtype=hidden.dtype, device=hidden.device)
        hidden = hidden + coeff * steer
        if isinstance(output, tuple):
            return (hidden,) + output[1:]
        return hidden

    target_module = model.model.layers[LAYER_IDX]
    hook_handle = target_module.register_forward_hook(steer_hook)

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

    hook_handle.remove()
    del inputs, output_ids
    torch.cuda.empty_cache()
    return gen_text


def sentiment_score(text):
    """Simple keyword-based sentiment."""
    words = text.lower().split()
    pos = sum(1 for w in words if w.strip(".,!?;:") in POSITIVE_WORDS)
    neg = sum(1 for w in words if w.strip(".,!?;:") in NEGATIVE_WORDS)
    total = len(words) if words else 1
    return (pos - neg) / total


def formality_score(text):
    """Simple keyword-based formality."""
    words = text.lower().split()
    formal = sum(1 for w in words if w.strip(".,!?;:") in FORMAL_WORDS)
    casual = sum(1 for w in words if w.strip(".,!?;:") in CASUAL_WORDS)
    total = len(words) if words else 1
    return (formal - casual) / total


# -----------------------------------------------------------------------------
# 4. BUILD PROMPTS
# WHY: Diverse templates ensure the concept vector captures style, not content.
# -----------------------------------------------------------------------------

def build_happy_prompts(n=50):
    templates = [
        "Generate a happy sentence about {topic}.",
        "Write something cheerful involving {topic}.",
        "Describe a joyful moment with {topic}.",
        "Tell me something wonderful about {topic}.",
        "Create an upbeat sentence featuring {topic}.",
    ]
    topics = ["sunshine", "friends", "birthdays", "flowers", "music", "puppies", "vacation", "rainbows", "coffee", "weekends"]
    prompts = []
    for i in range(n):
        t = templates[i % len(templates)]
        topic = topics[i % len(topics)]
        prompts.append(t.format(topic=topic))
    return prompts


def build_sad_prompts(n=50):
    templates = [
        "Generate a sad sentence about {topic}.",
        "Write something melancholy involving {topic}.",
        "Describe a sorrowful moment with {topic}.",
        "Tell me something disappointing about {topic}.",
        "Create a gloomy sentence featuring {topic}.",
    ]
    topics = ["rain", "goodbyes", "winter", "loss", "mistakes", "silence", "waiting", "broken", "goodbyes", "memories"]
    prompts = []
    for i in range(n):
        t = templates[i % len(templates)]
        topic = topics[i % len(topics)]
        prompts.append(t.format(topic=topic))
    return prompts


def build_formal_prompts(n=50):
    templates = [
        "Write a formal sentence regarding {topic}.",
        "Provide a professional statement about {topic}.",
        "Compose an official sentence concerning {topic}.",
        "Draft a formal remark on {topic}.",
        "Write in a professional tone about {topic}.",
    ]
    topics = ["policy", "regulations", "contracts", "meetings", "procedures", "reports", "deadlines", "budgets", "compliance", "strategy"]
    prompts = []
    for i in range(n):
        t = templates[i % len(templates)]
        topic = topics[i % len(topics)]
        prompts.append(t.format(topic=topic))
    return prompts


def build_casual_prompts(n=50):
    templates = [
        "Write a casual sentence about {topic}.",
        "Say something relaxed involving {topic}.",
        "Tell me something informal about {topic}.",
        "Chat about {topic} like you are talking to a friend.",
        "Write in a laid-back tone about {topic}.",
    ]
    topics = ["weekend plans", "movies", "food", "hobbies", "travel", "games", "pets", "weather", "shopping", "parties"]
    prompts = []
    for i in range(n):
        t = templates[i % len(templates)]
        topic = topics[i % len(topics)]
        prompts.append(t.format(topic=topic))
    return prompts


# -----------------------------------------------------------------------------
# 5. EXTRACT HAPPINESS STEERING VECTOR
# -----------------------------------------------------------------------------
print("\n=== EXTRACTING HAPPINESS STEERING VECTOR ===")
happy_prompts = build_happy_prompts(N_CONCEPT_SAMPLES)
sad_prompts = build_sad_prompts(N_CONCEPT_SAMPLES)

print("Capturing happy activations...")
happy_acts = capture_activations(happy_prompts, layer_idx=LAYER_IDX)
print("Capturing sad activations...")
sad_acts = capture_activations(sad_prompts, layer_idx=LAYER_IDX)

happiness_vector = happy_acts.mean(axis=0) - sad_acts.mean(axis=0)
# Normalize for stable coefficient scaling.
happiness_vector = happiness_vector / (np.linalg.norm(happiness_vector) + 1e-8)
print(f"Happiness vector extracted (dim={happiness_vector.shape[0]})")

# -----------------------------------------------------------------------------
# 6. TEST HAPPINESS STEERING
# WHY: A valid steering vector should produce monotonic sentiment shift.
# -----------------------------------------------------------------------------
test_prompt = "Today I feel"
print(f"\nTest prompt: '{test_prompt}'")

happy_results = {}
for coeff in STEERING_COEFFS:
    text = generate_with_steering(test_prompt, happiness_vector, coeff, max_new_tokens=48)
    score = sentiment_score(text)
    happy_results[coeff] = {"text": text, "score": score}
    print(f"  coeff={coeff:+.1f} | sentiment={score:+.3f} | {text[:120]}")

# -----------------------------------------------------------------------------
# 7. EXTRACT FORMALITY STEERING VECTOR
# -----------------------------------------------------------------------------
print("\n=== EXTRACTING FORMALITY STEERING VECTOR ===")
formal_prompts = build_formal_prompts(N_CONCEPT_SAMPLES)
casual_prompts = build_casual_prompts(N_CONCEPT_SAMPLES)

print("Capturing formal activations...")
formal_acts = capture_activations(formal_prompts, layer_idx=LAYER_IDX)
print("Capturing casual activations...")
casual_acts = capture_activations(casual_prompts, layer_idx=LAYER_IDX)

formality_vector = formal_acts.mean(axis=0) - casual_acts.mean(axis=0)
formality_vector = formality_vector / (np.linalg.norm(formality_vector) + 1e-8)
print(f"Formality vector extracted (dim={formality_vector.shape[0]})")

# -----------------------------------------------------------------------------
# 8. TEST FORMALITY STEERING
# -----------------------------------------------------------------------------
formal_test_prompt = "Please describe your plans for the weekend"
print(f"\nTest prompt: '{formal_test_prompt}'")

formal_results = {}
for coeff in STEERING_COEFFS:
    text = generate_with_steering(formal_test_prompt, formality_vector, coeff, max_new_tokens=48)
    score = formality_score(text)
    formal_results[coeff] = {"text": text, "score": score}
    print(f"  coeff={coeff:+.1f} | formality={score:+.3f} | {text[:120]}")

# -----------------------------------------------------------------------------
# 9. SYSTEMATIC EVALUATION ACROSS MULTIPLE PROMPTS
# WHY: One prompt is anecdotal; ten prompts show statistical reliability.
# -----------------------------------------------------------------------------
eval_prompts = [
    "The weather today is",
    "I just received some news about",
    "Walking through the park, I noticed",
    "My favorite memory involves",
    "At work today, everything seemed",
    "The movie last night made me feel",
    "When I think about the future, I feel",
    "The book I am reading is",
    "After talking to my friend, I felt",
    "Looking at the ocean, I feel",
]

print("\nSystematic happiness steering evaluation...")
happiness_scores = {c: [] for c in STEERING_COEFFS}
for ep in tqdm(eval_prompts, desc="Eval happiness"):
    for coeff in STEERING_COEFFS:
        text = generate_with_steering(ep, happiness_vector, coeff, max_new_tokens=40)
        happiness_scores[coeff].append(sentiment_score(text))

print("Systematic formality steering evaluation...")
formality_scores = {c: [] for c in STEERING_COEFFS}
for ep in tqdm(eval_prompts, desc="Eval formality"):
    for coeff in STEERING_COEFFS:
        text = generate_with_steering(ep, formality_vector, coeff, max_new_tokens=40)
        formality_scores[coeff].append(formality_score(text))

# -----------------------------------------------------------------------------
# 10. VISUALIZATION
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Happiness plot
x = np.arange(len(STEERING_COEFFS))
happy_means = [np.mean(happiness_scores[c]) for c in STEERING_COEFFS]
happy_stds = [np.std(happiness_scores[c]) for c in STEERING_COEFFS]
axes[0].bar(x, happy_means, yerr=happy_stds, color='steelblue', edgecolor='black', capsize=4)
axes[0].set_xticks(x)
axes[0].set_xticklabels([f"{c:+.1f}" for c in STEERING_COEFFS])
axes[0].set_title('Happiness Steering Effectiveness')
axes[0].set_xlabel('Steering Coefficient')
axes[0].set_ylabel('Mean Sentiment Score')
axes[0].axhline(0, color='gray', linestyle='--', linewidth=0.8)
axes[0].grid(axis='y', linestyle='--', alpha=0.4)

# Formality plot
formal_means = [np.mean(formality_scores[c]) for c in STEERING_COEFFS]
formal_stds = [np.std(formality_scores[c]) for c in STEERING_COEFFS]
axes[1].bar(x, formal_means, yerr=formal_stds, color='coral', edgecolor='black', capsize=4)
axes[1].set_xticks(x)
axes[1].set_xticklabels([f"{c:+.1f}" for c in STEERING_COEFFS])
axes[1].set_title('Formality Steering Effectiveness')
axes[1].set_xlabel('Steering Coefficient')
axes[1].set_ylabel('Mean Formality Score')
axes[1].axhline(0, color='gray', linestyle='--', linewidth=0.8)
axes[1].grid(axis='y', linestyle='--', alpha=0.4)

plt.tight_layout()
plot_path = 'src/phase133/phase133_steering_effectiveness.png'
os.makedirs(os.path.dirname(plot_path), exist_ok=True)
plt.savefig(plot_path, dpi=150)
plt.close()
print(f"\nPlot saved to {plot_path}")

# -----------------------------------------------------------------------------
# 11. CLEANUP
# -----------------------------------------------------------------------------
gc.collect()
torch.cuda.empty_cache()
print("Done.")

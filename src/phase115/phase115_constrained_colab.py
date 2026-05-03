# FRONTIER TRACK: Phase 115 — Structured Generation and Constrained Decoding
# Designed for Google Colab T4 (16GB VRAM)
# Runtime → Change runtime type → GPU → T4
# This script uses REAL models (Llama-3.2-3B-Instruct)

# !pip install -q transformers datasets torch accelerate bitsandbytes matplotlib tqdm

import torch
import json
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

# -----------------------------------------------------------------------------
# 1. Load model and tokenizer
# -----------------------------------------------------------------------------
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_name = "meta-llama/Llama-3.2-3B-Instruct"
print(f"Loading {model_name} on {device} ...")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
)
model.eval()

# -----------------------------------------------------------------------------
# 2. Define a simple JSON schema as a character-level DFA
#    Schema: {"name": string, "age": int, "skills": [string]}
# -----------------------------------------------------------------------------
class JSONSchemaDFA:
    """Deterministic finite automaton for prefixes of our toy schema."""

    def __init__(self):
        self.states = {
            'S0', 'S1',
            'S_NAME_1', 'S_NAME_2', 'S_NAME_3', 'S_NAME_4', 'S_NAME_5', 'S_NAME_6',
            'S2', 'S3', 'S4', 'S5',
            'S_AGE_1', 'S_AGE_2', 'S_AGE_3', 'S_AGE_4', 'S_AGE_5',
            'S6', 'S7', 'S8', 'S9', 'S10',
            'S_SKILLS_1', 'S_SKILLS_2', 'S_SKILLS_3', 'S_SKILLS_4',
            'S_SKILLS_5', 'S_SKILLS_6', 'S_SKILLS_7', 'S_SKILLS_8',
            'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17', 'S18'
        }

    @staticmethod
    def transition(state, ch):
        ws = ' \t\n\r'
        if state == 'S0':
            if ch in ws:
                return 'S0'
            if ch == '{':
                return 'S1'
            return None
        if state == 'S1':
            if ch in ws:
                return 'S1'
            if ch == '"':
                return 'S_NAME_1'
            return None
        if state == 'S_NAME_1':
            if ch == 'n':
                return 'S_NAME_2'
            return None
        if state == 'S_NAME_2':
            if ch == 'a':
                return 'S_NAME_3'
            return None
        if state == 'S_NAME_3':
            if ch == 'm':
                return 'S_NAME_4'
            return None
        if state == 'S_NAME_4':
            if ch == 'e':
                return 'S_NAME_5'
            return None
        if state == 'S_NAME_5':
            if ch == '"':
                return 'S_NAME_6'
            return None
        if state == 'S_NAME_6':
            if ch in ws:
                return 'S_NAME_6'
            if ch == ':':
                return 'S2'
            return None
        if state == 'S2':
            if ch in ws:
                return 'S2'
            if ch == '"':
                return 'S3'
            return None
        if state == 'S3':
            # Inside the name string value
            if ch == '"':
                return 'S4'
            return 'S3'
        if state == 'S4':
            if ch in ws:
                return 'S4'
            if ch == ',':
                return 'S5'
            return None
        if state == 'S5':
            if ch in ws:
                return 'S5'
            if ch == '"':
                return 'S_AGE_1'
            return None
        if state == 'S_AGE_1':
            if ch == 'a':
                return 'S_AGE_2'
            return None
        if state == 'S_AGE_2':
            if ch == 'g':
                return 'S_AGE_3'
            return None
        if state == 'S_AGE_3':
            if ch == 'e':
                return 'S_AGE_4'
            return None
        if state == 'S_AGE_4':
            if ch == '"':
                return 'S_AGE_5'
            return None
        if state == 'S_AGE_5':
            if ch in ws:
                return 'S_AGE_5'
            if ch == ':':
                return 'S6'
            return None
        if state == 'S6':
            if ch in ws:
                return 'S6'
            if ch == '-' or ch.isdigit():
                return 'S7'
            return None
        if state == 'S7':
            if ch.isdigit():
                return 'S7'
            # Integer ended
            if ch in ws:
                return 'S8'
            if ch == ',':
                return 'S9'
            if ch == '}':
                return 'S18'
            return None
        if state == 'S8':
            if ch in ws:
                return 'S8'
            if ch == ',':
                return 'S9'
            if ch == '}':
                return 'S18'
            return None
        if state == 'S9':
            if ch in ws:
                return 'S9'
            if ch == '"':
                return 'S_SKILLS_1'
            return None
        if state == 'S_SKILLS_1':
            if ch == 's':
                return 'S_SKILLS_2'
            return None
        if state == 'S_SKILLS_2':
            if ch == 'k':
                return 'S_SKILLS_3'
            return None
        if state == 'S_SKILLS_3':
            if ch == 'i':
                return 'S_SKILLS_4'
            return None
        if state == 'S_SKILLS_4':
            if ch == 'l':
                return 'S_SKILLS_5'
            return None
        if state == 'S_SKILLS_5':
            if ch == 'l':
                return 'S_SKILLS_6'
            return None
        if state == 'S_SKILLS_6':
            if ch == 's':
                return 'S_SKILLS_7'
            return None
        if state == 'S_SKILLS_7':
            if ch == '"':
                return 'S_SKILLS_8'
            return None
        if state == 'S_SKILLS_8':
            if ch in ws:
                return 'S_SKILLS_8'
            if ch == ':':
                return 'S10'
            return None
        if state == 'S10':
            if ch in ws:
                return 'S10'
            if ch == '[':
                return 'S11'
            return None
        if state == 'S11':
            if ch in ws:
                return 'S11'
            if ch == '"':
                return 'S12'
            if ch == ']':
                return 'S16'
            return None
        if state == 'S12':
            # Inside a skill string
            if ch == '"':
                return 'S13'
            return 'S12'
        if state == 'S13':
            if ch in ws:
                return 'S13'
            if ch == ',':
                return 'S11'
            if ch == ']':
                return 'S16'
            return None
        if state == 'S16':
            if ch in ws:
                return 'S16'
            if ch == '}':
                return 'S18'
            return None
        if state == 'S18':
            if ch in ws:
                return 'S18'
            return None
        return None

    def run(self, s):
        """Run the DFA on string s. Returns final state or None if invalid."""
        state = 'S0'
        for ch in s:
            state = self.transition(state, ch)
            if state is None:
                return None
        return state


dfa = JSONSchemaDFA()

# -----------------------------------------------------------------------------
# 3. Precompute allowed token IDs for every DFA state
# -----------------------------------------------------------------------------
print("Precomputing allowed tokens for each DFA state (this may take ~30s) ...")
allowed_tokens_map = {state: [] for state in dfa.states}
vocab_size = tokenizer.vocab_size

for tid in tqdm(range(vocab_size), desc="Token mask precomputation"):
    token_str = tokenizer.decode([tid], skip_special_tokens=True)
    if not token_str:
        continue
    for state in dfa.states:
        s = state
        valid = True
        for ch in token_str:
            s = dfa.transition(s, ch)
            if s is None:
                valid = False
                break
        if valid:
            allowed_tokens_map[state].append(tid)

# Allow EOS token when the JSON object is complete
end_states = {'S18'}
for es in end_states:
    allowed_tokens_map[es].append(tokenizer.eos_token_id)

print("Precomputation done.")

# -----------------------------------------------------------------------------
# 4. Build prompt
# -----------------------------------------------------------------------------
user_prompt = "Output valid JSON"
messages = [{"role": "user", "content": user_prompt}]
input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(input_text, return_tensors='pt').to(model.device)
prompt_len = inputs.input_ids.shape[1]

# -----------------------------------------------------------------------------
# 5. Generation helper
# -----------------------------------------------------------------------------
def generate_one(constrained=False, max_new_tokens=80):
    """Generate a single sequence. Returns decoded generated text."""
    if constrained:

        def prefix_fn(batch_id, input_ids):
            # input_ids includes the prompt; only constrain generated tokens
            gen_ids = input_ids[prompt_len:]
            text = tokenizer.decode(gen_ids, skip_special_tokens=True)
            state = dfa.run(text)
            if state is None:
                # Should not happen with a correct mask, but fallback safely
                return [tokenizer.eos_token_id]
            allowed = allowed_tokens_map.get(state, [])
            # If we are in an end state, allow EOS so generation can stop
            if state in end_states:
                if tokenizer.eos_token_id not in allowed:
                    allowed = allowed + [tokenizer.eos_token_id]
            return allowed

        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,  # greedy for structured output
            prefix_allowed_tokens_fn=prefix_fn,
            pad_token_id=tokenizer.eos_token_id,
        )
    else:
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    gen_text = tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)
    return gen_text


# -----------------------------------------------------------------------------
# 6. Generate outputs
# -----------------------------------------------------------------------------
N = 50
print(f"\nGenerating {N} CONSTRAINED outputs ...")
t0 = time.time()
constrained_texts = [generate_one(constrained=True) for _ in tqdm(range(N), desc="Constrained")]
t_constrained = time.time() - t0

print(f"Generating {N} UNCONSTRAINED outputs ...")
t0 = time.time()
unconstrained_texts = [generate_one(constrained=False) for _ in tqdm(range(N), desc="Unconstrained")]
t_unconstrained = time.time() - t0

# -----------------------------------------------------------------------------
# 7. Parse and evaluate
# -----------------------------------------------------------------------------
def valid_json_rate(texts):
    valid = 0
    for t in texts:
        try:
            json.loads(t)
            valid += 1
        except Exception:
            pass
    return valid


constrained_valid = valid_json_rate(constrained_texts)
unconstrained_valid = valid_json_rate(unconstrained_texts)

print("\n=== RESULTS ===")
print(f"Constrained valid JSON: {constrained_valid}/{N} ({constrained_valid/N*100:.1f}%)")
print(f"Unconstrained valid JSON: {unconstrained_valid}/{N} ({unconstrained_valid/N*100:.1f}%)")
print(f"Constrained time: {t_constrained:.1f}s ({t_constrained/N*1000:.0f}ms per output)")
print(f"Unconstrained time: {t_unconstrained:.1f}s ({t_unconstrained/N*1000:.0f}ms per output)")

# Show examples
print("\n--- Constrained example ---")
print(constrained_texts[0][:200])
print("\n--- Unconstrained example (valid) ---")
for t in unconstrained_texts:
    try:
        json.loads(t)
        print(t[:200])
        break
    except Exception:
        pass
print("\n--- Unconstrained example (invalid) ---")
for t in unconstrained_texts:
    try:
        json.loads(t)
        continue
    except Exception:
        print(t[:200])
        break

# -----------------------------------------------------------------------------
# 8. Plot comparison
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

categories = ['Constrained', 'Unconstrained']
valid_counts = [constrained_valid, unconstrained_valid]
colors = ['green', 'orange']

axes[0].bar(categories, valid_counts, color=colors)
axes[0].set_ylim(0, N)
axes[0].set_title('Valid JSON Count')
axes[0].set_ylabel('Valid Outputs')

axes[1].bar(categories, [t_constrained/N*1000, t_unconstrained/N*1000], color=colors)
axes[1].set_title('Average Generation Time')
axes[1].set_ylabel('Milliseconds per Output')

plt.tight_layout()
plt.savefig('src/phase115/constraint_comparison.png')
plt.close()

print("\nPlot saved to src/phase115/constraint_comparison.png")

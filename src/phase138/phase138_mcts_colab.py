#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 138 — MCTS for Math Reasoning with Qwen2.5-3B
Designed for Google Colab T4 (16GB VRAM)
Runtime -> Change runtime type -> GPU -> T4
This script uses REAL models (Qwen/Qwen2.5-3B-Instruct)

What this script demonstrates:
  1. Load Qwen2.5-3B-Instruct and tokenizer
  2. Implement MCTS for reasoning on GSM8K-style math problems
     - Each node = partial reasoning chain
     - Expand: generate next reasoning step
     - Simulate: complete to final answer with greedy decoding
     - Score: check if answer is correct
     - Backprop: update value estimates
  3. Run MCTS for 20 iterations
  4. Compare with:
     - Greedy decoding (1 sample)
     - Best-of-8 (8 random samples)
     - MCTS (20 iterations, ~8 full completions)
  5. Show MCTS finds correct answers more efficiently

Why Qwen2.5-3B? It is instruction-tuned, fits on a T4, and performs well
on grade-school math. The GSM8K task is verifiable, making it ideal for
MCTS with a simple correctness checker.
"""

# ---------------------------------------------------------------------------
# INSTALL DEPENDENCIES
# ---------------------------------------------------------------------------
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                       "transformers", "torch", "matplotlib", "tqdm", "accelerate"])

import os
import gc
import random
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ---------------------------------------------------------------------------
# REPRODUCIBILITY
# ---------------------------------------------------------------------------
SEED = 138
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
MAX_NEW_TOKENS = 128
TEMPERATURE = 0.7

# A small set of GSM8K-style problems for T4 speed
MATH_PROBLEMS = [
    ("Janet buys a box of cookies for $4. She buys 3 boxes. How much does she spend?", 12),
    ("A train travels 60 miles per hour for 2 hours. How far does it go?", 120),
    ("Tom has 15 apples. He gives 3 to his friend and buys 5 more. How many does he have?", 17),
    ("A rectangle is 5 meters long and 3 meters wide. What is its area?", 15),
    ("A baker makes 24 cupcakes. She sells them in boxes of 4. How many boxes does she need?", 6),
    ("Lisa reads 10 pages per day. How many pages does she read in 7 days?", 70),
    ("A store sells pencils in packs of 12. If a class needs 48 pencils, how many packs should they buy?", 4),
    ("A car uses 1 gallon of gas every 25 miles. How many gallons does it use for 100 miles?", 4),
]

print(f"Device: {DEVICE}")
print(f"Model: {MODEL_NAME}")

# ---------------------------------------------------------------------------
# LOAD MODEL AND TOKENIZER
# ---------------------------------------------------------------------------
print("\nLoading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)
model.eval()

# ---------------------------------------------------------------------------
# HELPER: GENERATION AND PARSING
# ---------------------------------------------------------------------------

def generate_text(prompt, max_new_tokens=MAX_NEW_TOKENS, temperature=TEMPERATURE,
                  do_sample=True, stop_phrases=None):
    """
    Generate text from the model. We manually stop at common reasoning
    terminators to keep rollouts short and focused.
    """
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        output_ids = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature if do_sample else 1.0,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = tokenizer.decode(output_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

    # Manual stopping
    if stop_phrases:
        for phrase in stop_phrases:
            idx = generated.find(phrase)
            if idx != -1:
                generated = generated[:idx]
                break
    return generated.strip()


def extract_number(text):
    """
    Extract the last number from the text. This is a simple heuristic
    for parsing GSM8K answers. We look for digits, possibly with commas.
    """
    # Remove commas inside numbers
    text = text.replace(',', '')
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[-1])
    return None


def is_correct(answer_text, correct_answer):
    """Check if the extracted number matches the ground truth."""
    num = extract_number(answer_text)
    if num is None:
        return False
    return num == correct_answer


# ---------------------------------------------------------------------------
# MCTS NODE AND TREE
# ---------------------------------------------------------------------------
class ReasoningNode:
    def __init__(self, text, parent=None):
        self.text = text  # partial reasoning chain
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.is_expanded = False

    def ucb1(self, exploration_constant=1.414):
        if self.visits == 0:
            return float('inf')
        parent_visits = self.parent.visits if self.parent else 1
        avg_reward = self.value / self.visits
        exploration = exploration_constant * np.sqrt(np.log(parent_visits) / self.visits)
        return avg_reward + exploration

    def best_child(self):
        if not self.children:
            return None
        return max(self.children, key=lambda c: c.ucb1())

    def backprop(self, reward):
        self.visits += 1
        self.value += reward
        if self.parent:
            self.parent.backprop(reward)


def run_mcts_for_problem(problem_text, correct_answer, iterations=20,
                         expansion_branching=2):
    """
    Run MCTS for a single math problem.
    Each node is a partial reasoning chain (string).
    Expansion generates the next reasoning step.
    Simulation completes to a final answer with greedy decoding.
    """
    root_prompt = f"Solve this step by step:\n{problem_text}\n"
    root = ReasoningNode(root_prompt)

    for _ in tqdm(range(iterations), desc="MCTS iterations", leave=False):
        # --- Selection ---
        node = root
        while node.is_expanded and node.children:
            node = node.best_child()

        # --- Expansion ---
        if not node.is_expanded:
            node.is_expanded = True
            # Generate K continuations (reasoning steps)
            for _ in range(expansion_branching):
                continuation = generate_text(
                    node.text,
                    max_new_tokens=40,
                    temperature=0.7,
                    do_sample=True,
                    stop_phrases=["\n\n", "The answer is", "####"]
                )
                if continuation:
                    child_text = node.text + " " + continuation
                    node.children.append(ReasoningNode(child_text, parent=node))

        # Pick a child to simulate (if any were created)
        if node.children:
            sim_node = random.choice(node.children)
        else:
            sim_node = node

        # --- Simulation ---
        # Complete the reasoning chain to a final answer with greedy decoding
        final_prompt = sim_node.text + "\nThe answer is"
        final_answer_text = generate_text(
            final_prompt,
            max_new_tokens=20,
            temperature=1.0,
            do_sample=False,
        )

        # --- Scoring ---
        reward = 1.0 if is_correct(final_answer_text, correct_answer) else 0.0

        # --- Backpropagation ---
        sim_node.backprop(reward)

    return root


def get_best_answer_from_tree(root, correct_answer):
    """
    Traverse the tree to find the node with highest average reward,
    then complete it to a final answer.
    """
    node = root
    while node.children:
        node = max(node.children, key=lambda c: c.value / c.visits if c.visits > 0 else 0)
    final_prompt = node.text + "\nThe answer is"
    final_answer_text = generate_text(final_prompt, max_new_tokens=20, do_sample=False)
    return final_answer_text, is_correct(final_answer_text, correct_answer)


# ---------------------------------------------------------------------------
# GREEDY DECODING BASELINE
# ---------------------------------------------------------------------------
def run_greedy(problem_text, correct_answer):
    prompt = f"Solve this step by step:\n{problem_text}\n"
    text = generate_text(prompt, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    correct = is_correct(text, correct_answer)
    return text, correct


# ---------------------------------------------------------------------------
# BEST-OF-N BASELINE
# ---------------------------------------------------------------------------
def run_best_of_n(problem_text, correct_answer, n=8):
    prompt = f"Solve this step by step:\n{problem_text}\n"
    best_text = None
    best_correct = False
    for _ in range(n):
        text = generate_text(prompt, max_new_tokens=MAX_NEW_TOKENS, do_sample=True, temperature=0.7)
        correct = is_correct(text, correct_answer)
        if correct:
            return text, True
        if best_text is None:
            best_text = text
            best_correct = correct
    return best_text, best_correct


# ---------------------------------------------------------------------------
# RUN ALL METHODS ON ALL PROBLEMS
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Running experiments on {} problems".format(len(MATH_PROBLEMS)))
print("=" * 70)

greedy_correct = []
best8_correct = []
mcts_correct = []

for idx, (problem, answer) in enumerate(MATH_PROBLEMS, 1):
    print(f"\n--- Problem {idx}/{len(MATH_PROBLEMS)} ---")
    print(f"Problem: {problem}")
    print(f"Correct answer: {answer}")

    # Greedy
    g_text, g_corr = run_greedy(problem, answer)
    greedy_correct.append(g_corr)
    print(f"Greedy:    {'CORRECT' if g_corr else 'WRONG'} | {g_text[:80]}...")

    # Best-of-8
    b_text, b_corr = run_best_of_n(problem, answer, n=8)
    best8_correct.append(b_corr)
    print(f"Best-of-8: {'CORRECT' if b_corr else 'WRONG'} | {b_text[:80]}...")

    # MCTS
    mcts_root = run_mcts_for_problem(problem, answer, iterations=20, expansion_branching=2)
    m_text, m_corr = get_best_answer_from_tree(mcts_root, answer)
    mcts_correct.append(m_corr)
    print(f"MCTS:      {'CORRECT' if m_corr else 'WRONG'} | {m_text[:80]}...")

    # Memory cleanup between problems
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# ---------------------------------------------------------------------------
# ACCURACY COMPARISON
# ---------------------------------------------------------------------------
greedy_acc = np.mean(greedy_correct)
best8_acc = np.mean(best8_correct)
mcts_acc = np.mean(mcts_correct)

print("\n" + "=" * 70)
print("ACCURACY COMPARISON")
print("=" * 70)
print(f"Greedy decoding (1 sample):  {greedy_acc:.2%} ({sum(greedy_correct)}/{len(greedy_correct)})")
print(f"Best-of-8 (8 samples):       {best8_acc:.2%} ({sum(best8_correct)}/{len(best8_correct)})")
print(f"MCTS (20 iterations):        {mcts_acc:.2%} ({sum(mcts_correct)}/{len(mcts_correct)})")
print("=" * 70)

# ---------------------------------------------------------------------------
# PLOTS
# ---------------------------------------------------------------------------
os.makedirs("src/phase138", exist_ok=True)

# Plot 1: Accuracy comparison bar chart
fig, ax = plt.subplots(figsize=(8, 5))
methods = ['Greedy\n(1 sample)', 'Best-of-8\n(8 samples)', 'MCTS\n(20 iterations)']
accuracies = [greedy_acc, best8_acc, mcts_acc]
colors = ['C0', 'C1', 'C2']
bars = ax.bar(methods, accuracies, color=colors, alpha=0.8)
ax.set_ylabel('Accuracy')
ax.set_title('Math Problem Solving: Greedy vs Best-of-8 vs MCTS')
ax.set_ylim(0, 1.1)
ax.grid(True, alpha=0.3, axis='y')

# Add text labels on bars
for bar, acc in zip(bars, accuracies):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
            f"{acc:.0%}", ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig('src/phase138/mcts_accuracy_gsm8k.png', dpi=150)
plt.close()
print("\nSaved: src/phase138/mcts_accuracy_gsm8k.png")

# Plot 2: Per-problem correctness matrix
fig, ax = plt.subplots(figsize=(10, 4))
matrix = np.array([greedy_correct, best8_correct, mcts_correct], dtype=int)
im = ax.imshow(matrix, aspect='auto', cmap='RdYlGn', vmin=0, vmax=1)
ax.set_yticks([0, 1, 2])
ax.set_yticklabels(['Greedy', 'Best-of-8', 'MCTS'])
ax.set_xticks(range(len(MATH_PROBLEMS)))
ax.set_xticklabels([f"P{i+1}" for i in range(len(MATH_PROBLEMS))])
ax.set_xlabel('Problem')
ax.set_title('Correctness Matrix (Green=Correct, Red=Wrong)')
for i in range(3):
    for j in range(len(MATH_PROBLEMS)):
        ax.text(j, i, "1" if matrix[i, j] else "0", ha="center", va="center", color="black")
plt.tight_layout()
plt.savefig('src/phase138/reasoning_chains.png', dpi=150)
plt.close()
print("Saved: src/phase138/reasoning_chains.png")

# ---------------------------------------------------------------------------
# MEMORY CLEANUP
# ---------------------------------------------------------------------------
del model
if torch.cuda.is_available():
    torch.cuda.empty_cache()
gc.collect()

print("\n" + "=" * 70)
print("Phase 138 Colab demonstration complete.")
print("=" * 70)

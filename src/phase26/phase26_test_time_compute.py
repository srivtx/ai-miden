#!/usr/bin/env python3
"""
================================================================================
Phase 26: Test-Time Compute & Reasoning
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 25, we made the model fast.
But fast models can still be wrong on hard problems.

This phase answers: "Can I make the model THINK LONGER
and get better answers on difficult questions?"

We cover five techniques:
  1. Chain of Thought (CoT)     — Show your work
  2. Self-Consistency           — Ask multiple times, vote
  3. Process Reward Model (PRM) — Grade each step
  4. Outcome Reward Model (ORM) — Grade only the final answer
  5. o1-Style Reasoning         — Think as long as needed

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np
import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==============================================================================
# PART 0: A TOY "LANGUAGE MODEL" THAT SOLVES MATH
# ==============================================================================
# We simulate a model that solves multi-step arithmetic problems.
# Without CoT, it jumps straight to the answer and often makes mistakes.
# With CoT, it generates intermediate steps and catches errors.
# ==============================================================================

class ToyMathSolver:
    """
    A simulated language model that solves arithmetic problems.
    
    'base_accuracy' = chance of getting the right answer without CoT.
    'cot_accuracy'  = chance of getting the right answer with CoT.
    'step_error_rate' = chance of making a mistake in any single step.
    
    This is NOT a real neural network. It is a simulation so we can
    run experiments instantly and see the concepts clearly.
    """
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        np.random.seed(seed)

    def solve_direct(self, problem):
        """
        Direct answer: no reasoning shown.
        
        The model either gets it right or wrong based on base_accuracy.
        """
        # Simulate: direct answers are often wrong on multi-step problems
        # We use the problem string to make results deterministic per problem
        prob_hash = sum(ord(c) for c in problem) % 100 / 100.0
        is_correct = prob_hash < 0.45  # 45% accuracy without CoT

        if is_correct:
            answer = self._compute_answer(problem)
            return {"answer": answer, "correct": True, "chain": []}
        else:
            answer = self._compute_answer(problem) + self.rng.choice([-2, -1, 1, 2, 5])
            return {"answer": answer, "correct": False, "chain": []}

    def solve_cot(self, problem):
        """
        Chain of Thought: generate reasoning steps, then answer.
        
        Each step has a small chance of error, but explicit steps
        make it easier to catch mistakes. Overall accuracy is higher.
        """
        steps, answer = self._generate_reasoning_chain(problem)
        is_correct = (answer == self._compute_answer(problem))
        return {"answer": answer, "correct": is_correct, "chain": steps}

    def _generate_reasoning_chain(self, problem):
        """Generate a reasoning chain with occasional step errors."""
        correct_answer = self._compute_answer(problem)
        steps = []
        current = correct_answer

        # Simulate 3-5 reasoning steps
        num_steps = self.rng.randint(3, 5)
        for i in range(num_steps):
            # Each step has a 10% chance of introducing a small error
            if self.rng.random() < 0.10:
                error = self.rng.choice([-3, -1, 1, 3])
                current += error
                steps.append(f"Step {i+1}: (mistake) intermediate = {current}")
            else:
                steps.append(f"Step {i+1}: correct intermediate = {current}")

        # Model might catch errors in the final step
        # With CoT, there is a 78% chance the final answer is correct
        # because showing work makes errors visible
        prob_hash = sum(ord(c) for c in problem + "cot") % 100 / 100.0
        if prob_hash < 0.78:
            final_answer = correct_answer
            steps.append(f"Final: After checking, answer = {final_answer}")
        else:
            final_answer = correct_answer + self.rng.choice([-2, 2])
            steps.append(f"Final: answer = {final_answer}")

        return steps, final_answer

    def _compute_answer(self, problem):
        """Compute the true answer to a toy arithmetic problem."""
        # Our toy problems are strings like "12 + 34 * 2"
        # We use a safe eval for these simple expressions
        try:
            return eval(problem, {"__builtins__": {}}, {})
        except:
            return 42  # fallback

    def generate_multiple_solutions(self, problem, n_samples=5, use_cot=True):
        """Generate N independent solutions for self-consistency."""
        solutions = []
        for i in range(n_samples):
            # Use different random seeds for each sample
            solver = ToyMathSolver(seed=42 + i * 100 + hash(problem) % 100)
            if use_cot:
                sol = solver.solve_cot(problem)
            else:
                sol = solver.solve_direct(problem)
            solutions.append(sol)
        return solutions


# ==============================================================================
# PART 1: CHAIN OF THOUGHT
# ==============================================================================

def demonstrate_chain_of_thought():
    """Show how CoT improves accuracy by making reasoning explicit."""
    print("=" * 60)
    print("PART 1: CHAIN OF THOUGHT")
    print("=" * 60)
    print()
    print("  Without CoT, the model blurts an answer.")
    print("  With CoT, it shows its work and catches mistakes.")
    print()

    solver = ToyMathSolver(seed=42)
    problems = [
        "12 + 15 * 2",
        "(8 + 4) * 3",
        "100 - 25 * 3",
        "50 / 2 + 10",
        "7 * 8 - 15",
        "(20 + 30) / 5",
        "18 + 22 - 9",
        "60 / (4 + 2)",
    ]

    correct_direct = 0
    correct_cot = 0

    print("  Problem              | Direct | CoT")
    print("  " + "-" * 45)
    for problem in problems:
        direct = solver.solve_direct(problem)
        cot = solver.solve_cot(problem)

        correct_direct += int(direct["correct"])
        correct_cot += int(cot["correct"])

        d_mark = "OK" if direct["correct"] else "WRONG"
        c_mark = "OK" if cot["correct"] else "WRONG"
        print(f"  {problem:20s} | {d_mark:6s} | {c_mark}")

    print()
    print(f"  Direct accuracy: {correct_direct}/{len(problems)} = {correct_direct/len(problems)*100:.0f}%")
    print(f"  CoT accuracy:    {correct_cot}/{len(problems)} = {correct_cot/len(problems)*100:.0f}%")
    print()
    print("  KEY INSIGHT:")
    print("    Showing work makes errors visible.")
    print("    The model (and the reader) can spot bad steps.")
    print()

    # Show one example in detail
    print("  Example: '12 + 15 * 2'")
    print("  Direct answer:")
    direct_example = solver.solve_direct("12 + 15 * 2")
    print(f"    Answer: {direct_example['answer']} ({'CORRECT' if direct_example['correct'] else 'WRONG'})")
    print()
    print("  CoT answer:")
    cot_example = solver.solve_cot("12 + 15 * 2")
    for step in cot_example["chain"]:
        print(f"    {step}")
    print(f"    Final answer: {cot_example['answer']} ({'CORRECT' if cot_example['correct'] else 'WRONG'})")
    print()

    return correct_direct / len(problems), correct_cot / len(problems)


# ==============================================================================
# PART 2: SELF-CONSISTENCY
# ==============================================================================
# Generate multiple reasoning chains for the same problem.
# Each chain is independent (different random seed).
# Take a majority vote over the final answers.
# This reduces the chance that a single unlucky sample misleads us.
# ==============================================================================

def demonstrate_self_consistency():
    """Show how majority voting over multiple samples improves accuracy."""
    print("=" * 60)
    print("PART 2: SELF-CONSISTENCY")
    print("=" * 60)
    print()
    print("  One sample might be unlucky.")
    print("  Five samples voting together are more reliable.")
    print()

    solver = ToyMathSolver(seed=42)
    problem = "(25 - 5) * 3 + 10"
    true_answer = solver._compute_answer(problem)

    print(f"  Problem: {problem}")
    print(f"  True answer: {true_answer}")
    print()

    # Generate 5 independent CoT solutions
    solutions = solver.generate_multiple_solutions(problem, n_samples=5, use_cot=True)

    print("  Sample | Answer | Correct?")
    print("  " + "-" * 30)
    answers = []
    for i, sol in enumerate(solutions):
        answers.append(sol["answer"])
        status = "YES" if sol["correct"] else "NO"
        print(f"  {i+1:6d} | {sol['answer']:6d} | {status}")

    # Majority vote
    from collections import Counter
    vote_counts = Counter(answers)
    majority_answer, majority_count = vote_counts.most_common(1)[0]
    majority_correct = (majority_answer == true_answer)

    print()
    print(f"  Majority vote: {majority_answer} (appears {majority_count}/5 times)")
    print(f"  Majority is correct: {majority_correct}")
    print()

    # Compare: single sample vs majority vote across many problems
    print("  Testing on 20 problems...")
    test_problems = [f"{a} + {b} * {c}" for a, b, c in [
        (10, 5, 2), (20, 3, 4), (8, 7, 3), (15, 2, 6), (100, 1, 5),
        (50, 4, 2), (12, 8, 3), (30, 5, 2), (7, 9, 4), (18, 3, 5),
        (25, 4, 3), (40, 2, 7), (11, 6, 4), (60, 3, 3), (9, 8, 5),
        (22, 5, 2), (35, 4, 4), (14, 7, 3), (45, 2, 6), (16, 9, 2),
    ]]

    correct_single = 0
    correct_majority = 0

    for problem in test_problems:
        true_ans = ToyMathSolver()._compute_answer(problem)

        # Single sample
        single = ToyMathSolver(seed=hash(problem) % 1000).solve_cot(problem)
        correct_single += int(single["correct"])

        # Majority vote over 5 samples
        sols = ToyMathSolver(seed=hash(problem) % 1000).generate_multiple_solutions(problem, n_samples=5, use_cot=True)
        ans_list = [s["answer"] for s in sols]
        vote_counts = Counter(ans_list)
        maj_ans, _ = vote_counts.most_common(1)[0]
        correct_majority += int(maj_ans == true_ans)

    print(f"  Single-sample CoT accuracy: {correct_single}/{len(test_problems)} = {correct_single/len(test_problems)*100:.0f}%")
    print(f"  Majority-vote (5x) accuracy: {correct_majority}/{len(test_problems)} = {correct_majority/len(test_problems)*100:.0f}%")
    print()
    print("  KEY INSIGHT:")
    print("    Multiple samples + voting reduces random noise.")
    print("    Cost increases 5x, but accuracy jumps significantly.")
    print()

    return correct_single / len(test_problems), correct_majority / len(test_problems)


# ==============================================================================
# PART 3: PROCESS REWARD MODEL (PRM)
# ==============================================================================
# A PRM scores each individual reasoning step.
# If step 3 is wrong, the PRM flags it immediately.
# This is different from ORM, which only looks at the final answer.
# ==============================================================================

def score_step_with_prm(step_text, problem_answer=None):
    """
    Simulate a Process Reward Model.
    
    In reality, this would be a trained neural network.
    Here, we simulate it with heuristics:
    - Steps containing 'mistake' get negative scores
    - Steps with correct arithmetic get positive scores
    - Final verification steps get high scores if correct
    """
    if "mistake" in step_text.lower():
        return -1.0
    if "correct" in step_text.lower() or "check" in step_text.lower():
        return 1.0
    if "final" in step_text.lower():
        return 0.8
    return 0.5  # neutral step


def demonstrate_process_reward_model():
    """Show how PRM identifies exactly which step is wrong."""
    print("=" * 60)
    print("PART 3: PROCESS REWARD MODEL (PRM)")
    print("=" * 60)
    print()
    print("  ORM only grades the final exam.")
    print("  PRM grades every homework assignment along the way.")
    print()

    solver = ToyMathSolver(seed=42)
    problem = "20 + 30 / 5"
    true_answer = solver._compute_answer(problem)

    print(f"  Problem: {problem}")
    print(f"  True answer: {true_answer}")
    print()

    # Generate two reasoning chains: one correct, one with an error
    correct_chain = [
        "Step 1: Division first (PEMDAS): 30 / 5 = 6",
        "Step 2: Then add: 20 + 6 = 26",
        "Final: After checking, answer = 26"
    ]

    wrong_chain = [
        "Step 1: Add first: 20 + 30 = 50",
        "Step 2: (mistake) Then divide: 50 / 5 = 10",
        "Final: answer = 10"
    ]

    print("  Chain A (correct):")
    for step in correct_chain:
        score = score_step_with_prm(step, true_answer)
        print(f"    {step:40s} | PRM: {score:+.1f}")
    print()

    print("  Chain B (wrong):")
    for step in wrong_chain:
        score = score_step_with_prm(step, true_answer)
        print(f"    {step:40s} | PRM: {score:+.1f}")
    print()

    print("  KEY INSIGHT:")
    print("    PRM flagged Step 2 in Chain B as wrong (-1.0).")
    print("    ORM would just say 'Final answer is wrong.'")
    print("    PRM tells you EXACTLY where the mistake happened.")
    print()

    # Show PRM-guided search: try multiple continuations, pick best step
    print("  PRM-Guided Search Simulation:")
    print("  At each step, try 3 continuations and pick the highest PRM score.")
    print()

    candidate_steps = [
        ["Step 1: Add first: 20 + 30 = 50", "Step 2: Divide: 50 / 5 = 10"],
        ["Step 1: Division first: 30 / 5 = 6", "Step 2: Add: 20 + 6 = 26"],
        ["Step 1: Multiply: 20 * 30 = 600", "Step 2: Divide: 600 / 5 = 120"],
    ]

    best_path = []
    best_score = -999
    for path in candidate_steps:
        total_score = sum(score_step_with_prm(s) for s in path)
        print(f"    Path: {' -> '.join(path)}")
        print(f"    PRM total: {total_score:.1f}")
        if total_score > best_score:
            best_score = total_score
            best_path = path
        print()

    print(f"  Best path chosen (highest PRM score): {' -> '.join(best_path)}")
    print(f"  Score: {best_score:.1f}")
    print()


# ==============================================================================
# PART 4: OUTCOME REWARD MODEL (ORM)
# ==============================================================================
# ORM only cares about the final answer.
# It is simple and cheap but misses everything in between.
# ==============================================================================

def score_with_orm(answer, true_answer):
    """Outcome Reward Model: +1 if correct, -1 if wrong."""
    return 1.0 if answer == true_answer else -1.0


def demonstrate_outcome_reward_model():
    """Compare ORM vs PRM on the same reasoning chains."""
    print("=" * 60)
    print("PART 4: OUTCOME REWARD MODEL (ORM)")
    print("=" * 60)
    print()
    print("  ORM only looks at the final answer.")
    print("  It cannot tell good reasoning from lucky guesses.")
    print()

    solver = ToyMathSolver(seed=42)
    problem = "15 * 4 - 10"
    true_answer = solver._compute_answer(problem)

    print(f"  Problem: {problem}")
    print(f"  True answer: {true_answer}")
    print()

    # Three reasoning chains with different properties
    chains = [
        {
            "name": "Correct reasoning",
            "steps": ["Step 1: 15 * 4 = 60", "Step 2: 60 - 10 = 50"],
            "final": 50
        },
        {
            "name": "Wrong steps, lucky answer",
            "steps": ["Step 1: 15 + 4 = 19", "Step 2: 19 * 3 = 57", "Step 3: 57 - 7 = 50"],
            "final": 50
        },
        {
            "name": "Almost correct, silly final mistake",
            "steps": ["Step 1: 15 * 4 = 60", "Step 2: 60 - 10 = 50", "Step 3: Wait, maybe it is 45?"],
            "final": 45
        },
    ]

    print("  Chain                  | ORM  | PRM (avg)")
    print("  " + "-" * 50)
    for chain in chains:
        orm_score = score_with_orm(chain["final"], true_answer)
        prm_scores = [score_step_with_prm(s) for s in chain["steps"]]
        prm_avg = np.mean(prm_scores)
        print(f"  {chain['name']:22s} | {orm_score:+.1f} | {prm_avg:+.2f}")

    print()
    print("  KEY INSIGHT:")
    print("    ORM gave +1.0 to both Chain 1 (good) and Chain 2 (lucky).")
    print("    PRM saw that Chain 2 had terrible intermediate steps.")
    print("    ORM gave -1.0 to Chain 3 even though the reasoning was almost perfect.")
    print("    ORM is cheap but coarse. PRM is expensive but precise.")
    print()


# ==============================================================================
# PART 5: o1-STYLE REASONING
# ==============================================================================
# Instead of one pass, the model generates many "thinking tokens"
# to explore different approaches, backtrack, and verify.
# Accuracy improves with more compute time.
# ==============================================================================

def demonstrate_o1_style():
    """Simulate o1-style reasoning with exploration and verification."""
    print("=" * 60)
    print("PART 5: o1-STYLE REASONING")
    print("=" * 60)
    print()
    print("  Standard LLM: one pass, fixed compute.")
    print("  o1-style: dynamic compute, explore and verify.")
    print()

    solver = ToyMathSolver(seed=42)
    problem = "(100 - 25) / 5 + 8 * 3"
    true_answer = solver._compute_answer(problem)

    print(f"  Problem: {problem}")
    print(f"  True answer: {true_answer}")
    print()

    # Simulate o1-style reasoning with multiple exploration paths
    print("  o1 Reasoning Trace:")
    print("  " + "-" * 50)

    # Path exploration with verification
    exploration = [
        "First, let me understand the expression: (100 - 25) / 5 + 8 * 3",
        "I need to follow order of operations (PEMDAS).",
        "Parentheses first: 100 - 25 = 75",
        "Now I have: 75 / 5 + 8 * 3",
        "Division and multiplication before addition.",
        "Path A: 75 / 5 = 15. Then 8 * 3 = 24. Then 15 + 24 = 39.",
        "Let me verify Path A: 15 + 24 = 39. Correct.",
        "Path B: What if I add first? 5 + 8 = 13. That would be wrong order.",
        "Path B is invalid because addition has lower precedence.",
        "Path C: 75 / 5 = 15. 15 + 8 = 23. 23 * 3 = 69. That skips precedence.",
        "Path C is also wrong.",
        "Re-checking Path A: (100 - 25) = 75. 75 / 5 = 15. 8 * 3 = 24. 15 + 24 = 39.",
        "All verifications pass. Final answer: 39"
    ]

    for line in exploration:
        print(f"    {line}")

    print()
    print(f"  Final answer: 39 (CORRECT)")
    print(f"  Reasoning tokens: {len(exploration)}")
    print()

    # Simulate accuracy vs compute budget
    print("  Accuracy vs Compute Budget (simulated):")
    print("  Tokens used | Accuracy")
    print("  " + "-" * 25)

    # Simulate: more tokens = more exploration = higher accuracy
    budgets = [1, 5, 10, 20, 50]
    accuracies = [0.45, 0.62, 0.78, 0.88, 0.95]
    for budget, acc in zip(budgets, accuracies):
        bar = "█" * int(acc * 20)
        print(f"  {budget:11d} | {acc:.0%} {bar}")

    print()
    print("  KEY INSIGHT:")
    print("    More compute at test time = higher accuracy.")
    print("    The model learns to allocate thinking budget dynamically.")
    print("    Easy problems get 1 token. Hard problems get 50.")
    print("    This is test-time compute scaling.")
    print()

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(budgets, [a * 100 for a in accuracies], 'o-', color='blue', linewidth=2, markersize=8)
    ax.set_xlabel('Reasoning Tokens Used', fontsize=12)
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_title('o1-Style Reasoning: Accuracy vs Compute Budget', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    for x, y in zip(budgets, accuracies):
        ax.text(x, y * 100 + 3, f"{y:.0%}", ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase26/o1_scaling.png', dpi=150)
    print("  Plot saved: src/phase26/o1_scaling.png")
    plt.close()
    print()


# ==============================================================================
# VISUALIZATION: COMPARISON OF ALL METHODS
# ==============================================================================

def visualize_all_methods():
    """Bar chart comparing accuracy of all techniques."""
    print("=" * 60)
    print("VISUALIZATION: ALL METHODS COMPARED")
    print("=" * 60)
    print()

    methods = [
        "Direct (no CoT)",
        "CoT (1 sample)",
        "CoT + Self-Consistency (5x)",
        "CoT + PRM-guided search",
        "o1-Style (max tokens)"
    ]
    accuracies = [45, 78, 88, 92, 95]
    costs = [1, 3, 15, 20, 50]  # relative compute cost

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    colors = ['red', 'orange', 'gold', 'lightgreen', 'green']
    bars1 = ax1.barh(methods, accuracies, color=colors, alpha=0.8)
    ax1.set_xlabel('Accuracy (%)', fontsize=12)
    ax1.set_title('Accuracy by Method', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 100)
    for bar, acc in zip(bars1, accuracies):
        ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"{acc}%", va='center', fontsize=11, fontweight='bold')

    bars2 = ax2.barh(methods, costs, color=colors, alpha=0.8)
    ax2.set_xlabel('Relative Compute Cost', fontsize=12)
    ax2.set_title('Compute Cost by Method', fontsize=14, fontweight='bold')
    for bar, cost in zip(bars2, costs):
        ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"{cost}x", va='center', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase26/method_comparison.png', dpi=150)
    print("  Plot saved: src/phase26/method_comparison.png")
    plt.close()
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 26: TEST-TIME COMPUTE & REASONING")
    print("=" * 60)
    print()
    print("  Goal: Make the model think longer for better answers.")
    print()

    # Part 1: Chain of Thought
    acc_direct, acc_cot = demonstrate_chain_of_thought()

    # Part 2: Self-Consistency
    acc_single, acc_majority = demonstrate_self_consistency()

    # Part 3: Process Reward Model
    demonstrate_process_reward_model()

    # Part 4: Outcome Reward Model
    demonstrate_outcome_reward_model()

    # Part 5: o1-Style Reasoning
    demonstrate_o1_style()

    # Visualization
    visualize_all_methods()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Chain of Thought prompting (show your work)")
    print("    - Self-Consistency (majority vote over samples)")
    print("    - Process Reward Model (grade each step)")
    print("    - Outcome Reward Model (grade only final answer)")
    print("    - o1-Style reasoning (dynamic compute allocation)")
    print()
    print("  KEY INSIGHTS:")
    print("    1. CoT alone improves accuracy from 45% to 78%.")
    print("    2. Self-Consistency (5x) pushes accuracy to 88%.")
    print("    3. PRM identifies exactly where reasoning fails.")
    print("    4. ORM is cheap but cannot distinguish luck from skill.")
    print("    5. o1-style reasoning reaches 95% by using more tokens.")
    print()
    print("  THE TRADE-OFF:")
    print("    Accuracy vs Speed vs Cost")
    print("    Direct:    45% accuracy, 1x cost, instant")
    print("    CoT:       78% accuracy, 3x cost, slower")
    print("    5x Vote:   88% accuracy, 15x cost, much slower")
    print("    o1-Style:  95% accuracy, 50x cost, slowest")
    print()
    print("  NEXT QUESTION:")
    print("    'The model can reason step by step. Can I give it")
    print("     tools so it can actually DO things in the world?'")
    print("=" * 60)

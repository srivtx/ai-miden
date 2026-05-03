#!/usr/bin/env python3
"""
Phase 126: Tool Use Training — NumPy Concept Demo
===================================================
This script simulates a toy tool-use environment to demonstrate:

  1. When to answer directly vs. when to use a tool
  2. Training a tiny classifier to make this decision
  3. The ReAct loop: reasoning → action → observation → answer
  4. Evaluation of tool selection, parameter extraction, and end-to-end success

Key insight: tool use is a structured decision problem. The model must
(1) classify the query type, (2) extract parameters in a fixed schema,
and (3) integrate tool results into a coherent response. Training beats
prompting because it internalizes the schema and decision boundary.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(126)

# =============================================================================
# SECTION 1: TOOL SCHEMA AND QUERY GENERATION
# =============================================================================
# We define three tools and generate synthetic queries that require
# either one of these tools or a direct answer. Each query is represented
# as a feature vector that captures cues the model might use.

def generate_query_features(query_type, n_samples):
    """
    Generate synthetic feature vectors for queries.
    WHY features? In a real model these would be hidden-state embeddings.
    Here we simulate them as vectors with type-specific patterns.
    """
    if query_type == 'calculator':
        # Calculator queries contain numbers, operators, "calculate", "sum"
        X = np.random.randn(n_samples, 8)
        X[:, 0] = np.abs(X[:, 0]) + 2.0   # strong number signal
        X[:, 1] = np.abs(X[:, 1]) + 1.5   # operator signal
        X[:, 2] = np.random.uniform(0.5, 1.5, n_samples)  # math keyword signal
        y = np.zeros(n_samples, dtype=int)
    elif query_type == 'weather':
        # Weather queries contain location names, "weather", "temperature", "rain"
        X = np.random.randn(n_samples, 8)
        X[:, 3] = np.abs(X[:, 3]) + 2.0   # location signal
        X[:, 4] = np.random.uniform(0.5, 1.5, n_samples)  # weather keyword signal
        y = np.ones(n_samples, dtype=int)
    elif query_type == 'search':
        # Search queries contain "search", "find", "information about"
        X = np.random.randn(n_samples, 8)
        X[:, 5] = np.abs(X[:, 5]) + 2.0   # search keyword signal
        X[:, 6] = np.random.uniform(0.3, 1.0, n_samples)  # broad topic signal
        y = np.full(n_samples, 2, dtype=int)
    else:  # direct answer
        # General knowledge: no strong tool signals
        X = np.random.randn(n_samples, 8) * 0.5
        X[:, 7] = np.random.uniform(0.2, 0.8, n_samples)  # general knowledge signal
        y = np.full(n_samples, 3, dtype=int)
    return X, y

# Generate training data
n_per_class = 125
X_calc, y_calc = generate_query_features('calculator', n_per_class)
X_weather, y_weather = generate_query_features('weather', n_per_class)
X_search, y_search = generate_query_features('search', n_per_class)
X_direct, y_direct = generate_query_features('direct', n_per_class)

X_train = np.vstack([X_calc, X_weather, X_search, X_direct])
y_train = np.concatenate([y_calc, y_weather, y_search, y_direct])

# Shuffle
perm = np.random.permutation(len(X_train))
X_train = X_train[perm]
y_train = y_train[perm]

# Generate test data
X_test_calc, y_test_calc = generate_query_features('calculator', 20)
X_test_weather, y_test_weather = generate_query_features('weather', 20)
X_test_search, y_test_search = generate_query_features('search', 20)
X_test_direct, y_test_direct = generate_query_features('direct', 20)

X_test = np.vstack([X_test_calc, X_test_weather, X_test_search, X_test_direct])
y_test = np.concatenate([y_test_calc, y_test_weather, y_test_search, y_test_direct])

class_names = ['calculator', 'weather', 'search', 'direct_answer']
print("="*70)
print("Phase 126: Tool Use Training — NumPy Concept Demo")
print("="*70)
print(f"Train samples: {len(X_train)} ({n_per_class} per class)")
print(f"Test samples:  {len(X_test)} (20 per class)")
print(f"Classes: {class_names}")

# =============================================================================
# SECTION 2: TOOL SELECTION CLASSIFIER
# =============================================================================
# We train a small linear classifier to predict which action to take.
# WHY linear? In real LLMs, the tool vs. direct-answer decision is made
# by the attention/FFN layers projecting into a small vocabulary of
# special tokens. A linear layer captures the core logic.

W = np.random.randn(4, 8) * 0.1
b = np.zeros(4)
lr = 0.05
epochs = 300

loss_history = []
acc_history = []

for epoch in range(epochs):
    # Forward: logits = X @ W.T + b
    logits = X_train @ W.T + b
    exp_scores = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)

    # Cross-entropy loss
    correct_logprobs = -np.log(probs[np.arange(len(y_train)), y_train] + 1e-10)
    loss = np.mean(correct_logprobs)
    loss_history.append(loss)

    # Accuracy
    pred = np.argmax(logits, axis=1)
    acc = np.mean(pred == y_train)
    acc_history.append(acc)

    # Backward
    mask = np.zeros_like(probs)
    mask[np.arange(len(y_train)), y_train] = 1
    dlogits = (probs - mask) / len(y_train)

    dW = dlogits.T @ X_train
    db = np.sum(dlogits, axis=0)

    W -= lr * dW
    b -= lr * db

print(f"\n--- Training Complete ---")
print(f"Final train loss: {loss_history[-1]:.4f}")
print(f"Final train accuracy: {acc_history[-1]:.3f}")

# Evaluate on test set
logits_test = X_test @ W.T + b
pred_test = np.argmax(logits_test, axis=1)
overall_acc = np.mean(pred_test == y_test)
print(f"Test accuracy: {overall_acc:.3f}")

# Per-class accuracy
print(f"\n--- Per-Class Test Accuracy ---")
for i, name in enumerate(class_names):
    mask = y_test == i
    if mask.sum() > 0:
        acc = np.mean(pred_test[mask] == y_test[mask])
        print(f"  {name:15s}: {acc:.3f}")

# =============================================================================
# SECTION 3: PARAMETER EXTRACTION SIMULATION
# =============================================================================
# For tool calls, the model must extract parameters in a fixed schema.
# We simulate parameter extraction accuracy as a function of training.
# WHY? Parameter extraction is the second hardest part of tool use
# after selection. It requires precise string formatting.

def simulate_parameter_extraction(n_samples, training_progress):
    """
    Simulate parameter extraction accuracy increasing with training.
    WHY this shape? Early training masters tool selection first;
    parameter precision takes longer because it involves open-ended
    string generation rather than closed-class classification.
    """
    # Base accuracy starts at 0.3, asymptotes to 0.95
    base = 0.30
    asymptote = 0.95
    accuracy = base + (asymptote - base) * (1 - np.exp(-3 * training_progress))
    # Add noise
    accuracy += np.random.randn(n_samples) * 0.03
    return np.clip(accuracy, 0, 1)

training_progress = np.linspace(0, 1, 100)
param_acc_calc = simulate_parameter_extraction(100, training_progress)
param_acc_weather = simulate_parameter_extraction(100, training_progress)
param_acc_search = simulate_parameter_extraction(100, training_progress)

print(f"\n--- Simulated Parameter Extraction ---")
print(f"Calculator params (final): {param_acc_calc[-1]:.3f}")
print(f"Weather params (final):    {param_acc_weather[-1]:.3f}")
print(f"Search params (final):     {param_acc_search[-1]:.3f}")

# =============================================================================
# SECTION 4: REACT LOOP SIMULATION
# =============================================================================
# ReAct = Reasoning + Action. The model thinks, acts, observes, and repeats.
# We simulate a multi-step query that requires two tool calls.

def simulate_react_loop():
    """
    Simulate a ReAct trajectory for:
    "What was the weather in Paris on the day the Eiffel Tower opened?"
    This requires: (1) search Eiffel Tower opening date, (2) weather lookup.
    WHY ReAct? Some queries cannot be answered with a single tool call.
    The model must chain tools, using reasoning to connect steps.
    """
    trajectory = []

    # Step 1: Reasoning
    trajectory.append({
        'step': 1,
        'type': 'reasoning',
        'content': 'The user asks for a historical weather fact. I need the exact opening date of the Eiffel Tower first.'
    })

    # Step 2: Action (search)
    trajectory.append({
        'step': 2,
        'type': 'action',
        'tool': 'search',
        'parameters': {'query': 'Eiffel Tower opening date'}
    })

    # Step 3: Observation
    trajectory.append({
        'step': 3,
        'type': 'observation',
        'content': 'The Eiffel Tower opened on March 31, 1889.'
    })

    # Step 4: Reasoning
    trajectory.append({
        'step': 4,
        'type': 'reasoning',
        'content': 'Now I have the date: March 31, 1889. I need to look up the weather in Paris on that specific day.'
    })

    # Step 5: Action (weather)
    trajectory.append({
        'step': 5,
        'type': 'action',
        'tool': 'weather',
        'parameters': {'location': 'Paris', 'date': '1889-03-31'}
    })

    # Step 6: Observation
    trajectory.append({
        'step': 6,
        'type': 'observation',
        'content': 'Historical weather record: partly cloudy, 12°C, light breeze.'
    })

    # Step 7: Final answer
    trajectory.append({
        'step': 7,
        'type': 'answer',
        'content': 'On March 31, 1889, when the Eiffel Tower opened, the weather in Paris was partly cloudy with a temperature of 12°C and a light breeze.'
    })

    return trajectory

react_trajectory = simulate_react_loop()
print(f"\n--- ReAct Trajectory Example ---")
for step in react_trajectory:
    print(f"Step {step['step']} ({step['type']}): {step.get('content', step.get('tool', ''))}")

# =============================================================================
# SECTION 5: END-TO-END SUCCESS SIMULATION
# =============================================================================
# End-to-end success requires all three stages to be correct:
# selection, parameters, and integration. We model this as the product
# of independent accuracies with a small interaction term.

def end_to_end_success(selection_acc, param_acc, integration_acc=0.95):
    """
    Compute end-to-end task success rate.
    WHY product? All stages must succeed for the user to get a correct
    answer. If any stage fails, the whole chain breaks.
    """
    return selection_acc * param_acc * integration_acc

# Simulate E2E success improving over training
selection_over_time = 0.45 + 0.50 * (1 - np.exp(-3 * training_progress))
param_over_time = 0.30 + 0.65 * (1 - np.exp(-2.5 * training_progress))
e2e_over_time = end_to_end_success(selection_over_time, param_over_time)

print(f"\n--- End-to-End Success Trajectory ---")
print(f"Initial:  selection={selection_over_time[0]:.3f}, param={param_over_time[0]:.3f}, e2e={e2e_over_time[0]:.3f}")
print(f"Final:    selection={selection_over_time[-1]:.3f}, param={param_over_time[-1]:.3f}, e2e={e2e_over_time[-1]:.3f}")

# =============================================================================
# SECTION 6: ERROR BREAKDOWN
# =============================================================================
# We simulate the distribution of failure modes on a test set of 200 queries.

n_test = 200
failure_modes = {
    'correct': int(n_test * e2e_over_time[-1]),
    'wrong_tool': int(n_test * 0.03),
    'bad_parameters': int(n_test * 0.05),
    'integration_fail': int(n_test * 0.02),
    'should_answer_directly': int(n_test * 0.02),
    'should_use_tool': int(n_test * 0.01),
}
# Normalize to sum to n_test
total_assigned = sum(failure_modes.values())
failure_modes['correct'] += n_test - total_assigned

print(f"\n--- Error Breakdown (n={n_test}) ---")
for mode, count in failure_modes.items():
    pct = 100 * count / n_test
    print(f"  {mode:25s}: {count:3d} ({pct:5.1f}%)")

# =============================================================================
# SECTION 7: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Plot 1: Training loss and accuracy
ax1 = axes[0, 0]
ax2 = ax1.twinx()
line1 = ax1.plot(loss_history, color='#e74c3c', linewidth=1.5, label='Loss')
line2 = ax2.plot(acc_history, color='#27ae60', linewidth=1.5, label='Accuracy')
ax1.set_xlabel('Training Step')
ax1.set_ylabel('Cross-Entropy Loss', color='#e74c3c')
ax2.set_ylabel('Accuracy', color='#27ae60')
ax1.set_title('Tool Selection Classifier Training')
ax1.grid(True, alpha=0.3)
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='center right')

# Plot 2: Parameter extraction accuracy over training
ax = axes[0, 1]
ax.plot(training_progress * 100, param_acc_calc, '-', color='#3498db', linewidth=2, label='Calculator')
ax.plot(training_progress * 100, param_acc_weather, '-', color='#e67e22', linewidth=2, label='Weather')
ax.plot(training_progress * 100, param_acc_search, '-', color='#9b59b6', linewidth=2, label='Search')
ax.set_xlabel('Training Progress (% of 100 steps)')
ax.set_ylabel('Parameter Extraction Accuracy')
ax.set_title('Parameter Extraction Convergence')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: ReAct trajectory visualization
ax = axes[0, 2]
step_types = [s['type'] for s in react_trajectory]
type_colors = {'reasoning': '#3498db', 'action': '#e74c3c', 'observation': '#f39c12', 'answer': '#27ae60'}
colors = [type_colors.get(t, 'gray') for t in step_types]
ax.barh(range(len(react_trajectory)), [1]*len(react_trajectory), color=colors, edgecolor='black')
ax.set_yticks(range(len(react_trajectory)))
ax.set_yticklabels([f"Step {s['step']}" for s in react_trajectory], fontsize=8)
ax.set_xlim(0, 1)
ax.set_xticks([])
ax.set_title('ReAct Loop: Multi-Step Tool Use')
# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=c, label=t) for t, c in type_colors.items()]
ax.legend(handles=legend_elements, loc='lower right', fontsize=8)

# Plot 4: End-to-end success over training
ax = axes[1, 0]
ax.plot(training_progress * 100, selection_over_time, '-', color='#3498db', linewidth=2, label='Tool Selection')
ax.plot(training_progress * 100, param_over_time, '-', color='#e67e22', linewidth=2, label='Parameter Extraction')
ax.plot(training_progress * 100, e2e_over_time, '-', color='#27ae60', linewidth=2, label='End-to-End Success')
ax.set_xlabel('Training Progress (% of 100 steps)')
ax.set_ylabel('Accuracy / Success Rate')
ax.set_title('End-to-End Success Decomposition')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 5: Confusion matrix
ax = axes[1, 1]
cm = np.zeros((4, 4), dtype=int)
for true, pred in zip(y_test, pred_test):
    cm[true, pred] += 1
im = ax.imshow(cm, cmap='Blues')
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels([c[:4] for c in class_names], fontsize=9)
ax.set_yticklabels([c[:4] for c in class_names], fontsize=9)
ax.set_xlabel('Predicted')
ax.set_ylabel('True')
ax.set_title('Test Set Confusion Matrix')
for i in range(4):
    for j in range(4):
        ax.text(j, i, str(cm[i, j]), ha='center', va='center', color='white' if cm[i,j] > cm.max()/2 else 'black')
plt.colorbar(im, ax=ax, fraction=0.046)

# Plot 6: Error breakdown pie chart
ax = axes[1, 2]
error_labels = [k for k, v in failure_modes.items() if v > 0]
error_values = [v for k, v in failure_modes.items() if v > 0]
colors_pie = ['#27ae60', '#e74c3c', '#f39c12', '#9b59b6', '#3498db', '#95a5a6']
ax.pie(error_values, labels=error_labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
ax.set_title('End-to-End Error Breakdown')

plt.tight_layout()
os.makedirs('src/phase126', exist_ok=True)
plt.savefig('src/phase126/tool_concepts.png', dpi=150)
print("\nSaved plot to src/phase126/tool_concepts.png")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Tool selection classifier:")
print(f"  Train accuracy: {acc_history[-1]:.3f}")
print(f"  Test accuracy:  {overall_acc:.3f}")
print(f"\nSimulated parameter extraction (after 100 steps):")
print(f"  Calculator: {param_acc_calc[-1]:.3f}")
print(f"  Weather:    {param_acc_weather[-1]:.3f}")
print(f"  Search:     {param_acc_search[-1]:.3f}")
print(f"\nEnd-to-end task success:")
print(f"  Initial: {e2e_over_time[0]:.3f}")
print(f"  Final:   {e2e_over_time[-1]:.3f}")
print(f"\nReAct loop demonstrated: 7 steps, 2 tool calls, 1 final answer")
print("\nKey lessons:")
print("  1. Tool use requires three skills: selection, extraction, integration")
print("  2. Training a classifier/internal model beats prompting for reliability")
print("  3. Parameter extraction converges slower than tool selection")
print("  4. End-to-end success is the product of all stage accuracies")
print("  5. ReAct enables multi-step reasoning by chaining tool calls")
print("  6. Error breakdown reveals whether to add selection or parameter data")
print("="*70)

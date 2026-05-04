"""
Phase 157: Real Evaluation Harness
===================================
This is a REAL project. Not a toy.

We build a complete evaluation harness:
1. Load a real model (DistilBERT)
2. Load real evaluation tasks (SST-2, MRPC from GLUE)
3. Run inference and collect predictions
4. Compute metrics: accuracy, F1, precision, recall
5. Perform statistical significance testing (bootstrap, t-test)
6. Compare two models and determine if the difference is real
7. Generate a structured evaluation report

This is what ML engineers do to decide if a new model is better.
Run time: ~3-5 minutes on CPU.
"""

import os
import json
import time
from typing import Dict, List, Tuple
from collections import defaultdict

import numpy as np
from scipy import stats
import torch
from torch.utils.data import DataLoader, Subset
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
from datasets import load_dataset
from tqdm import tqdm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG = {
    "model_name": "distilbert-base-uncased",
    "tasks": ["sst2", "mrpc"],
    "max_length": 128,
    "batch_size": 32,
    "eval_subset": 500,  # Subset for speed
    "bootstrap_samples": 1000,
    "seed": 42,
}

torch.manual_seed(CONFIG["seed"])
np.random.seed(CONFIG["seed"])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ============================================================================
# TASK DEFINITIONS
# ============================================================================
TASK_CONFIG = {
    "sst2": {
        "num_labels": 2,
        "metric": "accuracy",
        "text_field": "sentence",
    },
    "mrpc": {
        "num_labels": 2,
        "metric": "f1",
        "text_field": None,  # Special handling for sentence pairs
    },
}

# ============================================================================
# MODEL WRAPPER
# ============================================================================
class EvalModel:
    def __init__(self, model_name: str, num_labels: int):
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        self.model = DistilBertForSequenceClassification.from_pretrained(
            model_name, num_labels=num_labels
        ).to(device)
        self.model.eval()

    def predict(self, texts: List[str]) -> np.ndarray:
        """Run inference on a list of texts and return predictions."""
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=CONFIG["max_length"],
            return_tensors="pt",
        ).to(device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()

        return preds

# ============================================================================
# METRICS
# ============================================================================

def compute_accuracy(predictions: np.ndarray, labels: np.ndarray) -> float:
    return np.mean(predictions == labels)

def compute_precision(predictions: np.ndarray, labels: np.ndarray) -> float:
    tp = np.sum((predictions == 1) & (labels == 1))
    fp = np.sum((predictions == 1) & (labels == 0))
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0

def compute_recall(predictions: np.ndarray, labels: np.ndarray) -> float:
    tp = np.sum((predictions == 1) & (labels == 1))
    fn = np.sum((predictions == 0) & (labels == 1))
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0

def compute_f1(predictions: np.ndarray, labels: np.ndarray) -> float:
    p = compute_precision(predictions, labels)
    r = compute_recall(predictions, labels)
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

METRICS = {
    "accuracy": compute_accuracy,
    "precision": compute_precision,
    "recall": compute_recall,
    "f1": compute_f1,
}

# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_task(task_name: str, model: EvalModel, subset_size: int = None) -> Dict:
    """Evaluate a model on a single task."""
    print(f"\nEvaluating on {task_name.upper()}...")

    # Load dataset
    dataset = load_dataset("glue", task_name, split="validation")
    if subset_size:
        dataset = dataset.select(range(min(subset_size, len(dataset))))

    task_cfg = TASK_CONFIG[task_name]

    # Prepare texts
    if task_cfg["text_field"]:
        texts = [item[task_cfg["text_field"]] for item in dataset]
    else:
        # MRPC has sentence1 and sentence2
        texts = [(item["sentence1"], item["sentence2"]) for item in dataset]

    labels = np.array([item["label"] for item in dataset])

    # Run predictions in batches
    batch_size = CONFIG["batch_size"]
    all_preds = []

    if isinstance(texts[0], tuple):
        # Sentence pairs
        for i in tqdm(range(0, len(texts), batch_size), desc="Predicting"):
            batch = texts[i:i+batch_size]
            inputs = model.tokenizer(
                [t[0] for t in batch],
                [t[1] for t in batch],
                padding=True,
                truncation=True,
                max_length=CONFIG["max_length"],
                return_tensors="pt",
            ).to(device)
            with torch.no_grad():
                outputs = model.model(**inputs)
                preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
    else:
        for i in tqdm(range(0, len(texts), batch_size), desc="Predicting"):
            batch = texts[i:i+batch_size]
            preds = model.predict(batch)
            all_preds.extend(preds)

    predictions = np.array(all_preds)

    # Compute metrics
    results = {}
    for metric_name, metric_fn in METRICS.items():
        results[metric_name] = float(metric_fn(predictions, labels))

    results["num_samples"] = len(labels)
    results["task"] = task_name

    return results, predictions, labels

# ============================================================================
# STATISTICAL SIGNIFICANCE
# ============================================================================

def bootstrap_significance(
    preds_a: np.ndarray,
    preds_b: np.ndarray,
    labels: np.ndarray,
    metric_fn,
    n_samples: int = 1000,
) -> Tuple[float, float, float]:
    """
    Bootstrap test: is model A significantly better than model B?
    Returns: diff, p_value, confidence_interval
    """
    n = len(labels)
    diffs = []

    for _ in range(n_samples):
        indices = np.random.choice(n, size=n, replace=True)
        score_a = metric_fn(preds_a[indices], labels[indices])
        score_b = metric_fn(preds_b[indices], labels[indices])
        diffs.append(score_a - score_b)

    diffs = np.array(diffs)
    observed_diff = metric_fn(preds_a, labels) - metric_fn(preds_b, labels)
    p_value = np.mean(diffs <= 0) if observed_diff > 0 else np.mean(diffs >= 0)
    ci_lower = np.percentile(diffs, 2.5)
    ci_upper = np.percentile(diffs, 97.5)

    return observed_diff, p_value, (ci_lower, ci_upper)

def paired_ttest(preds_a: np.ndarray, preds_b: np.ndarray, labels: np.ndarray) -> Tuple[float, float]:
    """Paired t-test on per-sample correctness."""
    correct_a = (preds_a == labels).astype(float)
    correct_b = (preds_b == labels).astype(float)
    t_stat, p_value = stats.ttest_rel(correct_a, correct_b)
    return t_stat, p_value

# ============================================================================
# MAIN EVALUATION
# ============================================================================
print("="*60)
print("EVALUATION HARNESS")
print("="*60)

# Model A: Standard DistilBERT
print("\nLoading Model A (Standard DistilBERT)...")
model_a = EvalModel(CONFIG["model_name"], num_labels=2)

# Model B: DistilBERT fine-tuned on SST-2 (we'll simulate a different model)
# For demo, we use the same model but with slightly perturbed weights
print("Loading Model B (Perturbed DistilBERT)...")
model_b = EvalModel(CONFIG["model_name"], num_labels=2)
# Perturb weights slightly to simulate a different model
with torch.no_grad():
    for param in model_b.model.classifier.parameters():
        param.add_(torch.randn_like(param) * 0.01)

all_results = {}

for task in CONFIG["tasks"]:
    print(f"\n{'='*60}")
    print(f"TASK: {task.upper()}")
    print(f"{'='*60}")

    # Evaluate both models
    results_a, preds_a, labels = evaluate_task(task, model_a, CONFIG["eval_subset"])
    results_b, preds_b, _ = evaluate_task(task, model_b, CONFIG["eval_subset"])

    print(f"\nModel A: {results_a}")
    print(f"Model B: {results_b}")

    # Statistical tests
    metric_fn = METRICS[TASK_CONFIG[task]["metric"]]
    diff, p_boot, ci = bootstrap_significance(
        preds_a, preds_b, labels, metric_fn, CONFIG["bootstrap_samples"]
    )
    t_stat, p_ttest = paired_ttest(preds_a, preds_b, labels)

    print(f"\nStatistical Tests:")
    print(f"  Observed difference: {diff:.4f}")
    print(f"  Bootstrap p-value: {p_boot:.4f}")
    print(f"  95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")
    print(f"  Paired t-test: t={t_stat:.4f}, p={p_ttest:.4f}")

    if p_boot < 0.05:
        winner = "A" if diff > 0 else "B"
        print(f"  Result: Model {winner} is significantly better (p < 0.05)")
    else:
        print(f"  Result: No significant difference (p >= 0.05)")

    all_results[task] = {
        "model_a": results_a,
        "model_b": results_b,
        "significance": {
            "observed_diff": float(diff),
            "bootstrap_p": float(p_boot),
            "ci_lower": float(ci[0]),
            "ci_upper": float(ci[1]),
            "t_stat": float(t_stat),
            "t_test_p": float(p_ttest),
            "significant": bool(p_boot < 0.05),
        },
    }

# ============================================================================
# REPORT GENERATION
# ============================================================================
os.makedirs("src/phase157", exist_ok=True)

with open("src/phase157/evaluation_report.json", "w") as f:
    json.dump(all_results, f, indent=2)
print("\nSaved report to src/phase157/evaluation_report.json")

# ============================================================================
# VISUALIZATION
# ============================================================================
tasks = list(all_results.keys())
metrics = ["accuracy", "f1", "precision", "recall"]

fig, axes = plt.subplots(1, len(tasks), figsize=(12, 5))
if len(tasks) == 1:
    axes = [axes]

for idx, task in enumerate(tasks):
    ax = axes[idx]
    a_scores = [all_results[task]["model_a"][m] for m in metrics]
    b_scores = [all_results[task]["model_b"][m] for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35

    bars_a = ax.bar(x - width/2, a_scores, width, label='Model A', color='steelblue')
    bars_b = ax.bar(x + width/2, b_scores, width, label='Model B', color='coral')

    ax.set_ylabel('Score')
    ax.set_title(f'{task.upper()} Evaluation')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Add significance indicator
    sig = all_results[task]["significance"]["significant"]
    p_val = all_results[task]["significance"]["bootstrap_p"]
    ax.text(0.5, 0.95, f"Significant: {sig}\np={p_val:.4f}",
           transform=ax.transAxes, ha='center', va='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig("src/phase157/evaluation_results.png", dpi=150)
print("Saved visualization to src/phase157/evaluation_results.png")

print("\n" + "="*60)
print("PHASE 157 COMPLETE")
print("="*60)
print("You have built a real evaluation harness.")
print("This is how ML engineers decide if a new model")
print("is actually better or just lucky.")

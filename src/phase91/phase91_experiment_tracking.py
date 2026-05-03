"""
Phase 91: Experiment Tracking & MLOps Maturity
NumPy training simulation with a JSON-based experiment tracker.
No PyTorch. Uses matplotlib Agg backend for non-interactive plot saving.
"""

import json
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)


class JSONExperimentTracker:
    """
    A lightweight experiment tracker that logs runs to a JSON file.
    In production you might use MLflow, but this shows the underlying concept.
    """

    def __init__(self, log_path="experiment_log.json"):
        self.log_path = log_path
        # Load existing log if present so we can append new runs
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                self.runs = json.load(f)
        else:
            self.runs = []

    def start_run(self, run_name, hyperparams):
        """Initialize a new run with a name, timestamp, and hyperparameters."""
        self.current_run = {
            "run_name": run_name,
            "start_time": time.time(),
            "hyperparams": hyperparams,
            "metrics": [],  # list of dicts, one per epoch
            "artifacts": {},  # artifact name -> content summary
        }

    def log_metric(self, epoch, loss, accuracy):
        """Append per-epoch metrics. Real trackers also log learning rate, etc."""
        self.current_run["metrics"].append(
            {"epoch": epoch, "loss": float(loss), "accuracy": float(accuracy)}
        )

    def log_artifact(self, artifact_name, artifact_data):
        """
        Save an artifact (e.g., model weights) to disk and record its path.
        artifact_data should be a NumPy array or serializable object.
        """
        artifact_dir = "artifacts"
        os.makedirs(artifact_dir, exist_ok=True)
        artifact_path = os.path.join(artifact_dir, f"{self.current_run['run_name']}_{artifact_name}.npy")
        np.save(artifact_path, artifact_data)
        self.current_run["artifacts"][artifact_name] = artifact_path

    def end_run(self):
        """Finalize the run, append it to the log, and persist to JSON."""
        self.current_run["end_time"] = time.time()
        duration = self.current_run["end_time"] - self.current_run["start_time"]
        self.current_run["duration_seconds"] = duration
        self.runs.append(self.current_run)
        with open(self.log_path, "w") as f:
            json.dump(self.runs, f, indent=2)

    def compare_runs(self, metric_name="accuracy"):
        """
        Print a simple comparison table of all runs based on the final epoch
        value of the chosen metric.
        """
        print(f"\n=== Run Comparison (final {metric_name}) ===")
        print(f"{'Run Name':<20} {'Hyperparams':<30} {metric_name.capitalize():<10}")
        for run in self.runs:
            if run["metrics"]:
                final_value = run["metrics"][-1][metric_name]
                hparams = json.dumps(run["hyperparams"])
                print(f"{run['run_name']:<20} {hparams:<30} {final_value:<10.4f}")


def generate_data(n_samples=200, noise=0.5):
    """
    Generate a simple 2D classification dataset.
    Returns X (n_samples, 2) and y (n_samples,).
    """
    # Two Gaussian blobs centered at (-1, -1) and (1, 1)
    n_per_class = n_samples // 2
    X0 = np.random.randn(n_per_class, 2) * noise + np.array([-1.0, -1.0])
    X1 = np.random.randn(n_per_class, 2) * noise + np.array([1.0, 1.0])
    X = np.vstack([X0, X1])
    y = np.hstack([np.zeros(n_per_class), np.ones(n_per_class)])
    return X, y


def train_model(X, y, learning_rate, n_epochs, tracker, run_name):
    """
    Train a tiny linear classifier using gradient descent.
    Weights are logged as an artifact at the end.
    """
    n_features = X.shape[1]
    # Initialize weights and bias
    W = np.random.randn(n_features) * 0.01
    b = 0.0

    tracker.start_run(run_name, hyperparams={"lr": learning_rate, "epochs": n_epochs})

    for epoch in range(1, n_epochs + 1):
        # Linear logits
        logits = X @ W + b
        # Sigmoid activation
        preds = 1.0 / (1.0 + np.exp(-logits))
        # Binary cross-entropy loss (clipped for numerical stability)
        eps = 1e-7
        loss = -np.mean(y * np.log(preds + eps) + (1 - y) * np.log(1 - preds + eps))

        # Accuracy
        acc = np.mean((preds >= 0.5).astype(float) == y)

        # Gradients
        dlogits = preds - y
        dW = X.T @ dlogits / len(y)
        db = np.mean(dlogits)

        # Update
        W -= learning_rate * dW
        b -= learning_rate * db

        tracker.log_metric(epoch, loss, acc)

    # Log final weights as an artifact
    tracker.log_artifact("model_weights", {"W": W, "b": b})
    tracker.end_run()
    return W, b


def plot_runs(tracker, output_path="phase91_runs.png"):
    """
    Plot loss curves for all tracked runs.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    for run in tracker.runs:
        epochs = [m["epoch"] for m in run["metrics"]]
        losses = [m["loss"] for m in run["metrics"]]
        ax.plot(epochs, losses, label=run["run_name"], marker="o", markersize=3)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Phase 91: Experiment Tracking Loss Curves")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_path)
    print(f"Saved plot to {output_path}")


def main():
    # Prepare data
    X, y = generate_data(n_samples=200, noise=0.8)

    # Initialize tracker
    tracker = JSONExperimentTracker(log_path="phase91_experiments.json")

    # Run 1: conservative learning rate
    train_model(X, y, learning_rate=0.1, n_epochs=20, tracker=tracker, run_name="run_lr0.1")

    # Run 2: aggressive learning rate (might oscillate)
    train_model(X, y, learning_rate=0.5, n_epochs=20, tracker=tracker, run_name="run_lr0.5")

    # Run 3: very small learning rate
    train_model(X, y, learning_rate=0.01, n_epochs=20, tracker=tracker, run_name="run_lr0.01")

    # Compare runs
    tracker.compare_runs(metric_name="accuracy")

    # Visualize
    plot_runs(tracker, output_path="phase91_runs.png")

    # Show artifact locations
    print("\nArtifacts logged:")
    for run in tracker.runs:
        print(f"  {run['run_name']}: {run['artifacts']}")


if __name__ == "__main__":
    main()

"""
Phase 80 MLOps & Production Monitoring — Colab Real-Workflow Script
====================================================================

This script is designed to run in Google Colab (or any Jupyter environment)
and demonstrates a **complete MLOps loop**:

  1. Train a model and log everything (MLflow / Weights & Biases).
  2. Simulate production data that gradually drifts.
  3. Detect drift using a statistical library (alibi-detect / Evidently).
  4. Trigger retraining when drift exceeds a threshold.
  5. Promote the new model through a Model Registry (Staging → Production).

Copy-paste this into a Colab cell, install the commented dependencies,
and run top-to-bottom.
"""

# =============================================================================
# 0. INSTALL DEPENDENCIES (uncomment in Colab)
# =============================================================================
# !pip install -q scikit-learn mlflow alibi-detect evidently pandas numpy matplotlib

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 1. EXPERIMENT TRACKING SETUP
# =============================================================================
# WHY: Without logging, you cannot reproduce results, compare runs, or debug
# production issues.  Every hyperparameter, metric, and artifact must be tied
# to a unique run ID.

USE_MLFLOW = True  # Set to False to use Weights & Biases instead

if USE_MLFLOW:
    import mlflow
    import mlflow.sklearn
    from mlflow.tracking import MlflowClient

    mlflow.set_tracking_uri("sqlite:///mlflow.db")  # local SQLite backend for demo
    mlflow.set_experiment("phase80_fraud_detection")
    client = MlflowClient()
else:
    import wandb
    # wandb.login()  # required once per Colab session


def start_run(run_name: str):
    """Start a tracked run in whichever backend is active."""
    if USE_MLFLOW:
        return mlflow.start_run(run_name=run_name)
    else:
        wandb.init(project="phase80-mlops", name=run_name, reinit=True)
        return None


def log_params(params: dict):
    """Log hyperparameters."""
    if USE_MLFLOW:
        mlflow.log_params(params)
    else:
        wandb.config.update(params)


def log_metrics(metrics: dict, step: int = None):
    """Log scalar metrics."""
    if USE_MLFLOW:
        mlflow.log_metrics(metrics, step=step)
    else:
        wandb.log(metrics, step=step)


def log_model(model, artifact_path: str, registered_model_name: str = None):
    """Log the trained model artifact and optionally register it."""
    if USE_MLFLOW:
        mlflow.sklearn.log_model(
            model,
            artifact_path=artifact_path,
            registered_model_name=registered_model_name
        )
    else:
        # W&B model registry
        wandb.sklearn.plot_learning_curve(model, X_train, y_train)
        wandb.sklearn.plot_feature_importances(model, feature_names)
        # Save artifact
        model_artifact = wandb.Artifact("fraud-model", type="model")
        # (In practice you would add files to the artifact here)
        wandb.log_artifact(model_artifact)


# =============================================================================
# 2. GENERATE REFERENCE DATA & TRAIN BASELINE MODEL
# =============================================================================
# WHY: We need a reproducible baseline.  We log the dataset hash so we know
# exactly what the model saw.

np.random.seed(42)
N = 5000

# Feature 1: transaction amount (log-normal-ish)
amt = np.random.lognormal(3, 1, N)
# Feature 2: hour of day
hour = np.random.randint(0, 24, N)
# Feature 3: account age in days
age = np.random.poisson(365, N)

# Baseline concept: fraud = high amount AND late night
fraud_prob = 1 / (1 + np.exp(-(-5 + 0.5 * np.log(amt) + 0.3 * (hour > 20).astype(float))))
y = (np.random.rand(N) < fraud_prob).astype(int)

X = pd.DataFrame({
    'amount': amt,
    'hour': hour,
    'age': age
})
feature_names = list(X.columns)

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Log dataset fingerprint
dataset_hash = pd.util.hash_pandas_object(X_train).sum() % (2**32)

hyperparams = {
    "n_estimators": 100,
    "max_depth": 6,
    "min_samples_split": 10,
    "random_state": 42,
    "dataset_hash": dataset_hash
}

with start_run("baseline_training"):
    log_params(hyperparams)

    # WHY: Random Forest is robust and requires little preprocessing,
    # letting us focus on the MLOps workflow rather than feature engineering.
    model = RandomForestClassifier(**{k: v for k, v in hyperparams.items() if k != "dataset_hash"})
    model.fit(X_train, y_train)

    y_val_pred = model.predict(X_val)
    val_acc = accuracy_score(y_val, y_val_pred)
    val_f1 = f1_score(y_val, y_val_pred)

    log_metrics({"val_accuracy": val_acc, "val_f1": val_f1})
    log_model(model, artifact_path="model", registered_model_name="fraud_detector")

    print(f"[BASELINE] Validation accuracy: {val_acc:.4f} | F1: {val_f1:.4f}")
    baseline_metrics = {"accuracy": val_acc, "f1": val_f1}

# =============================================================================
# 3. SIMULATE PRODUCTION DATA WITH DRIFT
# =============================================================================
# WHY: In production you do not get i.i.d. samples from the training set.
# Users change behaviour, competitors launch campaigns, and upstream pipelines
# bug out.  We simulate three regimes:
#   Months 1-2  — stable (same as training)
#   Months 3-5  — data drift (amounts inflate, hours shift to night)
#   Months 6-8  — concept drift (fraud pattern inverts: day-time high-amount)

production_batches = []

for month in range(1, 9):
    n = 800
    if month <= 2:
        # STABLE
        amt_m = np.random.lognormal(3, 1, n)
        hour_m = np.random.randint(0, 24, n)
        age_m = np.random.poisson(365, n)
        fraud_prob_m = 1 / (1 + np.exp(-(-5 + 0.5 * np.log(amt_m) + 0.3 * (hour_m > 20))))
    elif month <= 5:
        # DATA DRIFT only: P(X) changes, P(y|X) stays the same
        # Amounts balloon (inflation), everyone transacts at night.
        amt_m = np.random.lognormal(5, 1.2, n)   # fatter, higher
        hour_m = np.random.choice(np.arange(20, 24), n)  # only late night
        age_m = np.random.poisson(100, n)        # younger accounts
        # Concept is UNCHANGED: still high-amount + late-night = fraud
        fraud_prob_m = 1 / (1 + np.exp(-(-5 + 0.5 * np.log(amt_m) + 0.3 * (hour_m > 20))))
    else:
        # CONCEPT DRIFT: P(y|X) changes
        # Same inflated distribution as months 3-5...
        amt_m = np.random.lognormal(5, 1.2, n)
        hour_m = np.random.choice(np.arange(20, 24), n)
        age_m = np.random.poisson(100, n)
        # ...but the fraud pattern INVERTS: now DAY-TIME + HIGH amount is risky.
        # This mimics a real-world scenario where attackers adapt to the model.
        fraud_prob_m = 1 / (1 + np.exp(-(-5 + 0.5 * np.log(amt_m) - 0.8 * (hour_m > 20))))

    y_m = (np.random.rand(n) < fraud_prob_m).astype(int)
    X_m = pd.DataFrame({"amount": amt_m, "hour": hour_m, "age": age_m})
    production_batches.append({"month": month, "X": X_m, "y": y_m})

# =============================================================================
# 4. DRIFT DETECTION WITH ALIBI-DETECT (or Evidently)
# =============================================================================
# WHY: You cannot wait for ground-truth labels to know your model is failing.
# Drift detectors look at the INPUT distribution and scream *before* accuracy
# collapses.  We use the Maximum Mean Discrepancy (MMD) test because it is
# non-parametric and works well on tabular data.

try:
    from alibi_detect.cd import TabularDrift
    detector = TabularDrift(X_train.values, p_val=0.05)
    USE_ALIBI = True
except Exception:
    USE_ALIBI = False
    print("[WARN] alibi-detect not available; falling back to manual PSI.")


def detect_drift(X_ref: pd.DataFrame, X_prod: pd.DataFrame) -> dict:
    """Return drift score and boolean flag."""
    if USE_ALIBI:
        preds = detector.predict(X_prod.values)
        return {
            "is_drift": bool(preds["data"]["is_drift"]),
            "p_val": float(preds["data"]["p_val"]),
            "distance": float(preds["data"].get("distance", 0.0))
        }
    else:
        # Manual PSI fallback (univariate average)
        psi_total = 0.0
        for col in X_ref.columns:
            # decile bins
            bins = np.percentile(X_ref[col].values, np.linspace(0, 100, 11))
            bins = np.unique(bins)
            if len(bins) < 3:
                continue
            ref_hist, _ = np.histogram(X_ref[col].values, bins=bins)
            prod_hist, _ = np.histogram(X_prod[col].values, bins=bins)
            ref_pct = (ref_hist + 1e-10) / (ref_hist.sum() + 1e-10)
            prod_pct = (prod_hist + 1e-10) / (prod_hist.sum() + 1e-10)
            psi_col = np.sum((prod_pct - ref_pct) * np.log(prod_pct / ref_pct))
            psi_total += psi_col
        avg_psi = psi_total / len(X_ref.columns)
        # PSI heuristic: > 0.25 is significant drift
        return {"is_drift": avg_psi > 0.25, "psi": avg_psi}


# =============================================================================
# 5. PRODUCTION MONITORING LOOP
# =============================================================================
# WHY: This is the heart of MLOps.  Every production batch is scored for drift
# and (if labels are available) for accuracy.  When drift crosses the threshold,
# we trigger retraining.

DRIFT_THRESHOLD = 3  # number of consecutive drift flags before retraining
consecutive_drift = 0
retrain_triggered = False

print("\n" + "=" * 70)
print(f"{'Month':>6} | {'Acc':>8} | {'Drift?':>8} | {'Score':>12} | {'Action'}")
print("=" * 70)

for batch in production_batches:
    month = batch["month"]
    X_prod = batch["X"]
    y_prod = batch["y"]

    # 5a. Predict
    y_pred = model.predict(X_prod)
    acc = accuracy_score(y_prod, y_pred)

    # 5b. Detect drift on inputs
    drift_result = detect_drift(X_train, X_prod)
    is_drift = drift_result["is_drift"]
    score = drift_result.get("p_val", drift_result.get("psi", 0.0))

    # 5c. Decision logic
    action = "Monitor"
    if is_drift:
        consecutive_drift += 1
    else:
        consecutive_drift = 0

    if consecutive_drift >= DRIFT_THRESHOLD and not retrain_triggered:
        action = "RETRAIN TRIGGERED"
        retrain_triggered = True
        # -----------------------------------------------------------------
        # 6. RETRAINING PIPELINE
        # -----------------------------------------------------------------
        # WHY: When the world changes, the model must relearn.  We combine
        # the original training data with recent production data (assuming
        # labels arrive with delay) and train a fresh model.

        # In a real system you would use a labelled window of production data.
        # Here we simulate by adding the current batch.
        X_new_train = pd.concat([X_train, X_prod], ignore_index=True)
        y_new_train = np.concatenate([y_train, y_prod])

        with start_run(f"retraining_month_{month}"):
            new_params = hyperparams.copy()
            new_params["n_estimators"] = 150  # slightly more capacity
            log_params(new_params)

            new_model = RandomForestClassifier(
                **{k: v for k, v in new_params.items() if k != "dataset_hash"}
            )
            new_model.fit(X_new_train, y_new_train)

            new_val_pred = new_model.predict(X_val)
            new_acc = accuracy_score(y_val, new_val_pred)
            new_f1 = f1_score(y_val, new_val_pred)
            log_metrics({"val_accuracy": new_acc, "val_f1": new_f1})
            log_model(new_model, artifact_path="model", registered_model_name="fraud_detector")

            print(f"\n[RETRAIN] New model validated — accuracy: {new_acc:.4f} | F1: {new_f1:.4f}")

            # ---------------------------------------------------------
            # 7. MODEL REGISTRY WORKFLOW
            # ---------------------------------------------------------
            # WHY: A registry separates "training" from "serving".  You never
            # overwrite the production model directly.  Instead you stage the
            # new model, run shadow tests / canary traffic, and only then
            # promote it to Production.

            if USE_MLFLOW:
                # Find the latest version of the registered model
                latest_versions = client.get_latest_versions("fraud_detector", stages=["Staging"])
                if latest_versions:
                    for v in latest_versions:
                        client.transition_model_version_stage(
                            name="fraud_detector",
                            version=v.version,
                            stage="Archived"
                        )

                # Get the version we just logged (it is the latest)
                mv = client.get_latest_versions("fraud_detector", stages=["None"])[-1]
                client.transition_model_version_stage(
                    name="fraud_detector",
                    version=mv.version,
                    stage="Staging"
                )
                print(f"[REGISTRY] Model version {mv.version} moved to Staging.")
                print("[REGISTRY] In production you would A/B test before promoting to Production.")
            else:
                wandb.run.summary["model_stage"] = "Staging"
                print("[REGISTRY] Model artifact tagged as Staging in W&B.")

            # Replace in-memory model for the rest of the simulation
            model = new_model
            consecutive_drift = 0  # reset after retraining

    print(f"{month:6d} | {acc:8.3f} | {str(is_drift):>8} | {score:12.4f} | {action}")

print("=" * 70)

# =============================================================================
# 8. SUMMARY VISUALISATION (optional, runs only if matplotlib is available)
# =============================================================================
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    months_list = [b["month"] for b in production_batches]
    accs_list = [accuracy_score(b["y"], model.predict(b["X"])) for b in production_batches]

    # Recompute drift scores for plotting
    drift_scores = []
    for b in production_batches:
        dr = detect_drift(X_train, b["X"])
        drift_scores.append(dr.get("p_val", dr.get("psi", 0.0)))

    fig, ax1 = plt.subplots(figsize=(10, 5))
    color = 'tab:blue'
    ax1.set_xlabel('Production Month')
    ax1.set_ylabel('Accuracy', color=color)
    ax1.plot(months_list, accs_list, color=color, marker='o', label='Accuracy')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axvline(2.5, color='gray', linestyle='--', alpha=0.5, label='Stable → Drift')
    ax1.axvline(5.5, color='red', linestyle='--', alpha=0.5, label='Drift → Concept')

    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Drift Score (p-val or PSI)', color=color)
    ax2.plot(months_list, drift_scores, color=color, marker='s', linestyle='--', label='Drift Score')
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.title("Production Monitoring: Accuracy vs Drift Score")
    plt.savefig("production_monitoring.png", dpi=150)
    print("\nMonitoring plot saved to production_monitoring.png")
except Exception as e:
    print(f"Plotting skipped: {e}")

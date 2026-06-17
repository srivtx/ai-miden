## Why it exists (THE PROBLEM)

You train a model. Then you make changes. New data, new hyperparameters, new model architecture. You retrain. But did the new version actually improve? Did you accidentally break something? How do you deploy the new version without downtime? How do you roll back if it's worse?

Without CI/CD: you SSH into a server, `git pull`, kill the process, restart manually, and pray. If it's broken, you SSH back and restore the old version from memory. At 3 AM. During a critical launch.

**CI/CD for ML** automates this. Every code change triggers: training → evaluation → model registry → canary deployment → full rollout. If any step fails, the pipeline stops and sends you a message. If the new model is worse than the old one, it never reaches production.

## Definition (very simple)

**CI (Continuous Integration):** When you push code, automatically run: tests, linting, a mini-training run (smoke test), and evaluation against a baseline. The CI check fails if the model doesn't reach target loss, if accuracy drops, or if tests break.

**CD (Continuous Delivery/Deployment):** Automatically push the trained model to a model registry, then deploy to staging (canary: 5% of traffic), monitor for 1 hour, promote to production (100% of traffic) OR rollback automatically if metrics degrade.

**The pipeline (GitHub Actions example):**
```
Push to main
    ↓
[CI] Run tests + lint + smoke train
    ↓
[CI] Evaluate vs. baseline model (must pass to continue)
    ↓
[CD] Push model artifact to registry (MLflow / S3 / HuggingFace)
    ↓
[CD] Deploy to staging (kubectl apply)
    ↓
[CD] Canary: route 5% traffic, monitor latency/error for 1h
    ↓
[CD] If healthy: promote to 100%. If degraded: auto-rollback.
```

## Practice: Minimal CI for cortexcode

```yaml
# .github/workflows/ml_ci.yml
name: ML CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install torch
      - name: Smoke train (200 steps)
        run: |
          python cortexcode_torch.py train \
            --data-dir /tmp/test_data \
            --steps 200 --dim 64 --n-layers 2 \
            --out /tmp/model.pt
      - name: Check loss threshold
        run: |
          # Verify loss is below threshold (fails CI if not)
          python -c "
          import torch
          ckpt = torch.load('/tmp/model.pt')
          final_loss = ckpt['losses'][-1]
          assert final_loss < 3.0, f'Loss {final_loss} > 3.0 threshold'
          print(f'Smoke test passed: loss={final_loss:.4f}')
          "

  evaluate:
    needs: smoke-test
    runs-on: ubuntu-latest
    steps:
      - name: Compare to baseline
        run: |
          # Download baseline model from registry
          # Run eval on held-out set
          # Assert new_loss < baseline_loss * 1.05
          pass
```

Now: every push to main automatically smoke-trains for 200 steps and checks the loss. If you push broken code, CI fails BEFORE merging to main. No broken model ever reaches training cluster.

## Key properties

| What | Without CI/CD | With CI/CD |
|---|---|---|
| Code check | Manual (`python -c "import train"`) | Automated (GitHub Actions) |
| Smoke test | Manual (run small training) | Automated on every push |
| Model comparison | Manual (scroll terminal) | Automated (assert new > old) |
| Deploy | SSH + manual restart | `kubectl` + rolling update |
| Rollback | Revert code + restart from memory | `kubectl rollout undo` (one click) |
| Model registry | `.pt` file on disk | MLflow / S3 with version, metadata |
| Audit trail | None | Git history + MLflow lineage |

## Tech comparison

| Tool | Best for | Notes |
|---|---|---|
| **GitHub Actions** | CI (the build/test part) | Free for public repos, 2000 min/month |
| **Kubeflow Pipelines** | Full ML pipeline (K8s) | Heavy; for large teams |
| **Argo Workflows** | K8s-native orchestration | Lighter than Kubeflow |
| **Airflow** | Scheduled retraining | Classic ETL style, not ML-specific |
| **Prefect / Dagster** | Modern data pipelines | Good for ML, Python-native |
| **MLflow** | Model registry + tracking | Standard choice for model versioning |

## Common confusion

1. **"CI/CD is overkill for a solo project."** No. The FIRST time you break something, get confused about which model version you're running, or lose a trained model because you overwrote the file, CI/CD pays for itself. Minimum: GitHub Actions smoke test. 15 lines of YAML.

2. **"I can't run a full training run in CI."** You don't need to. Smoke train for 200 steps (verify the code runs and loss decreases). Full training happens on your GPU cluster. CI verifies the code is correct; GPU cluster verifies the model is good.

3. **"Model versioning is hard."** `model_v1.pt`, `model_v2_final.pt`, `model_v2_final_real.pt` — this is what you have without versioning. MLflow: `mlflow.log_model(model, "cortexcode")` auto-creates version v1, v2, v3 with: timestamp, parameters, metrics, and the artifact. Query: `mlflow.search_runs(filter_string="params.dim = 256").sort_values("metrics.loss")`. One line.

## Connection to cortexcode

Add `.github/workflows/ml_ci.yml` to the repo (the YAML above). Every push smoke-checks the training code. Add a `evaluate.py` script that loads the new model, runs eval on a held-out set, and asserts improvement. Automate the whole quality gate.

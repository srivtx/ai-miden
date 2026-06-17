## Why it exists (THE PROBLEM)

You train a model. Loss goes from 4.0 to 1.5. Was that good? Without tracking, you don't know. You can't compare this run to last week's run. You can't tell if changing the learning rate from 5e-4 to 1e-3 helped or hurt. You can't reproduce your best result because you don't remember which seed you used.

**Every training run generates evidence.** Loss curves, hyperparameters, sample outputs, GPU utilization, memory usage. Without systematic tracking, this evidence is lost the moment you close the notebook.

**Experiment tracking** (wandb, MLflow, TensorBoard) solves this. Every run is logged with: hyperparameters (lr, batch_size, dim, layers), metrics over time (loss, accuracy, perplexity), system metrics (GPU temp, VRAM, CPU), artifacts (model checkpoints, sample outputs), and a unique ID. You can compare any two runs in a dashboard, reproduce any result from its config, and share it with a link.

## Definition (very simple)

**Experiment tracking** is structured logging for ML training. Instead of `print(f"Step {step}: loss {loss:.4f}")`, you write `wandb.log({"loss": loss, "step": step})`. The platform (wandb/MLflow) collects, stores, and visualizes everything.

The key primitives:
- **Run:** one training session with a unique ID
- **Config:** hyperparameters captured at start (python `wandb.init(config=args)`)
- **Metric:** a value logged over time (loss, accuracy, learning rate)
- **Artifact:** a file logged once (model checkpoint, evaluation report, sample image)

After logging, you get:
- A dashboard showing all runs, filterable by config (only show runs with dim=256)
- Side-by-side comparison of any two runs
- Automatic line plots for all scalar metrics
- Histograms for gradients/weights (debugging)
- Shareable reports

## Real-life analogy

**Without tracking:** You're a chef who throws ingredients together without measuring. The dish turns out great. Tomorrow, you can't recreate it because you don't remember how much salt you added.

**With tracking:** You write down every ingredient, every measurement, every cooking time, and a photo of the final dish. Next week, you compare 5 variations side-by-side. You know EXACTLY which combination produced the best result.

**wandb/MLflow = a lab notebook with a search engine.** Every experiment is recorded. You can query: "show me all runs from last month with dim=384 and lr<1e-3 sorted by lowest loss." 3 seconds. Without tracking: scroll through terminal history. 30 minutes.

## Tiny numeric example

Three training runs with different learning rates:

```python
# Without tracking:
print("lr=1e-3: loss went from 4.0 to 1.5")  # gone when terminal scrolls past
print("lr=5e-4: loss went from 4.2 to 1.3")
print("lr=1e-4: loss went from 4.5 to 2.1")

# With tracking:
wandb.init(project="cortexcode", config={"lr": 5e-4, "dim": 256, "n_layers": 4, "dataset": "rich"})
for step in range(10000):
    loss = train_step()
    wandb.log({"loss": loss, "step": step, "lr": scheduler.get_last_lr()[0]})
wandb.finish()
```

Now you can answer:
- Which learning rate converged fastest? → Filter by `lr`, plot loss curves overlayed
- Did the model overfit? → Compare train_loss vs val_loss over steps
- What was the best loss? → `wandb.Api().runs("cortexcode").filter({"config.lr": 5e-4}).summary["best_loss"]`
- Can I reproduce this? → Yes, the config is stored: `{"lr": 5e-4, "dim": 256, ...}`

## Key properties

| Property | print() | wandb / MLflow |
|---|---|---|
| Persistence | Lost on disconnect | Cloud storage (free tier) |
| Comparison | Manual (memory) | Side-by-side plots |
| Filtering | Manual grep | Structured query |
| Reproduction | Human memory | Stored config dict |
| Sharing | Screenshot | Link to dashboard |
| System metrics | No | GPU temp, VRAM, CPU (auto) |
| Artifact versioning | No | Yes (model.pt → v0, v1, v2) |
| Gradient histograms | No | Yes (debug vanishing gradients) |
| Collaboration | No | Team workspace |

## Common confusion

1. **"I can just save logs to a file."** You can, but you'll implement 80% of what wandb gives you: log rotation, structured query, visualization, comparison, sharing. At 80% of the effort for 20% of the features. wandb: `pip install wandb`, `wandb.init()`, `wandb.log()`. Three lines.

2. **"My runs are small (15 min) — tracking is overkill."** The SHORTER your runs, the MORE runs you'll do. 10 runs × 15 min = 2.5 hours. After 2.5 hours, you have 10 runs to compare. Tracking pays off immediately.

3. **"It's too slow."** wandb and MLflow are async. `wandb.log()` sends data to a background thread. No impact on training speed. The Python library collects metrics in memory and flushes periodically.

4. **"I train in Colab — can't use wandb."** Colab supports wandb natively. `!pip install wandb`, `wandb.init(project="cortexcode")`. Same as local. Data shows up at wandb.ai.

## Tech comparison

| Tool | Best for | Free tier |
|---|---|---|
| **wandb** | Quick setup, dashboards | 100 GB, public projects |
| **MLflow** | Self-hosted, open-source | Free (self-hosted) |
| **TensorBoard** | Local, embedded | Free (local) |
| **Neptune** | Teams, collaboration | 200h/month |
| **Comet ML** | Large-scale, artifacts | Public projects |

**wandb is the default choice** for most ML teams. MLflow if you need self-hosted (no third-party dependency). TensorBoard if you're already in the TF ecosystem. All three support PyTorch.

## Connection to our projects

**cortexcode:** Replace all `print(f"Step {step}: loss {loss:.4f}")` with `wandb.log({"loss": loss}, step=step)`. Add `wandb.init(config=args)` at startup. Hook in at the top of `train()` in `cortexcode_torch.py`. ~10 lines.

**Immediately after one run:** `python cortexcode_torch.py train ...` logs to wandb. Dashboard shows loss curve, config, system metrics. You can share the URL: "here's the run, loss went from 4.0 to 1.5." One link instead of a wall of pasted output.

**What to learn:** `wandb.init()` → `wandb.log()` → `wandb.finish()`. Three functions. ~10 lines of code. The rest is automatic.

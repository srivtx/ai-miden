## What Is Production MLOps?

---

### The Problem

You trained a great model. It scores 92% on your test set. You deploy it manually on a Friday afternoon. By Monday, traffic has doubled, latency is spiking, and a competitor's model is being A/B tested against yours in production because nobody told the product team not to. You have no rollback plan. The old model weights are on a laptop that is now in another country. Your monitoring dashboards are localhost-only because you never set up authentication. This is not a deployment; it is a dare.

Production MLOps for LLMs is the discipline of treating model deployment like software deployment: versioned, tested, monitored, and reversible. But LLMs add unique challenges: models are multi-gigabyte artifacts, inference is stateful (KV cache), evaluation is subjective, and failures are probabilistic rather than deterministic.

---

### Definition

**Production MLOps** (machine learning operations) is the set of practices, tools, and workflows that enable reliable, scalable, and observable deployment of machine learning models. For LLMs, MLOps encompasses CI/CD for model artifacts, automated evaluation pipelines, A/B testing, canary deployments, rollback strategies, cost tracking per request, and infrastructure scaling. It bridges the gap between research experiments and 24/7 production systems.

**How it works:**
```
LLM MLOps lifecycle:
  ┌─────────────────────────────────────────┐
  │  1. Train / fine-tune                   │
  ├─────────────────────────────────────────┤
  │  2. Evaluate (benchmarks + human review)│
  ├─────────────────────────────────────────┤
  │  3. Package (weights + tokenizer + cfg) │
  ├─────────────────────────────────────────┤
  │  4. Deploy (canary → 10% → 50% → 100%)  │
  ├─────────────────────────────────────────┤
  │  5. Monitor (latency, drift, cost)      │
  ├─────────────────────────────────────────┤
  │  6. Rollback if alerts fire             │
  ├─────────────────────────────────────────┤
  │  7. Retrain when drift accumulates      │
  └─────────────────────────────────────────┘
```

**Key practices:**
- **CI/CD for models:** every commit triggers training, evaluation, and packaging. Model weights are versioned artifacts in an artifact store (MLflow, Weights & Biases).
- **A/B testing:** route a percentage of traffic to a new model version; compare latency, cost, user satisfaction, and task success against the baseline.
- **Canary deployments:** release to 1% of users, then 5%, then 25%, watching metrics at each stage. Abort if error rate or latency degrades.
- **Rollback strategies:** keep the previous model hot in memory or on disk so you can revert in seconds, not hours. Blue-green deployments maintain two identical environments.
- **Cost tracking per request:** tag every request with model version, compute cost, and token count. Attribute cloud spend to specific features or user segments.

**Why this matters:**
- A failed deployment without rollback can cost hours of downtime and millions of tokens of user frustration
- A/B testing prevents "it worked in the lab" disasters by validating on real traffic
- Cost tracking reveals that 20% of your users generate 80% of your inference bill

---

### Real-Life Analogy

A professional theater production.
- **Research/training:** Rehearsing the play in a small studio. Actors experiment with lines, directors cut scenes. This is safe because no audience sees the mistakes.
- **Evaluation:** Dress rehearsals with a small invited audience. You measure laughs, pacing, and scene transitions. This is your benchmark suite.
- **Canary deployment:** Preview week in one city. You watch reviews and ticket sales. If the lead forgets their lines, you fix it before Broadway.
- **Full deployment:** Broadway opening. The show runs eight times a week. Understudies are ready (rollback). Stage managers monitor every cue (monitoring). If a prop breaks mid-show, the stage manager swaps it without stopping the play (hot failover).
- **A/B testing:** Two directors alternate nights. You track which director's version gets better reviews and higher ticket prices. The winner becomes the permanent show.

---

### Tiny Numeric Example

**Deploying a new model version (v2) to a chatbot serving 10,000 requests/hour:**

**Canary rollout plan:**
```
Step 1: 1% traffic (100 req/hr)  → monitor for 30 min
Step 2: 5% traffic (500 req/hr)  → monitor for 1 hour
Step 3: 25% traffic (2,500/hr)   → monitor for 2 hours
Step 4: 100% traffic             → full rollout
```

**Metrics at each step:**
```
Step    Error Rate    p95 Latency    User Satisfaction    Cost/1K req
--------------------------------------------------------------------
Baseline   0.5%         210 ms           4.2/5.0            $0.12
1%         0.6%         205 ms           4.1/5.0            $0.11
5%         0.4%         195 ms           4.3/5.0            $0.10
25%        2.1%         890 ms           3.5/5.0            $0.14  ← ALERT
Rollback   0.5%         210 ms           4.2/5.0            $0.12
```

**What happened:** At 25% traffic, the new model's longer outputs caused KV cache eviction and latency spikes. Error rate jumped because requests timed out. Canary caught this before 100% rollout.

**Cost tracking per request:**
```
User segment      Requests    Avg tokens    Total cost    % of spend
-------------------------------------------------------------------
Free tier         6,000       45            $32.40        18%
Pro tier          3,000       180           $194.40       54%
Enterprise        1,000       420           $100.80       28%
```

**The shift:** Pro tier is 30% of users but 54% of cost. MLOps cost tracking tells the product team to either meter Pro tier more aggressively or optimize for longer-context inference.

---

### Common Confusion

1. **"MLOps is just DevOps for models."** MLOps extends DevOps but adds model-specific concerns: non-deterministic outputs, subjective evaluation, large artifact sizes, and data drift. A CI/CD pipeline for a web app does not handle 50 GB model weights or perplexity regression tests.

2. **"A/B testing requires two identical hardware setups."** Not necessarily. You can route 10% of traffic to the new model on the same hardware if the model fits. The key is randomized assignment, not hardware duplication.

3. **"Canary deployment is too slow for hotfixes."** Canary is for planned releases. Hotfixes can use blue-green deployment: switch all traffic from blue to green in seconds. Canary and blue-green are complementary, not exclusive.

4. **"Cost tracking is finance's job."** Engineering must own cost tracking because only engineering knows which model version, batch size, and quantization level was used for each request. Finance sees the bill; engineering sees the levers.

5. **"Rollback means losing data."** Rollback reverts the model, not the database. User conversations and logs are preserved. The only loss is the KV cache, which is rebuilt on the next request.

6. **"Automated evaluation replaces human review."** Automated evaluation (benchmarks, perplexity, drift tests) catches 80% of regressions. Human review catches the remaining 20%, especially subjective quality. Both are necessary.

7. **"MLOps is only for large teams."** Even a solo developer benefits from versioned models, basic monitoring, and a rollback script. The practices scale with team size; the principles are universal.

---

### Where It Is Used in Our Code

`src/phase130/phase130_monitoring_concepts.py` — We simulate an A/B test between two model versions, tracking latency, output length, and a simulated user satisfaction score. We show how canary thresholds prevent a bad model from reaching full traffic.

`src/phase130/phase130_monitoring_colab.py` — We run a real A/B test on Llama-3.2-3B-Instruct: 50% traffic to the base model and 50% to a fine-tuned variant. We compare latency, output length, and simulated user satisfaction, producing a production-style A/B report.

(End of file)

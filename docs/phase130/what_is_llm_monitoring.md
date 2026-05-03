## What Is LLM Monitoring?

---

### The Problem

Your LLM application goes live. For the first week, everything looks fine. Then support tickets start arriving: "The bot gave me nonsense yesterday." You check the logs and see millions of requests. Which one was nonsense? When did it start? Was it a model drift, a bad prompt injection, or a dependency failure? You have no dashboards. You have no baselines. You are flying blind at 30,000 feet with a billion-dollar model and no instruments.

Traditional ML monitoring watches input features and output probabilities. LLMs break that pattern: inputs are free-form text, outputs are free-form text, and "correctness" is subjective. You need a different monitoring stack.

---

### Definition

**LLM monitoring** is the practice of tracking production LLM behavior to detect anomalies, measure performance, and ensure reliability. It covers latency distributions, error rates, token usage, cost per request, input/output length distributions, output quality metrics (perplexity, toxicity, relevance), and user satisfaction signals. Unlike traditional ML monitoring, LLM monitoring must handle unstructured data, subjective quality, and emergent failure modes like hallucinations or prompt injection.

**How it works:**
```
LLM monitoring stack:
  ┌─────────────────────────────────────────┐
  │  Request/response logging               │
  ├─────────────────────────────────────────┤
  │  Metrics aggregation (latency, tokens)  │
  ├─────────────────────────────────────────┤
  │  Quality scoring (perplexity, drift)    │
  ├─────────────────────────────────────────┤
  │  Alerting (thresholds, anomalies)       │
  ├─────────────────────────────────────────┤
  │  Dashboards (real-time visualization)   │
  └─────────────────────────────────────────┘
```

**Key metrics:**
- **Latency:** TTFT (time to first token), TPOT (time per output token), total request time. Track p50, p95, p99.
- **Error rate:** failed generations, timeout responses, HTTP 5xx, malformed JSON outputs.
- **Token usage:** input tokens, output tokens, total tokens per request. This directly determines cost.
- **Input/output length distribution:** sudden spikes in prompt length may indicate abuse or a UI bug.
- **Output quality:** perplexity (is the model speaking its own language?), repetition rate, toxicity score.
- **Cost per request:** derived from token count and model pricing.

**Why this matters:**
- A latency regression from 50 ms to 200 ms at p99 can drop user retention by 20%
- A drift in output length from 50 tokens to 500 tokens can 10× your API bill overnight
- Undetected hallucinations erode trust; you need signals that catch them before users do

---

### Real-Life Analogy

A hospital emergency room.
- **Traditional ML monitoring:** Tracking blood pressure and heart rate. These are single numbers with known healthy ranges. If BP hits 180, you act.
- **LLM monitoring:** Tracking everything in the ER: how long patients wait (latency), how many leave without treatment (error rate), how many tests are ordered per patient (token usage), whether the doctors are suddenly prescribing antibiotics for every complaint (output drift), and whether patient satisfaction scores are dropping (quality). Some signals are numeric; others are patterns in free-text notes.
- **The challenge:** A patient with normal vital signs might still be septic. A model with normal latency might still be hallucinating. You need layered monitoring: vital signs, narrative patterns, and outcome tracking.

---

### Tiny Numeric Example

**One hour of production traffic (3,600 requests):**

**Normal hour:**
```
Requests:           3,600
Mean latency:       120 ms
p95 latency:        280 ms
p99 latency:        450 ms
Error rate:         0.2%
Mean input length:  45 tokens
Mean output length: 78 tokens
Mean perplexity:    2.1
Cost:               $4.32
```

**Anomalous hour (undetected bug in prompt template):**
```
Requests:           3,600
Mean latency:       890 ms      ← 7× higher
p95 latency:        4,200 ms    ← 15× higher
p99 latency:        8,100 ms    ← 18× higher
Error rate:         3.8%        ← 19× higher
Mean input length:  1,240 tokens  ← prompt template duplication bug
Mean output length: 312 tokens
Mean perplexity:    4.7         ← model is confused by garbled input
Cost:               $38.70      ← 9× higher
```

**Without monitoring:** You notice when the credit card bill arrives.
**With monitoring:** An alert fires at minute 4 when input length distribution crosses 2 standard deviations. You rollback the prompt template at minute 6.

---

### Common Confusion

1. **"LLM monitoring is the same as traditional ML monitoring."** No. Traditional monitoring tracks tabular feature drift. LLM inputs are text; drift is semantic, not statistical. You need embeddings and distribution tests on vector representations, not just column means.

2. **"Low latency means the model is working well."** Latency is a necessary but not sufficient condition. A model can return garbage instantly. You must monitor quality and correctness alongside speed.

3. **"Error rate only means HTTP errors."** LLM-specific errors include: empty outputs, infinite repetition, refusals on safe queries, JSON parse failures, and hallucinations. Your error taxonomy must be richer than HTTP status codes.

4. **"Perplexity measures output quality."** Perplexity measures how "surprised" the model is by its own output. Low perplexity can mean bland, repetitive text. High perplexity can mean creative, correct answers or complete nonsense. It is a signal, not a verdict.

5. **"You only need to monitor outputs."** Input monitoring is equally important. A spike in prompt length, a new language appearing, or a flood of identical queries are all early warning signs of attacks, bugs, or viral traffic.

6. **"Monitoring adds too much overhead."** Modern asynchronous logging and sampling reduce overhead to <1% of request time. You can monitor 100% of latency metrics and 10% of quality metrics without impacting serving.

7. **"Human review replaces monitoring."** Human review is the gold standard but scales poorly. Monitoring catches 90% of issues automatically; human review audits the remaining 10% and validates the monitors themselves.

---

### Where It Is Used in Our Code

`src/phase130/phase130_monitoring_concepts.py` — We simulate production LLM traffic and compute latency distributions, error rates, token usage, and cost per request. We show how a sudden input length spike creates cascading cost and latency regressions.

`src/phase130/phase130_monitoring_colab.py` — We run real inference on Llama-3.2-3B-Instruct for 200 requests, logging input length, output length, latency, token count, and output perplexity. We build a dashboard showing these metrics over time and set alert thresholds.

(End of file)

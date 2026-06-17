## Why it exists (THE PROBLEM)

You deploy a model. It works on day 1. On day 3, a user reports gibberish. On day 7, latency is 5× baseline. On day 14, someone changed the input format and didn't tell you. All of this happened silently. You had no alerts, no metrics, no visibility. The model was failing for 11 days while you thought it was fine.

**Monitoring** answers: is the model healthy RIGHT NOW? **Observability** answers: WHY did it break? Together they give you eyes on your system while you sleep.

Every production ML system monitors 4 pillars:
1. **Latency:** p50, p95, p99 over time (is it getting slower?)
2. **Throughput:** requests per second (are we overloaded?)
3. **Error rate:** 4xx/5xx count (are we failing?)
4. **Saturation:** GPU utilization, VRAM, CPU (are we hitting limits?)

Plus ML-specific metrics:
5. **Data drift:** is the input distribution changing? (Covariate shift)
6. **Prediction drift:** is the output distribution changing? (Label shift)
7. **Model quality:** accuracy/bleu/perplexity on a held-out set, updated daily

## Definition (very simple)

**Monitoring** = collecting metrics over time and alerting on thresholds. **Observability** = being able to inspect the system's internal state to answer novel questions. Monitoring tells you "something is wrong" (p99 latency > 500ms). Observability tells you "the batch size grew to 300 because a downstream service is enqueuing faster than we dequeue."

**The stack:**
- **Prometheus:** scrapes metrics from your app every 15s, stores as time series
- **Grafana:** dashboards on top of Prometheus (graphs, alerts)
- **OpenTelemetry:** standardizes traces (follow a request through the system) and logs (structured, searchable)

**A production-ready ML API exposes these endpoints:**
- `/health` — is the process alive? (binary)
- `/ready` — is the model loaded and ready? (binary)
- `/metrics` — Prometheus scrape endpoint (counters, histograms, gauges)

## Practice: instrumenting cortexcode_api.py

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Define metrics
REQUEST_COUNT = Counter('cortexcode_requests_total',
                        'Total requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('cortexcode_request_seconds',
                            'Request latency', ['endpoint'])
MODEL_LOSS = Gauge('cortexcode_model_loss', 'Current model loss')
GPU_VRAM = Gauge('cortexcode_gpu_vram_bytes', 'GPU VRAM used')

@app.get("/metrics")
def metrics():
    # Update live metrics
    if torch.cuda.is_available():
        GPU_VRAM.set(torch.cuda.memory_allocated())
    return Response(generate_latest(), media_type="text/plain")

@app.post("/complete")
@REQUEST_LATENCY.labels(endpoint='complete').time()
def complete(req: CompleteRequest):
    try:
        result = _LOOP.model.generate(...)
        REQUEST_COUNT.labels(endpoint='complete', status='200').inc()
        return result
    except Exception:
        REQUEST_COUNT.labels(endpoint='complete', status='500').inc()
        raise
```

Now Prometheus scrapes `/metrics` every 15s. Grafana shows: request rate, p95 latency, error rate over time. Set an alert: `if latency_p99 > 1s for 5m → page on-call`. You know BEFORE the user complains.

## Key properties

| What | Tool | Scraped/collected | What it tells you |
|---|---|---|---|
| Latency histogram | Prometheus | Every 15s | Is it getting slower over time? |
| Request count | Prometheus | Every 15s | Traffic patterns (hourly, daily) |
| GPU VRAM gauge | Prometheus | Every 15s | Are we close to OOM? |
| Error breakdown | Prometheus | Every 15s | Which endpoint is failing? |
| Data drift | evidently | Daily batch | Is input distribution changing? |
| Prediction drift | evidently | Daily batch | Is output distribution changing? |
| Logs | ELK / Loki | Real-time | Root cause for any error |

## Tech comparison

| Tool | Best for | Free tier |
|---|---|---|
| **Prometheus + Grafana** | Metrics, alerts, dashboards | Self-hosted (free) |
| **ELK (Elasticsearch)** | Log search, root cause analysis | Self-hosted (free) |
| **Grafana Loki** | Logs (lighter than ELK) | Self-hosted (free) |
| **Datadog** | All-in-one, no self-hosting | $15/host/month |
| **evidently** | ML-specific drift detection | Open-source |
| **whylogs** | Data profiling at scale | Open-source |

## Common confusion

1. **"My model is small, I don't need monitoring."** The SMALLER the model, the MORE you benefit from monitoring, because small models are more sensitive to domain shift (a 10M model that overfits jc produces garbage on any non-jc input — you need to know when that happens).

2. **"I'll know when it's broken — users will tell me."** By the time users tell you, the damage is done. A Colab tunnel with 100 users getting gibberish for 3 hours = 100 frustrated users. An alert catches it in 5 minutes.

3. **"Prometheus is hard to set up."** For a single process: `pip install prometheus_client`. Add `/metrics` endpoint. That's it. Grafana can connect to Prometheus on the same machine. For Colab: the metrics endpoint works; Prometheus might not scrape from a trycloudflare URL, but you can run a local `curl` loop instead.

## Connection to cortexcode

Add the `/metrics` endpoint above. When you run `cortexcode_api.py`, Prometheus scrapes it. In Colab, replace the real Prometheus with a simple metrics logger that writes to a file every 30s: `json.dump(metrics_dict, open("/content/metrics.jsonl", "a"))`. Same data, less infrastructure.

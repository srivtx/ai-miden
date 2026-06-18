# The Decisions

> *"If you can't measure it, you can't improve it."*

## Decision 1: Prometheus and not Datadog / New Relic

**Alternatives**:
- **Datadog** — hosted, easy, expensive
- **New Relic** — hosted, similar
- **InfluxDB** — self-hosted, time-series
- **CloudWatch** — AWS-specific

**Why Prometheus: Self-hosted. Free. The standard. Massive ecosystem. Grafana is the de-facto dashboard tool.

**Trade-off**: We have to set up and maintain Prometheus and Grafana. Hosted solutions are easier but cost money.

## Decision 2: RED method

**Alternative**: USE method (Utilization, Saturation, Errors) or other.

**Why RED: It's the standard for web services. Rate, Errors, Duration. Easy to understand.

**Trade-off**: USE is for resources (CPU, memory). RED is for requests. We use RED for HTTP.

## Decision 3: Histogram for latency

**Alternative**: Summary.

**Why Histogram: Server-side aggregation. PromQL computes percentiles. More flexible.

**Trade-off**: Histograms are larger (one time series per bucket). Summaries are smaller but less flexible.

## Decision 4: prom-client and not a custom solution

**Alternative**: Hand-roll the metrics format.

**Why prom-client: The standard. Handles the Prometheus text format. Default metrics. Histograms. Summaries. All built-in.

**Trade-off**: We depend on prom-client. It's well-maintained.

## Decision 5: /metrics endpoint and not push

**Alternative**: Push metrics to a collector (StatsD, etc.).

**Why pull (Prometheus): The standard. Prometheus scrapes. The app is stateless.

**Trade-off**: Pull-based requires Prometheus to know about the app. For dynamic environments (Kubernetes), use service discovery. We use static configs.

## Decision 6: Default Node.js metrics

We use `promClient.collectDefaultMetrics({ register })` to expose Node.js process metrics (CPU, memory, event loop lag, etc.).

**Alternative**: Hand-roll these metrics.

**Why default: They're useful out of the box. CPU spikes, memory leaks, event loop blocking — all visible.

**Trade-off**: Slight overhead. Negligible.

## Decision 7: No tracing

**Alternative**: OpenTelemetry for distributed tracing.

**Why no: Out of scope. For a single service, metrics are enough. For microservices, traces are essential.

**Trade-off**: Can't trace a request across services. We accept this.

## Decision 8: No log aggregation

**Alternative**: Loki, Elasticsearch, Splunk.

**Why no: We have structured logs (project 16). For aggregation, we'd add Loki.

**Trade-off**: Hard to search logs across containers. We accept this.

## Decision 9: Starter dashboard

We provide a Grafana dashboard JSON. It shows RED metrics and Node.js process metrics.

**Alternative**: Build the dashboard from scratch.

**Why starter: It works. Users can customize.

**Trade-off**: The dashboard is opinionated. We accept this.

## Decision 10: No alerting (yet)

**Alternative**: Set up alerts in Prometheus or Grafana.

**Why no: Out of scope. We show how to set up an alert in experiments.

**Trade-off**: No automated alerts. We accept this.

---

## What We Did Not Decide

- **Distributed tracing** — out of scope
- **Log aggregation** — out of scope
- **APM (Application Performance Monitoring)** — out of scope
- **Real User Monitoring (RUM)** — out of scope
- **Synthetic monitoring** — out of scope
- **Status page** — out of scope
- **SLO / SLI** — out of scope
- **Alerting via PagerDuty / Slack** — out of scope
- **Custom dashboards per team** — out of scope
- **Long-term storage** (Prometheus is short-term) — out of scope

Each is a future decision.

---

## The Meta-Decision: The App Is Observable

For 38 projects, we had logs but no metrics. We could see individual events but not trends. We couldn't answer "is latency increasing?" or "is the error rate normal?"

Now the app is observable. Prometheus scrapes metrics. Grafana visualizes them. We can see request rate, error rate, latency, and Node.js process metrics. We can spot problems before users do. We can make data-driven decisions.

This is the foundation of *observability*. From here, every project that needs to see what's happening in production can use these tools. The patterns (RED method, prom-client, Prometheus, Grafana) are universal.

The next project (40, the last) will assume observability exists. The path diverges:

- **Microservice** (project 40): split into services

The app is observable. The path continues.

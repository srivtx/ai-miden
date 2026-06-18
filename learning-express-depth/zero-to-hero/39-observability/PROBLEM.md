# The Problem

> *"The app is in production. Is it working? You can't know unless you measure."*

## Why Logs Are Not Enough

In project 16, we have structured logs. We can see individual events: a request came in, a user was created, etc. But we can't see the *big picture*:

- How many requests per second?
- What's the p99 latency?
- What's the error rate?
- Are requests getting slower over time?
- How many users are online?

Logs are *events*. Metrics are *aggregations*. To answer "how many requests in the last hour?", you don't want to count log lines. You want a metric that increments.

## What Pain Is This Solving?

Imagine the app is in production. Users are complaining "it's slow." You check the logs. You see individual requests, but you can't see the trend. You don't know if latency is 100ms or 5 seconds. You don't know if it's getting worse.

With metrics, you can see:

- Request rate: 100 RPS (steady), 1000 RPS (spike), 10 RPS (problem)
- Latency: p50, p95, p99. Are they increasing? Are some endpoints slower than others?
- Error rate: 0.1% (normal), 5% (problem), 50% (outage)
- Resource usage: memory, CPU, file descriptors, etc.

You can see the trend. You can spot the problem. You can fix it before users complain.

## The Deeper Problem: The Three Pillars of Observability

Observability has three pillars:

1. **Metrics**: numeric values over time (request count, latency, error count)
2. **Logs**: discrete events (a request came in, a user was created)
3. **Traces**: a request's path through the system (which services it touched, how long each took)

We have logs (project 16). This project adds metrics. Traces are out of scope (would use OpenTelemetry).

## What This Project Will Solve

This project will:

1. Add `prom-client` to expose Prometheus metrics
2. Add a `/metrics` endpoint
3. Add custom metrics (request count, request duration, error count)
4. Add default Node.js metrics (memory, CPU, etc.)
5. Set up Prometheus and Grafana (via docker-compose)
6. Create a dashboard (Grafana JSON)

By the end, we can see what's happening in production. We catch problems before users do. We make data-driven decisions.

## What This Project Will *Not* Solve

- **Distributed tracing** — out of scope. Use OpenTelemetry.
- **Log aggregation** — we have structured logs (project 16). For aggregation, use Loki or Elasticsearch.
- **Alerting** — we set up alerts. Out of scope.
- **Custom dashboards** — we provide a starter dashboard. Custom dashboards are a separate effort.
- **APM (Application Performance Monitoring)** — out of scope. Use Datadog, New Relic, etc.

## The Question This Project Answers

> *"How do I see what's happening in production?"*

If you can answer: "use Prometheus for metrics, Grafana for dashboards, expose a `/metrics` endpoint, track RED metrics (Rate, Errors, Duration)," you are ready for project 40.

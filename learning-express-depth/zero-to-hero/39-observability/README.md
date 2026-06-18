# Project 39: The Observability

> *"The app is in production. Is it working? You can't know unless you measure."*

In projects 01-38, we have logs (project 16) but no *metrics*. We can see individual events, but we can't see the big picture:

- How many requests per second?
- What's the p99 latency?
- What's the error rate?
- How much memory is the process using?
- How many users are online?

We need **observability**: metrics, dashboards, and alerts. We use **Prometheus** for metrics collection, **Grafana** for dashboards, and **Prom-client** for the Node.js client.

We add a `/metrics` endpoint that Prometheus scrapes. The endpoint returns metrics in the Prometheus format (text). Prometheus stores them. Grafana visualizes them. We set up alerts for high error rates, high latency, etc.

By the end, we can see what's happening in production. We catch problems before users do. We make data-driven decisions.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why are logs not enough? What is observability?
2. [The Thought](./THOUGHT.md) — How do Prometheus and Grafana work? What are metrics?
3. [The Build](./BUILD.md) — Line-by-line construction of the metrics
4. [The Decisions](./DECISIONS.md) — Why Prometheus? Why Grafana? Why RED metrics?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Observability is the ability to understand a system's internal state from its external outputs. We use **Prometheus** (metrics storage), **Grafana** (dashboards), and **prom-client** (Node.js client). We add a `/metrics` endpoint that Prometheus scrapes. The metrics include request count, request duration, error count, and Node.js process metrics (memory, CPU, etc.).

---

## The Code

```js
const promClient = require('prom-client');

// Create a Registry
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestDurationSeconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.001, 0.01, 0.1, 1, 10],
});
register.registerMetric(httpRequestDurationSeconds);

// Middleware
app.use((req, res, next) => {
  const start = process.hrtime.bigint();
  res.on('finish', () => {
    const duration = Number(process.hrtime.bigint() - start) / 1e9;
    httpRequestDurationSeconds.labels(req.method, req.route?.path || req.path, res.statusCode).observe(duration);
  });
  next();
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

The pain of "is the app working?" is solved. We have metrics. We can see what's happening.

---

## What You Will Have Learned

- What observability is (metrics, logs, traces)
- The RED method (Rate, Errors, Duration)
- How to use prom-client to expose metrics
- How to set up Prometheus and Grafana
- How to create dashboards and alerts

These are the foundations of *observability*. From here, every project that needs to see what's happening in production can use these tools.

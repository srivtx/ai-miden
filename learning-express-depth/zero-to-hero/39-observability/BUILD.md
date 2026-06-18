# The Build

> *"If you can't measure it, you can't improve it."*

We are going to add observability. The change from project 38: add `prom-client`, expose `/metrics`, set up Prometheus and Grafana via docker-compose.

## Setup

```bash
npm install prom-client
```

## The Code

### The Metrics

```js
const promClient = require('prom-client');

const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

const httpRequestDurationSeconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10],
});
register.registerMetric(httpRequestDurationSeconds);

const httpRequestTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status'],
});
register.registerMetric(httpRequestTotal);
```

### The Middleware

```js
app.use((req, res, next) => {
  const start = process.hrtime.bigint();
  res.on('finish', () => {
    const duration = Number(process.hrtime.bigint() - start) / 1e9;
    const route = req.route?.path || req.path;
    httpRequestDurationSeconds.labels(req.method, route, res.statusCode).observe(duration);
    httpRequestTotal.labels(req.method, route, res.statusCode).inc();
  });
  next();
});
```

### The /metrics Endpoint

```js
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

### `prometheus.yml`

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['app:3000']
```

### `docker-compose.yml` (add to existing)

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    # ... (existing config)

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
```

## Run It

```bash
docker compose up --build
```

- App: http://localhost:3000
- Metrics: http://localhost:3000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

In Grafana:
1. Add Prometheus as a data source: URL `http://prometheus:9090`
2. Import the starter dashboard (or create your own)
3. View the metrics

The pain of "is the app working?" is solved. We can see what's happening.

---

## Experiments

### Experiment 1: Add an error counter

```js
const httpRequestErrorsTotal = new promClient.Counter({
  name: 'http_request_errors_total',
  help: 'Total number of HTTP errors',
  labelNames: ['method', 'route', 'status'],
});

// In the error handler
httpRequestErrorsTotal.labels(req.method, req.route?.path || req.path, err.status || 500).inc();
```

### Experiment 2: Add a custom business metric

```js
const signupsTotal = new promClient.Counter({
  name: 'signups_total',
  help: 'Total number of signups',
});

// In the signup handler
signupsTotal.inc();
```

### Experiment 3: Set up an alert

In Prometheus:

```yaml
groups:
  - name: 'myapp'
    rules:
      - alert: 'HighErrorRate'
        expr: 'sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05'
        for: 5m
        annotations:
          summary: 'High error rate detected'
```

Alert when error rate > 5% for 5 minutes.

### Experiment 4: Add traces with OpenTelemetry

```bash
npm install @opentelemetry/api @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node
```

```js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const sdk = new NodeSDK({ /* config */ });
sdk.start();
```

Auto-instrumentation: traces every HTTP request, every database query, etc. Out of scope for this project but a good next step.

### Experiment 5: Add log aggregation with Loki

```bash
# Add Loki to docker-compose
```

Use Loki to aggregate logs. Grafana queries both Prometheus (metrics) and Loki (logs). You can correlate metrics spikes with log events.

---

## Summary

You now have observability. The app exposes metrics. Prometheus scrapes. Grafana visualizes. You can see what's happening in production.

This is the foundation of *observability*. From here, every project that needs to see what's happening in production can use these tools. The patterns (RED method, prom-client, Prometheus, Grafana) are universal.

In project 40, we will add **microservices**. We will split the monolith into independent services (auth, posts, presence, etc.) that communicate via HTTP/gRPC and a message broker.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

# The Thought

> *"If you can't measure it, you can't improve it. If you can't improve it, you can't scale it."*

## The RED Method

The standard set of metrics for a web service is **RED**:

- **Rate**: requests per second
- **Errors**: error rate (4xx, 5xx)
- **Duration**: latency (p50, p95, p99)

We expose these for every endpoint. We can answer:

- Is the request rate normal?
- Is the error rate increasing?
- Is the latency increasing?

## Prometheus

Prometheus is a *metrics* database. It *scrapes* metrics from your app at a regular interval (e.g., every 15 seconds). It stores them in a time-series database. You can query them with PromQL.

Your app exposes a `/metrics` endpoint that returns metrics in the Prometheus text format:

```
# HELP http_request_duration_seconds Duration of HTTP requests in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.001"} 0
http_request_duration_seconds_bucket{le="0.01"} 5
http_request_duration_seconds_bucket{le="0.1"} 100
http_request_duration_seconds_bucket{le="1"} 110
http_request_duration_seconds_bucket{le="+Inf"} 115
http_request_duration_seconds_count 115
http_request_duration_seconds_sum 12.345
```

This is human-readable but designed to be scraped by Prometheus.

## prom-client

`prom-client` is the standard Node.js client for Prometheus. It provides:

- Default metrics (CPU, memory, event loop lag, etc.)
- Custom metrics (Counter, Gauge, Histogram, Summary)
- The `/metrics` endpoint

We add it to our app:

```js
const promClient = require('prom-client');

const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });
```

The default metrics include process CPU, memory, file descriptors, event loop lag, etc. Useful for monitoring the Node.js process.

## Custom Metrics

We add custom metrics for the HTTP requests:

```js
const httpRequestDurationSeconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.001, 0.01, 0.1, 1, 10],
});
register.registerMetric(httpRequestDurationSeconds);
```

A Histogram is a metric that counts observations in buckets. For latency, we have buckets at 1ms, 10ms, 100ms, 1s, 10s. We can compute percentiles (p50, p95, p99) from the histogram.

## The Middleware

We add a middleware to track request duration:

```js
app.use((req, res, next) => {
  const start = process.hrtime.bigint();
  res.on('finish', () => {
    const duration = Number(process.hrtime.bigint() - start) / 1e9;
    httpRequestDurationSeconds.labels(req.method, req.route?.path || req.path, res.statusCode).observe(duration);
  });
  next();
});
```

When a request finishes (response sent), we observe the duration. The labels (method, route, status) let us filter by endpoint and status code.

## The /metrics Endpoint

```js
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

Prometheus scrapes this endpoint every 15 seconds. The response is the metrics in the Prometheus text format.

## Grafana

Grafana is a dashboard tool. It connects to Prometheus (and many other data sources) and visualizes the metrics.

We set up Grafana via docker-compose. It comes with a default Prometheus data source. We provide a starter dashboard (JSON) that shows:

- Request rate (per endpoint)
- Error rate (per endpoint)
- Latency (p50, p95, p99)
- Node.js process metrics (CPU, memory)

## docker-compose.yml

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    # ...

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

`prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['app:3000']
```

Prometheus scrapes `app:3000/metrics` every 15 seconds. Grafana connects to Prometheus and visualizes.

## Common Confusions (read these)

**Confusion 1: "Why Prometheus and not a hosted solution?"**
Prometheus is self-hosted. Free. The standard. Hosted solutions (Datadog, New Relic) are easier but cost money.

**Confusion 2: "Why not just use logs?"**
Logs are events. Metrics are aggregations. For trends, you need metrics. For events, you need logs.

**Confusion 3: "What about traces?"**
Traces are for distributed systems (multiple services). For a single service, metrics are enough. We don't add traces.

**Confusion 4: "What's the difference between Counter, Gauge, Histogram, Summary?"**
- **Counter**: monotonically increasing value (request count)
- **Gauge**: can go up or down (memory usage)
- **Histogram**: counts observations in buckets (latency)
- **Summary**: similar to Histogram but computes quantiles client-side

We use Counter and Histogram. Summary is less common.

**Confusion 5: "What about cardinality?"**
Labels create unique time series. Don't use unbounded values as labels (e.g., user IDs). Use bounded values (method, route, status).

**Confusion 6: "What about histograms and percentiles?"**
Prometheus computes percentiles from histograms. `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` gives the p99.

**Confusion 7: "What about alerting?"**
We set up an alert for high error rate. Out of scope for more complex alerts.

**Confusion 8: "What about logs and metrics together?"**
Use a correlation ID. The metric has a label for the correlation ID. The log has the same. You can find the log from the metric and vice versa.

## What We Are About to Build

A ~900-line Express app + Prometheus + Grafana + starter dashboard. The app exposes `/metrics`. Prometheus scrapes. Grafana visualizes. We can see what's happening.

The HTTP handlers are extended. The new piece is the metrics.

In [BUILD.md](./BUILD.md) we will go line by line.

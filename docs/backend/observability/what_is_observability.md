## Why it exists (THE PROBLEM)

Your app is in production. Users report "the site is slow." You check your logs. Nothing. You check the database CPU. Normal. You have no idea what's slow. Was it the auth middleware? The database query? The third-party API call? You can't fix what you can't see.

**Observability** = the ability to ask arbitrary questions about your system's state from its outputs. Three pillars:
1. **Logs** — what happened (events, errors, state changes)
2. **Metrics** — numeric measurements over time (request rate, latency, error rate)
3. **Traces** — a single request's path through the system (which services, which queries, how long)

With observability, you see: "the /search endpoint has p99 latency 2.3 seconds because the OpenAI API call is taking 2 seconds." Without it, you guess.

## Definition (very simple)

**Logs**: Discrete events. Structured (JSON) or unstructured (text). `logger.info("user signed up", { userId: 42, email: "..." })`. Each log line is a point in time.

**Metrics**: Aggregated numeric data over time. Counters (only increase: `http_requests_total = 5000`), gauges (can go up/down: `cpu_percent = 73`), histograms (distribution: `http_request_duration_ms`).

**Traces**: A request's journey across services. Each service adds a "span" with start/end time and tags. Traces show which service is slow. Trace ID propagated via `X-Trace-Id` header.

## Real-life analogy

**Without observability = driving blindfolded.** You know you're moving but you don't know how fast, where, or if you're about to crash.

**With observability = full dashboard.** Speedometer, RPM, fuel, GPS, engine temperature, oil pressure. Every metric the car reports. You see the problem before it becomes a breakdown.

**Logs = event log on your phone.** "App was opened at 2:14 PM." "Crash at 3:47 PM, error: out of memory."

**Metrics = aggregate stats on your phone.** "App opened 47 times today. Average session: 12 minutes. Crashes: 2."

**Traces = call detail record.** "When you opened the app, here's the path: 0.1s in splash, 0.3s in auth, 0.2s in main API, 0.1s in image load, total 0.7s." Each step is a span.

## Tiny numeric example

Without observability:
```
User: "site is slow"
You:  "What page? When? What did you do?"
User: "I don't know, just slow"
You:  *checks server* "Everything looks fine"
User: "still slow"
You:  *more checking* "still fine"  
[User leaves, you never know what was slow]
```

With observability:
```
[Dashboard shows] p99 latency: 2.3s
[Trace shows] /search → call to third-party API (1.8s) → 400 error
[Logs show] "OpenAI rate limit exceeded" 47 times in last hour
[Action] implement request batching, add retry, problem solved
```

## Common confusion (5+ bullet points)

1. **"Print statements are logging."** Sort of. But `console.log("done")` is unstructured. You can't search it, can't graph it, can't alert on it. Structured logging: `logger.info("user_login", { userId: 42, durationMs: 87, ip: "1.2.3.4" })`. Now you can search for slow logins, alert on failed logins, graph login rate.

2. **"Metrics are for monitoring servers."** Metrics are for monitoring PRODUCTS. How many users signed up today? What's the conversion rate? What's the median time to first purchase? These are product metrics, not just server metrics.

3. **"Tracing is too complex for small apps."** OpenTelemetry has a "no-op" exporter that does nothing but lets you add spans. If you never need to debug, the cost is near zero. The day you DO need it, you have traces. The cost of NOT having it is hours of debugging.

4. **"I have one log file. That's enough."** Single log file is OK at 100 MB. At 10 GB, you can't grep it. At 100 GB, your disk fills up and your service crashes. Use log rotation (daily files) and aggregation (Datadog, ELK, Loki).

5. **"Alert on every error."** You'll get 1000 alerts per minute. Alert fatigue. Alert on: error rate > 1%, p99 latency > 1s, queue depth > 100. The metric, the threshold, the runbook.

## Key properties

| Pillar | Format | Tool | Use |
|---|---|---|---|
| **Logs** | JSON lines, structured | Winston, Pino, Bunyan | Events, errors, audit |
| **Metrics** | Prometheus format, time series | prom-client, StatsD | Dashboards, alerts |
| **Traces** | OpenTelemetry spans | OTel SDK, Jaeger, Zipkin | Latency diagnosis |

## The RED method (rate, errors, duration)

The minimal useful dashboard:
- **Rate**: requests per second (current, vs last week)
- **Errors**: error rate (% of 5xx responses)
- **Duration**: p50, p95, p99 latency

Three metrics. That's the minimum. Add: saturation (CPU, memory, queue depth) for capacity planning.

## Connection to our projects

Many of our 73 projects should have a `/metrics` endpoint, structured logs, and X-Trace-Id header propagation. The observability service we built (in apps/level2) is the simplest possible implementation. For real production, replace in-memory storage with Prometheus + Grafana.

For CortexCode and logogen, the SAME pattern applies: track request count, latency, error rate. Add `X-Trace-Id` to your API calls. Use a logging library like Winston instead of `console.log`.

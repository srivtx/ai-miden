# Observability Demo — Logs + Metrics + Traces with SQLite

A complete observability service using SQLite as the storage backend. In production, replace SQLite with Prometheus + ELK + Jaeger.

## Run
```
node server.js
```

## Endpoints
```
GET /health
GET /api/users
GET /api/slow          (2s delay)
GET /api/error         (500 response)

GET /logs?level=error&trace=abc&since=2024-01-01&limit=50
GET /metrics            (Prometheus format)
GET /traces/:traceId   (all spans for a trace)
```

## What this teaches
1. Structured logging (JSON, with trace ID)
2. Metrics: counter, gauge, histogram (Prometheus format)
3. Distributed tracing: trace ID, span ID, parent span
4. Correlation: logs and metrics linked by trace ID
5. RED method: Rate, Errors, Duration
6. SQLite as a multi-purpose time-series store

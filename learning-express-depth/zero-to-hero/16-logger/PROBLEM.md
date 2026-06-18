# The Problem

> *"Console.log is a string. Production needs JSON. Strings can't be searched, filtered, or aggregated."*

## Why Console.log Is Not Enough

In projects 01-15, our logging is `console.log(...)` and `console.error(...)`. The output is unstructured text:

```
Server listening on http://localhost:3000
POST /signup 200 12ms
POST /signup 400 3ms
Error: username already taken
    at ...
```

This is fine for development. In production, we have problems:

1. **Can't search** — "show me all 500 errors from yesterday" requires regex on free text.
2. **Can't filter** — "show me requests from user 42" requires parsing the log line.
3. **Can't aggregate** — "how many requests per minute?" requires counting log lines.
4. **Can't alert** — "tell me when error rate exceeds 5%" requires parsing the log.
5. **No structure** — the log line is a free-form string. Different parts of the code log different formats.

## What Pain Is This Solving?

Imagine the alternative. You have 10 million log lines in production. A customer says "I got an error at 3pm." You need to find that error. With `console.log`:

1. Grep for "3pm" or "15:00" — false positives everywhere
2. Grep for the user's request — they don't know the exact time
3. Manually read thousands of lines

With structured logs:

1. Filter: `level >= 50` (errors)
2. Filter: `time >= "2024-01-15T15:00:00"` and `time < "2024-01-15T16:00:00"`
3. Find the user's request_id in their client-side error reporting
4. Look up the request by ID

Structured logs make debugging at scale possible.

## The Deeper Problem: Logs Are Data

In the modern era, logs are not strings. They are *data*. Each log line is an object with fields. The fields are consistent. The values are typed. The data can be queried, filtered, aggregated, alerted on.

The standard format is JSON Lines (JSONL). Each line is a valid JSON object. Tools like Datadog, ELK, Splunk, Loki, CloudWatch Logs all understand JSONL.

```json
{"level":30,"time":1700000000000,"msg":"request completed","req":{"method":"GET","url":"/"},"res":{"statusCode":200},"responseTime":12}
```

vs.

```
[2024-01-15 15:00:00] request completed GET / 200 12ms
```

The JSON line is structured. The string is not.

## What This Project Will Solve

This project will:

1. Add `pino` for structured JSON logging
2. Add `pino-http` for automatic request logging
3. Generate a unique request ID for each request
4. Log every request with method, URL, status, duration, request ID
5. Log every error with stack trace and request context
6. Pretty-print logs in development (`pino-pretty`)

By the end, every event in the server is logged as a JSON line. We can search, filter, aggregate, and alert.

## What This Project Will *Not* Solve

- **Log shipping** — we log to stdout. In production, we'd ship to a log aggregator (Datadog, etc.). That's infrastructure.
- **Distributed tracing** — out of scope. Project 39 (Observability).
- **Metrics** — out of scope. Project 39.
- **Alerting** — out of scope. The aggregator handles alerts.
- **Log retention** — out of scope. The aggregator handles retention.
- **Sensitive data in logs** — we don't log passwords or tokens, but we should be careful. Out of scope.

## The Question This Project Answers

> *"How do I see what's happening in production?"*

If you can answer: "structured JSON logs, request IDs, automatic request logging, error logging with context," you are ready for project 17.

# The Decisions

> *"Logs are data. Data is JSON. JSON is queryable. Queryable is debuggable."*

## Decision 1: Pino and not winston / bunyan

**Alternatives**:
- **winston** — older, mature, very flexible (formats, transports), but slower
- **bunyan** — JSON-first (pino's predecessor), still maintained but less popular
- **consola** — Vue/Nuxt's logger
- **roarr** — structured logger with a unique syntax

**Why pino**: Fastest JSON logger for Node. JSON by default. Small API. Pino-http for request logging. The de-facto standard in 2024-2026.

**Trade-off**: Less flexible than winston (no built-in file rotation, no custom formats). We don't need those — infrastructure handles them.

## Decision 2: JSON in production, pretty in development

```js
transport: process.env.NODE_ENV === 'production' ? undefined : { target: 'pino-pretty' }
```

**Alternative**: Always JSON. Always pretty.

**Why conditional**: Humans need pretty for development. Aggregators need JSON for production. We switch based on `NODE_ENV`.

**Trade-off**: Two formats. We have to remember to set `NODE_ENV=production` in production. Standard practice.

## Decision 3: stdout, not files

We log to stdout. We don't write to files.

**Why stdout**: The process manager (systemd, Docker, Kubernetes) captures stdout. In production, we let the process manager handle file rotation and shipping.

**Trade-off**: In dev, we lose logs when the terminal scrolls. We can redirect to a file: `node server.js > app.log`. In production, we let the infrastructure handle it.

## Decision 4: `pino-http` for request logging

**Alternative**: Hand-write a request logger middleware.

**Why pino-http: It's the standard. It handles the details (request ID, start time, end time, status). It integrates with pino. We use it.

**Trade-off**: One more dependency. We accept it for the time saved.

## Decision 5: Auto-generated request IDs

`pino-http` generates request IDs with `crypto.randomUUID()`. We could use a different scheme (e.g., `nanoid`), but UUID is fine.

**Why auto-generated**: We don't want to require the client to send an ID. We want every request to have one. Auto-generation is the default.

**Trade-off**: We could read a request ID from a header (`X-Request-ID`). Some clients send one. We don't propagate it in this project. We could add it.

## Decision 6: Log warnings for recoverable issues

`req.log.warn(...)` for things like "username already taken" — the user can fix it. The system isn't broken.

`req.log.info(...)` for important events — "user created", "post published".

`req.log.error(...)` for things that shouldn't happen — unexpected exceptions, database errors.

**Why distinguish**: Logs are queryable. We can filter by level. Warnings are interesting but not critical. Errors need attention. Info is for understanding traffic.

**Trade-off**: We're making a judgment call. Some teams log everything at info level. We use the standard levels.

## Decision 7: Don't log sensitive data

We log `username` and `userId`. We don't log `password` (even the hash), `email` (sometimes), or `token`. We avoid logging the full `req.body` because it might contain sensitive fields.

**Why not: Logs are often shared with third parties (Datadog, Sentry, etc.). Sensitive data in logs is a leak. We minimize what we log.

**Trade-off**: Sometimes you want to log the body for debugging. You can do it explicitly in a specific handler, but not by default.

## Decision 8: Logs go through `req.log` (child logger)

`req.log` is a child of `logger` with the request ID bound. Every log line in a handler includes the request ID.

**Why: We can search for "all logs for request X" and see everything that happened. Without request IDs, we'd have to correlate by time, which is unreliable.

**Trade-off**: Slight overhead. Negligible.

## Decision 9: No log levels in the error wall

The error wall logs at `error` level. We could differentiate: 4xx as `warn`, 5xx as `error`. We don't, for simplicity. We can add later.

**Trade-off**: All errors are at the same level. We can filter by status if we want.

## Decision 10: No PII redaction

We log `username` and `userId`. We don't log `email` (which could be PII). We don't have automatic redaction of sensitive fields.

**Why not: PII redaction is a config decision. We can add it (e.g., `pino` has a `redact` option for paths like `req.body.password`). Out of scope for this project.

**Trade-off**: If we add `email` to logs, it could be a privacy issue. We avoid it for now.

---

## What We Did Not Decide

- **Log shipping** — out of scope (infrastructure)
- **Distributed tracing** — out of scope (project 39)
- **Metrics** — out of scope (project 39)
- **Alerting** — out of scope (infrastructure)
- **Log retention** — out of scope (infrastructure)
- **Sensitive data redaction** — out of scope
- **Custom log formats** — out of scope
- **Log sampling** — out of scope (for high-volume services, you sample logs)

Each is a future decision.

---

## The Meta-Decision: The Server Is Observable

For 15 projects, our server was a black box. We could see what we logged with `console.log`. We couldn't search, filter, or aggregate. We had no request IDs, no durations, no structured context.

Now the server is *observable*. Every request is logged. Every error is logged with context. Request IDs tie everything together. The logs are JSON, queryable, aggregatable.

This is the foundation of *production-ready services*. Every real service has structured logging. The patterns (pino, pino-http, request IDs, child loggers) are universal.

The next 24 projects will assume structured logging exists. The path diverges:

- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance
- **File upload** (project 20): accept files
- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The server is observable. The path continues.

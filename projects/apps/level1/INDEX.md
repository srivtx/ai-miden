# Level 1 — Backend Learning Projects (one concept per project)

Each project is small (100-300 lines), focused on one concept, and runnable with `node server.js`. Uses SQLite where applicable (per user preference: easy to start).

## Core concepts

### Request/response
- **routing-demo** — static, dynamic, regex, optional params, nested routers
- **middleware-demo** — custom middleware: timing, counter, blocklist, transform
- **validation-demo** — schema-based validation (no external libs)
- **streams-demo** — file streams, NDJSON, CSV, SSE, upload streams

### Data
- **database-design-demo** — 3NF schema, FKs, indexes, JOIN, GROUP BY
- **connection-pooling-demo** — naive vs pooled, async acquire/release
- **indexing-demo** — composite indexes, query plans, EXPLAIN
- **migrations-demo** — versioned up/down, rollback, tracking
- **soft-delete-demo** — `deleted_at` pattern, restore, 410 Gone
- **search-demo** — inverted index, TF ranking, snippets

### API patterns
- **api-versioning-demo** — URI/query/header strategies
- **rate-limiting-demo** — token bucket, per-endpoint limits
- **pagination-demo** — offset vs cursor, benchmark
- **idempotency-demo** — safe retries with `Idempotency-Key`
- **error-handling-demo** — typed errors, request IDs, global handler
- **api-client-demo** — retry, timeout, circuit breaker
- **rpc-demo** — gRPC-style service definitions over HTTP
- **graphql-demo** — schema, resolvers, queries, mutations
- **openapi-demo** — spec-first design with auto-docs
- **api-gateway-demo** — single entry point, routing, aggregation

### Auth/security
- **jwt-demo** — issue, sign, verify, decode, refresh (no `jsonwebtoken`)
- **security-patterns-demo** — SQL injection, XSS, path traversal, hashing
- **security-basics** — auth, secrets, OWASP
- **csrf-app** — CSRF tokens, SameSite cookies

### Async/realtime
- **websocket-demo** — chat with rooms (uses `ws`)
- **pubsub-demo** — event bus, topics, retry, DLQ, wildcards
- **background-jobs-demo** — in-process queue with progress tracking
- **email-demo** — templates, queue, send tracking
- **cron-demo** — 5-field cron parser, scheduler
- **file-upload-demo** — multipart parsing (no multer)

### State
- **caching-demo** — cache-aside, TTL, in-memory
- **multi-tenant-demo** — row-level isolation with `X-Tenant-Id`
- **feature-flags-demo** — rollout %, A/B variants, kill switch
- **audit-log-demo** — append-only with before/after state
- **health-check-demo** — liveness, readiness, dependencies

### Operations
- **observability-demo** — logs, metrics, traces in SQLite
- **logging** — structured JSON, request-scoped
- **docker-demo** — multi-stage Dockerfile + compose
- **ci-cd-demo** — GitHub Actions workflow
- **graceful-shutdown-demo** — SIGTERM, drain in-flight
- **service-discovery-demo** — registry, heartbeats, TTL

### Money
- **payment-service** (level2) — Stripe-like API
- **subscription-billing** (level2) — recurring payments

### Misc
- **config-demo** — env vars, .env files, feature flags
- **i18n-demo** — multi-language, locale detection
- **testing-demo** — testable endpoints + mini runner

## How to use
1. Pick a concept you want to learn
2. Read the README
3. Run `node server.js`
4. Try the `curl` examples
5. Read the code (it's < 300 lines)
6. Modify it to test your understanding

## Total: 63 level1 projects

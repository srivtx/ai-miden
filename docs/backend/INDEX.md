# Backend Curriculum — ai-miden format

A complete backend engineering curriculum. Each topic has a `what_is_X.md` doc in the ai-miden format (Problem → Definition → Analogy → Numeric → Confusions → Properties → Connection), plus a working project in `projects/apps/level1/`.

## Topics

### Fundamentals
- [01. Express Basics](../express_basics/) — what is Express, routes, middleware, request/response
- [02. Error Handling](error_handling/) — status codes, typed errors, global handler, request IDs
- [03. Logging](logging/) — structured logs, levels, request-scoped, PII

### Data
- [04. Database Design](database_design/) — 3NF, FKs, indexes, denormalization
- [05. Connection Pooling](connection_pooling/) — pool patterns, leaks, pgbouncer
- [06. Caching](caching/) — Redis, in-memory, cache-aside
- [07. Indexing](indexing/) — composite indexes, query plans

### Architecture
- [08. API Versioning](versioning/) — URI/query/header, deprecation
- [09. Rate Limiting](rate_limiting/) — token bucket, fixed window, sliding log
- [10. Idempotency](idempotency/) — Idempotency-Key, retries
- [11. Pagination](pagination/) — offset vs cursor
- [12. Observability](observability/) — logs + metrics + traces, RED method

### Operations
- [13. Docker](docker/) — images, containers, multi-stage builds, compose
- [14. CI/CD](ci_cd/) — pipelines, blue-green, matrix testing
- [15. Webhooks](webhooks/) — delivery, HMAC signatures, retry
- [16. Security Patterns](security_patterns/) — auth, secrets, OWASP
- [17. GraphQL](../graphql/) — schemas, resolvers, N+1
- [18. WebRTC](../webrtc/) — peer-to-peer, signaling
- [19. Payments](../payments/) — Stripe, idempotency
- [20. Email](../email/) — SES, templates
- [21. Microservices](../microservices/) — service boundaries, communication
- [22. Message Queues](../message_queues/) — pub/sub, RabbitMQ, Kafka
- [23. Testing Patterns](../testing_patterns/) — unit, integration, e2e

## Format
Each topic doc follows the ai-miden chapter format:
1. **Why it exists (THE PROBLEM)**: real-world motivation
2. **Definition (very simple)**: 1-2 sentence summary
3. **Real-life analogy**: accessible comparison
4. **Tiny numeric example**: code or numbers
5. **Common confusion (5+ bullet points)**: pitfalls and myths
6. **Key properties**: comparison tables
7. **Connection to our projects**: links to 73-app library

## Companion projects
Each topic has a working project in `projects/apps/level1/`. Run them with `node server.js`. They use SQLite for simplicity (per user preference: "with database as sqlite coz its easy to start").

## Status: 23/40+ topics written. Continuously expanding.

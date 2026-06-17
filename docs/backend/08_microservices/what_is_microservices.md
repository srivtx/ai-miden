## Why it exists (THE PROBLEM)

One Express server handles everything: auth, users, products, payments, email, file upload. The server is 2000 lines. If you change the payment logic, you redeploy the entire server. If the file upload crashes (OOM on a 2GB file), the entire server restarts — including auth and payments. A single-purpose failure cascades into a total outage.

**Microservices** split the monolith into independent services. Each service: one responsibility, one database, one deployment. Auth service crashes → users service is unaffected. Payment service needs more CPU → scale only that service. Deploy email service → no impact on API.

The cost: service-to-service communication (HTTP, gRPC, message queue), data consistency (no more ACID across services — eventual consistency), and operational complexity (10 services = 10 deployments, 10 health checks, 10 log streams).

## Definition (very simple)

**Microservices** = independent deployable units, each owning one business capability. They communicate via:
- **HTTP/REST** — simple, universal, but synchronous (blocking)
- **Message Queue** — async, decoupled, but eventual consistency
- **gRPC** — binary, fast, typed, but harder to debug

**Key patterns:**
- **API Gateway:** single entry point that routes to services
- **Service Discovery:** services register themselves (Consul, etcd, K8s DNS)
- **Circuit Breaker:** stop calling a dead service, return cached/fallback
- **Saga:** distributed transaction (compensating actions for rollback)

## Monolith vs Microservices

| | Monolith | Microservices |
|---|---|---|
| Deploy | One artifact | N artifacts (complex) |
| Scale | Entire app | Per service (efficient) |
| Failure blast radius | Entire app | One service |
| Data consistency | ACID (easy) | Eventual (hard) |
| Development speed | Slows over time | Teams work independently |
| Debugging | One log stream | Distributed tracing needed |
| When to use | < 5 developers, < 10K users | > 10 developers, > 100K users |

## The truth about microservices

You don't need them at the start. A well-structured monolith (separate modules, clean interfaces) works for 95% of projects. Microservices solve ORGANIZATIONAL scaling (50+ engineers), not TECHNICAL scaling. Start with a monolith. Split into services when you have: (a) 10+ developers, (b) a clear domain boundary that changes independently, (c) a team that owns that boundary end-to-end.

## Connection to our projects

All 20 apps we built are monoliths. They're well-structured (separate routes, middleware, validation) but deployed as one. The next step: take the e-commerce app and split payments into its own service. The `server.js` calls `POST http://payment-service/internal/charge` instead of running Stripe logic inline. The payment service has its own database, its own deployment, its own scaling.

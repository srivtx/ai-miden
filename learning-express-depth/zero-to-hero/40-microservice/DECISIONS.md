# The Decisions

> *"The final project. The path is complete."*

## Decision 1: Microservices and not a modular monolith

**Alternative**: Modular monolith (one process, well-defined modules).

**Why microservices: Independent scaling. Independent deploys. Team scaling. Tech flexibility. The monolith is too large to maintain as one codebase.

**Trade-off**: Operational complexity. Network latency. Distributed systems challenges. We accept this.

## Decision 2: 8 services (by bounded context)

**Alternative**: 2-3 services (auth, posts, everything else).

**Why 8: Each service has a clear bounded context. Auth, users, posts, presence, collab, voice, payment, notifications. Each can be scaled independently.

**Trade-off**: More services to manage. We accept this.

## Decision 3: API gateway

**Alternative**: Direct service-to-service (no gateway).

**Why gateway: Single entry point. Authentication. Rate limiting. Logging. Routing. Standard pattern.

**Trade-off**: Another service to manage. We accept this.

## Decision 4: HTTP for sync, message broker for async

**Alternative**: All HTTP. Or all message broker.

**Why mixed: HTTP for sync (request/response). Message broker for async (events). The right tool for the right job.

**Trade-off**: Two patterns to manage. We accept this.

## Decision 5: Redis pub/sub for the message broker

**Alternative**: RabbitMQ, Kafka, AWS SNS/SQS.

**Why Redis: We already have it. Simple. For our scale, enough. Pub/sub for events.

**Trade-off**: For high throughput, use Kafka. We accept this.

## Decision 6: One database per service

**Alternative**: Shared database.

**Why separate: Each service has its own data. No coupling. No cross-service joins. Each can use the right DB (Postgres, MongoDB, etc.).

**Trade-off**: Data consistency across services is hard (no transactions). Use the saga pattern. We accept this.

## Decision 7: Saga pattern for cross-service workflows

**Alternative**: Two-phase commit (2PC), distributed transactions.

**Why saga: No distributed transactions in modern systems. Saga is the standard: chain of events that eventually reach a consistent state.

**Trade-off**: Eventual consistency. We accept this.

## Decision 8: Distributed tracing with OpenTelemetry

**Alternative**: Custom tracing, no tracing.

**Why OpenTelemetry: Standard. Auto-instrumentation. Integrates with Jaeger, Zipkin, etc.

**Trade-off**: We depend on OpenTelemetry. We accept this.

## Decision 9: Service mesh out of scope

**Alternative**: Istio, Linkerd.

**Why out of scope: Adds complexity. We don't need it for our scale. We can add it later.

**Trade-off**: No automatic retries, no traffic shifting, no mTLS. We accept this.

## Decision 10: gRPC out of scope

**Alternative**: gRPC for service-to-service.

**Why out of scope: We use HTTP/JSON. Simpler. gRPC is faster but more complex.

**Trade-off**: Slower internal communication. We accept this.

---

## What We Did Not Decide

- **Service mesh (Istio, Linkerd)** — out of scope
- **Distributed transactions (2PC, sagas in detail)** — out of scope
- **Event sourcing** — out of scope
- **CQRS** — out of scope
- **Kubernetes operators** — out of scope
- **gRPC** — out of scope
- **API versioning** — out of scope
- **Service mesh observability** — out of scope
- **Chaos engineering** — out of scope
- **Multi-region** — out of scope

Each is a future decision.

---

## The Meta-Decision: The App Is Distributed

For 39 projects, the app was a monolith. One process. One codebase. One deploy.

Now the app is distributed. 8 services. 8 databases. An API gateway. Service-to-service communication. Distributed tracing. The path is **complete**.

This is the foundation of *distributed systems*. From here, every project that needs to scale individual components can use microservices. The patterns (bounded context, API gateway, service-to-service communication, saga, distributed tracing) are universal.

## The End of the Path

The 40-project zero-to-hero backend path is **complete**. You have built:

- **Phase 1**: HTTP substrate (6 projects)
- **Phase 2**: Identity & Persistence (6 projects)
- **Phase 3**: Robustness & Quality (6 projects)
- **Phase 4**: Real-World Operations (9 projects)
- **Phase 5**: Real-Time (5 projects)
- **Phase 6**: Production (8 projects)

You have built a real-time, role-based, tested, deployed, observed, distributed system. The complete backend for the final artifact (Cove, the Slack × Notion × Figma-lite hybrid).

The path is complete. The final artifact is ready. You can now build the frontend, deploy to production, and serve users.

Or you can extend the path: more services, more features, more scale. The foundation is solid. The patterns are universal. The possibilities are endless.

**Congratulations on completing the zero-to-hero backend path.**

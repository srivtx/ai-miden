# The Thought

> *"The final project. The path is complete."*

## Bounded Contexts

A *bounded context* is a part of the system that has its own domain model and data. We split the monolith by bounded context:

| Service | Responsibility | Data |
|---------|---------------|------|
| auth-service | Signup, login, sessions, password reset | users (auth fields), sessions |
| user-service | Profiles, RBAC, workspaces | users (profile), workspaces, members |
| post-service | Posts, comments | posts, comments |
| presence-service | Who's online | Redis (TTL) |
| collab-service | Co-editing | Yjs documents |
| voice-service | Voice channels | WebRTC signaling |
| payment-service | Stripe | subscriptions |
| notification-service | Email, webhooks | email logs, webhook logs |

Each service has its own database. They communicate via HTTP (sync) and a message broker (async).

## Service Communication

There are two types of communication:

### Synchronous (HTTP)

For requests that need a response:

- `user-service` calls `auth-service` to verify a token
- `post-service` calls `user-service` to get the author's profile
- `api-gateway` calls `user-service` to get the user

We use HTTP (REST or gRPC) for sync. The caller waits for a response.

### Asynchronous (Message Broker)

For events that don't need an immediate response:

- `post-service` publishes `post.created` → `notification-service` sends an email
- `payment-service` publishes `subscription.updated` → `user-service` updates the user's role
- `presence-service` publishes `user.online` → `notification-service` shows "Alice is online"

We use Redis pub/sub (project 23) or RabbitMQ for async. The publisher doesn't wait for a response.

## The API Gateway

The API gateway is the only entry point. External clients talk to the gateway. The gateway routes to the appropriate service.

```
Client → API Gateway → auth-service
                  → user-service
                  → post-service
                  → ...
```

The gateway:
- Routes requests
- Authenticates (verify the JWT)
- Rate limits
- Logs

We use `http-proxy-middleware` for routing. The gateway is a thin layer.

## The Saga Pattern

For workflows that span multiple services (e.g., "user upgrades to premium"), we use the **saga pattern**:

1. `payment-service` creates a Stripe session
2. Stripe sends a webhook to `payment-service`
3. `payment-service` publishes `subscription.activated` to Redis
4. `user-service` consumes the event, updates the user's role
5. `notification-service` consumes the event, sends a welcome email

If step 4 fails, we retry. If it keeps failing, we publish `subscription.activation_failed` and roll back. The saga is a chain of events that eventually reach a consistent state.

## Distributed Tracing

For a request that spans multiple services, we use **distributed tracing**. Each request has a `trace-id` that propagates through all services. We can see the full path.

We use OpenTelemetry. The `trace-id` is in the request headers. Each service adds its span. We can see the full request path in a tracing UI (Jaeger, Zipkin).

## Common Confusions (read these)

**Confusion 1: "Why microservices and not a modular monolith?"**
A modular monolith has well-defined modules but is still one process. Easier to develop, deploy, debug. Microservices add operational complexity. Use microservices when the monolith is too large or when you need independent scaling.

**Confusion 2: "How do services share data?"**
They don't share a database. Each service has its own. If user-service needs the user's email, it calls auth-service. Or it duplicates the data (eventual consistency).

**Confusion 3: "How do services authenticate?"**
The API gateway verifies the JWT. Internal services use a service-to-service token (e.g., mTLS, JWT with a different secret).

**Confusion 4: "What about transactions?"**
No distributed transactions. Use the saga pattern. Each service has its own transaction. The saga coordinates.

**Confusion 5: "What about failures?"**
Each service is independent. If one fails, the others can continue. Use circuit breakers (e.g., `opossum`) to prevent cascading failures.

**Confusion 6: "What about service discovery?"**
In Kubernetes, services register themselves. In Docker Compose, services are named (e.g., `auth-service`). We use the latter for simplicity.

**Confusion 7: "What about versioning?"**
Each service has its own version. The API gateway routes to the appropriate version. For breaking changes, use API versioning (e.g., `/v1/users`, `/v2/users`).

**Confusion 8: "What about monitoring?"**
We have observability (project 39). Each service exposes its own metrics. The API gateway aggregates. Grafana shows the full picture.

## What We Are About to Build

A ~1000-line setup + 8 services + 1 API gateway + 1 shared library. The monolith is a distributed system. The path is complete.

The HTTP handlers are split across services. The new piece is the architecture.

In [BUILD.md](./BUILD.md) we will go line by line.

## The End of the Path

This is the last project. After this, you have:

- A complete HTTP substrate
- A complete identity and persistence layer
- A complete robustness and quality layer
- A complete real-world operations layer
- A complete real-time layer
- A complete production layer

The path is complete. The final artifact (Cove, the Slack × Notion × Figma-lite hybrid) has a real, production-ready backend.

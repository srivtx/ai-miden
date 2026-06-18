# The Problem

> *"The final project. The path is complete."*

## Why a Monolith Is Painful

In projects 01-39, we have a monolith. One Node.js process. One codebase. One deploy.

As the app grows, this becomes painful:

- **Hard to scale**: we can't scale just the chat; we have to scale the whole app
- **Hard to deploy**: a small change requires redeploying the whole app
- **Hard to maintain**: the codebase is large; changes ripple
- **Hard to use different tech**: the chat needs WebSocket, the docs need CRDT, the analytics need a different stack
- **Hard to team-scale**: many developers working on one codebase = merge conflicts

## What Pain Is This Solving?

**Microservices** solve this. We split the monolith into independent services. Each service:

- Has its own codebase
- Has its own database
- Can be deployed independently
- Can be scaled independently
- Can use a different tech stack

The benefits:

- **Independent scaling**: scale the chat to 1000 instances, the docs to 10
- **Independent deploys**: deploy the chat without redeploying the whole app
- **Team scaling**: each team owns a service
- **Tech flexibility**: use Python for ML, Go for performance, Node for the rest

The costs:

- **Operational complexity**: more services to deploy, monitor, debug
- **Network latency**: services communicate over the network (not in-process)
- **Distributed systems**: you have to handle failures, retries, idempotency, eventual consistency
- **Data consistency**: no transactions across services (use sagas)

## The Deeper Problem: Bounded Contexts

How do you split a monolith? By *bounded context*. A bounded context is a part of the system that has its own domain model and data.

For our app:

- **auth-service**: users, sessions, passwords
- **user-service**: profiles, RBAC, workspaces
- **post-service**: posts, comments
- **presence-service**: who's online
- **collab-service**: co-editing
- **voice-service**: voice channels
- **payment-service**: Stripe
- **notification-service**: email, webhooks

Each service has its own database. They communicate via HTTP and a message broker.

## What This Project Will Solve

This project will:

1. Split the monolith into 8 services
2. Add an API gateway
3. Add service-to-service communication (HTTP and message broker)
4. Add distributed tracing
5. Document the architecture

By the end, the monolith is a distributed system. The path is complete.

## What This Project Will *Not* Solve

- **Service mesh** (Istio, Linkerd) — out of scope.
- **Distributed transactions** (2PC, sagas) — out of scope.
- **Event sourcing** — out of scope.
- **CQRS** — out of scope.
- **Kubernetes operators** — out of scope.

## The Question This Project Answers

> *"How do I split a monolith into independent services?"*

If you can answer: "by bounded context, each service has its own codebase and database, services communicate via HTTP and a message broker, an API gateway routes external requests," then the path is complete. You have built a real-time, role-based, tested, deployed, observed, distributed system.

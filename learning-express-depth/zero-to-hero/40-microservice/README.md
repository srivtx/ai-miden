# Project 40: The Microservice Split

> *"The final project. One monolith becomes many services. The path is complete."*

In projects 01-39, we have a monolith. One Node.js process. One codebase. One deploy. As the app grows, this becomes painful:

- **Hard to scale**: we can't scale just the chat; we have to scale the whole app
- **Hard to deploy**: a small change requires redeploying the whole app
- **Hard to maintain**: the codebase is large; changes ripple
- **Hard to use different tech**: the chat needs WebSocket, the docs need CRDT, the analytics need a different stack

**Microservices** solve this. We split the monolith into independent services. Each service:

- Has its own codebase
- Has its own database
- Can be deployed independently
- Can be scaled independently
- Can use a different tech stack

The services communicate via HTTP/gRPC and a message broker (Redis pub/sub, RabbitMQ, Kafka).

For our app, we split into:

- **auth-service**: signup, login, sessions, password reset
- **user-service**: user profiles, RBAC
- **post-service**: posts, comments
- **presence-service**: who's online (WebSocket, Redis pub/sub)
- **collab-service**: co-editing (Yjs)
- **voice-service**: voice channels (WebRTC signaling)
- **payment-service**: Stripe integration
- **notification-service**: email, webhooks
- **api-gateway**: routes requests to the appropriate service

By the end, the monolith is a distributed system. The path is complete.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is a monolith painful? What is a microservice?
2. [The Thought](./THOUGHT.md) — How do you split a monolith? What is an API gateway?
3. [The Build](./BUILD.md) — Line-by-line construction of the service split
4. [The Decisions](./DECISIONS.md) — Why microservices? Why an API gateway? Why a message broker?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Microservices split a monolith into independent services. Each service has its own codebase, database, and deploy. Services communicate via HTTP (synchronous) and a message broker (asynchronous). An API gateway routes external requests to the appropriate service. We split the monolith into auth, user, post, presence, collab, voice, payment, and notification services.

---

## The Code

### The API Gateway

```js
const http = require('http');
const httpProxy = require('http-proxy-middleware');

const app = express();

app.use('/users', httpProxy({ target: 'http://user-service:3001', changeOrigin: true }));
app.use('/sessions', httpProxy({ target: 'http://auth-service:3002', changeOrigin: true }));
app.use('/posts', httpProxy({ target: 'http://post-service:3003', changeOrigin: true }));
// ...

app.listen(3000);
```

The API gateway is the only entry point. It routes to the appropriate service.

### The Services

Each service is a separate Node.js app. They share a common library (e.g., `common/` with auth middleware, error handling, etc.).

```
services/
  api-gateway/
  auth-service/
  user-service/
  post-service/
  presence-service/
  collab-service/
  voice-service/
  payment-service/
  notification-service/
common/
```

Each service has its own `Dockerfile`, `package.json`, and database.

### The docker-compose.yml

```yaml
version: '3.8'
services:
  api-gateway:
    build: ./services/api-gateway
    ports:
      - "3000:3000"
    depends_on:
      - user-service
      - auth-service
      - post-service
      # ...

  user-service:
    build: ./services/user-service
    environment:
      - DATABASE_URL=postgres://user:pass@user-db:5432/userdb
    depends_on:
      - user-db

  user-db:
    image: postgres:15

  # ... other services
```

The pain of "I can't scale just the chat" is solved. Each service can be deployed and scaled independently.

---

## What You Will Have Learned

- What microservices are (independent services that compose an application)
- How to split a monolith (by bounded context)
- What an API gateway is (routes external requests to internal services)
- How services communicate (HTTP for sync, message broker for async)
- The trade-offs of microservices (complexity, operational overhead)
- When to use microservices (vs. a modular monolith)

These are the foundations of *distributed systems*. From here, every project that needs to scale individual components can use microservices.

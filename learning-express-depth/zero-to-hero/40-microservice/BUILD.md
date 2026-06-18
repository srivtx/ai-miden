# The Build

> *"The final project. The path is complete."*

We are going to split the monolith into microservices. The change from project 39: extract each bounded context into its own service, add an API gateway, add service-to-service communication.

## The Code

### The Directory Structure

```
cove/
  services/
    api-gateway/
      server.js
      Dockerfile
      package.json
    auth-service/
      server.js
      Dockerfile
      package.json
    user-service/
    post-service/
    presence-service/
    collab-service/
    voice-service/
    payment-service/
    notification-service/
  common/
    auth.js (shared auth middleware)
    errors.js (shared error classes)
    logger.js (shared pino logger)
  docker-compose.yml
  prometheus.yml
  grafana-dashboard.json
```

### The Common Library

`common/auth.js`:

```js
const jwt = require('jsonwebtoken');
const SECRET = process.env.JWT_SECRET || 'dev-secret';

function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'missing or invalid authorization header' });
  }
  try {
    req.user = jwt.verify(auth.slice(7), SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: 'invalid or expired token' });
  }
}

module.exports = { authMiddleware, SECRET };
```

Each service uses the same auth middleware. The JWT is verified the same way everywhere.

### The API Gateway

`services/api-gateway/server.js`:

```js
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { authMiddleware } = require('../../common/auth');

const app = express();
app.use(express.json());

// Authenticate all requests
app.use(authMiddleware);

// Route to the appropriate service
app.use('/sessions', createProxyMiddleware({ target: 'http://auth-service:3001', changeOrigin: true }));
app.use('/users', createProxyMiddleware({ target: 'http://user-service:3002', changeOrigin: true }));
app.use('/posts', createProxyMiddleware({ target: 'http://post-service:3003', changeOrigin: true }));
app.use('/webhooks', createProxyMiddleware({ target: 'http://notification-service:3004', changeOrigin: true }));
app.use('/subscriptions', createProxyMiddleware({ target: 'http://payment-service:3005', changeOrigin: true }));
// ... presence, collab, voice

app.listen(3000);
```

The API gateway is the only entry point. It authenticates and routes.

### A Service (e.g., `auth-service`)

`services/auth-service/server.js`:

```js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const knex = require('knex');
const { SECRET } = require('../../common/auth');
// ... error classes, validation, etc.

const db = knex({ client: 'pg', connection: process.env.DATABASE_URL });

const app = express();
app.use(express.json());

// Auth endpoints (signup, login, etc.)
app.post('/users', ...);  // signup
app.post('/sessions', ...);  // login
app.delete('/sessions', ...);  // logout

app.listen(3001);
```

The auth-service has its own database (Postgres). It exposes the same endpoints as the monolith's auth flow.

### The `docker-compose.yml`

```yaml
version: '3.8'
services:
  api-gateway:
    build: ./services/api-gateway
    ports:
      - "3000:3000"
    environment:
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - user-service
      - auth-service
      - post-service
      - payment-service
      - notification-service

  user-service:
    build: ./services/user-service
    environment:
      - DATABASE_URL=postgres://user:pass@user-db:5432/userdb
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - user-db

  user-db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=userdb

  auth-service:
    build: ./services/auth-service
    environment:
      - DATABASE_URL=postgres://auth:pass@auth-db:5432/authdb
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - auth-db

  auth-db:
    image: postgres:15
    environment:
      - POSTGRES_USER=auth
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=authdb

  # ... other services

  redis:
    image: redis:7-alpine
```

Each service has its own database. They communicate via HTTP (through the gateway) and Redis (for events).

## Run It

```bash
docker compose up --build
```

The API gateway is at http://localhost:3000. It routes to the appropriate service.

The pain of "I can't scale just the chat" is solved. Each service can be deployed and scaled independently.

---

## Experiments

### Experiment 1: Add a circuit breaker

```bash
npm install opossum
```

```js
const CircuitBreaker = require('opossum');

const breaker = new CircuitBreaker(callUserService, { timeout: 3000, errorThresholdPercentage: 50 });
breaker.fallback(() => ({ cached: true }));
const user = await breaker.fire(userId);
```

If user-service is down, the circuit breaker returns a fallback (e.g., cached data). Prevents cascading failures.

### Experiment 2: Add distributed tracing

```bash
npm install @opentelemetry/api @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node @opentelemetry/exporter-trace-otlp-http
```

```js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: 'http://jaeger:4318/v1/traces' }),
});
sdk.start();
```

Auto-instrumentation: traces every HTTP request, every database query, every Redis call. Send to Jaeger. Visualize.

### Experiment 3: Deploy to Kubernetes

```bash
# Generate Kubernetes manifests
kompose convert -f docker-compose.yml

# Apply
kubectl apply -f .
```

Docker Compose → Kubernetes. Each service becomes a Deployment. The gateway becomes an Ingress.

### Experiment 4: Use gRPC for service-to-service

```bash
npm install @grpc/grpc-js @grpc/proto-loader
```

gRPC is faster than HTTP/JSON for internal communication. Define a `.proto` file, generate stubs, use them.

### Experiment 5: Add a service mesh (Istio)

```bash
istioctl install
kubectl label namespace default istio-injection=enabled
```

Istio adds observability, security, and traffic management to your services. Without changing your code.

---

## Summary

You now have a microservices architecture. The monolith is split into 8 services. The API gateway is the only entry point. Services communicate via HTTP and Redis. The path is **complete**.

This is the foundation of *distributed systems*. From here, every project that needs to scale individual components can use microservices. The patterns (bounded context, API gateway, service-to-service communication, saga, distributed tracing) are universal.

## The End of the Path

The 40-project path is **complete**. You have built:

- **Phase 1 (HTTP substrate)**: 6 projects — the foundation
- **Phase 2 (Identity & Persistence)**: 6 projects — the auth and data layers
- **Phase 3 (Robustness & Quality)**: 6 projects — validation, errors, logging, REST, pagination, search
- **Phase 4 (Real-World Operations)**: 9 projects — search, upload, email, cache, Redis, rate limit, cron, queue, transactions
- **Phase 5 (Real-Time)**: 5 projects — WebSocket, SSE, presence, CRDT, WebRTC
- **Phase 6 (Production)**: 8 projects — RBAC, webhooks, payments, tests, Docker, CI/CD, observability, microservices

You have built a real-time, role-based, tested, deployed, observed, distributed system. The complete backend for the final artifact (Cove, the Slack × Notion × Figma-lite hybrid).

The path is complete. The final artifact is ready. You can now build the frontend, deploy to production, and serve users.

Or you can extend the path: more services, more features, more scale. The foundation is solid. The patterns are universal. The possibilities are endless.

**Congratulations on completing the zero-to-hero backend path.**

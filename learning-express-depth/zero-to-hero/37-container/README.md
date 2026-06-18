# Project 37: The Container

> *"It works on my machine. But will it work on yours?"*

In projects 01-36, our server runs on our machine. We have Node 20, npm 10, a specific OS, specific system libraries. Deploy to a different machine and... it might not work.

**Docker** solves this. We package the app and all its dependencies into a **container** — a standardized unit that runs anywhere Docker runs. The container includes:

- The OS (Alpine Linux, ~5MB)
- Node.js
- npm packages
- The application code
- Configuration

The container runs the same on our laptop, a CI server, a staging server, and production. No more "it works on my machine."

We add a `Dockerfile` and a `docker-compose.yml`. The Dockerfile builds the image. The compose file orchestrates multiple containers (app, Redis, etc.).

By the end, the app is reproducible. Anyone with Docker can run it. Deploy is a single command.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is "it works on my machine" a problem? What is Docker?
2. [The Thought](./THOUGHT.md) — How do Dockerfiles work? What is a container vs. an image?
3. [The Build](./BUILD.md) — Line-by-line construction of the Dockerfile
4. [The Decisions](./DECISIONS.md) — Why Docker? Why Alpine? Why multi-stage?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Docker packages an app and its dependencies into a container — a standardized unit that runs anywhere. We add a `Dockerfile` (build instructions) and a `docker-compose.yml` (multi-container orchestration). The container includes Node, npm packages, and the app code. Deploy is `docker compose up`.

---

## The Code

### `Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app . .
EXPOSE 3000
CMD ["node", "server.js"]
```

### `docker-compose.yml`

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - REDIS_HOST=redis
      - NODE_ENV=production
    depends_on:
      - redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

The pain of "it works on my machine" is solved. The app runs the same everywhere.

---

## What You Will Have Learned

- What Docker is (containerization)
- How to write a `Dockerfile` (build instructions)
- How to use `docker compose` (multi-container orchestration)
- Multi-stage builds (smaller images)
- The difference between images and containers

These are the foundations of *containerization*. From here, every project that needs reproducible deployments can use Docker.

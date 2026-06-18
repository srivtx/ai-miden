# The Connect

> *"The app is reproducible. Now we need CI/CD, observability, and microservices."*

This project added Docker. The pain of "it works on my machine" is solved. The app is packaged into a container. The container runs the same on any machine. Deploy is `docker compose up`.

The next 3 projects complete Phase 6 (Production):

| # | Project | Pain Answered |
|---|---------|---------------|
| 38 | Pipeline | "I want CI/CD." |
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

After these, the server is a production-ready, real-time, role-based, tested, deployed, observed, distributed system. The complete backend for the final artifact.

## What Works

- `Dockerfile` (multi-stage build)
- `docker-compose.yml` (app + Redis)
- Non-root user
- Volume for SQLite persistence
- Health check
- Restart policy

## What Doesn't Work

### 1. No CI/CD

We can't run tests automatically on every commit.

**The pain**: Pipeline. Project 38.

### 2. No observability

We can't see metrics.

**The pain**: Observability. Project 39.

### 3. No microservices

One big monolith.

**The pain**: Microservices. Project 40.

### 4. No Kubernetes

We use Docker Compose. For production at scale, use Kubernetes.

**The pain**: Kubernetes. Out of scope.

### 5. No Helm charts

We don't use Helm.

**The pain**: Helm. Out of scope.

### 6. No auto-scaling

We don't auto-scale.

**The pain**: Auto-scaling. Out of scope.

### 7. No blue/green deployment

We don't do blue/green.

**The pain**: Blue/green. Out of scope.

### 8. No canary deployment

We don't do canary.

**The pain**: Canary. Out of scope.

### 9. No service mesh

We don't use Istio or Linkerd.

**The pain**: Service mesh. Out of scope.

### 10. No secrets management

We use env vars. For production, use a secrets manager.

**The pain**: Secrets management. Out of scope.

---

## What This Project Forbids Us From Doing

This server can:

- Run reproducibly in any Docker environment
- Be deployed with `docker compose up`
- Persist data via volumes
- Restart automatically on crash

It cannot:

- Run tests automatically in CI
- Show metrics
- Be split into microservices
- Scale to hundreds of containers
- Use Kubernetes
- Use Helm
- Auto-scale
- Do blue/green or canary deployments
- Use a service mesh
- Use a secrets manager

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 38 | Pipeline | "I want CI/CD." |
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

Project 38 is the natural next step. We have Docker. Now we need CI/CD.

---

## What You Should Do Now

1. **Read the code.** Notice the `Dockerfile` (multi-stage build), the `docker-compose.yml` (app + Redis), the volume for persistence. The HTTP handlers are unchanged.
2. **Run `docker compose up --build`.** See the app start.
3. **Test the app.** `curl http://localhost:3000/`. See the response.
4. **Run `docker compose down`.** See the app stop.
5. **When you are ready**, move to [Project 38: Pipeline](../38-pipeline/).
6. **If anything is unclear**, do not proceed. Docker is the foundation of reproducible deployments. It must be solid.

---

## A Note on the Bigger Picture

You now have a reproducible app. The container runs the same on any machine. Deploy is `docker compose up`. Anyone with Docker can run your app.

From here, the path diverges into the final 3 projects of Phase 6 (Production):

- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The app is reproducible. The path continues.

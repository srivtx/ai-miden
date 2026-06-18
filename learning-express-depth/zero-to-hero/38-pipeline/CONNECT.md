# The Connect

> *"The app is continuously deployed. Now we need observability and microservices."*

This project added CI/CD. The pain of "I forgot to run the tests" is solved. Every commit is tested. Every merge to main is built and deployed. The pipeline is automatic.

The next 2 projects complete Phase 6 (Production):

| # | Project | Pain Answered |
|---|---------|---------------|
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

After these, the server is a production-ready, real-time, role-based, tested, deployed, observed, distributed system. The complete backend for the final artifact.

## What Works

- CI workflow (tests on every push)
- CD workflow (build and deploy on every merge to main)
- Docker image tagged with git SHA
- Deploy via SSH
- Secrets for sensitive data

## What Doesn't Work

### 1. No observability

We can't see metrics (request rate, error rate, latency, etc.).

**The pain**: Observability. Project 39.

### 2. No microservices

One big monolith.

**The pain**: Microservices. Project 40.

### 3. No multi-environment

We deploy to one environment (production).

**The pain**: Multi-environment. Out of scope.

### 4. No auto-rollback

A failed deploy stays in production.

**The pain**: Auto-rollback. Out of scope.

### 5. No canary

A bug reaches 100% of users.

**The pain**: Canary. Out of scope.

### 6. No approval workflow

A bad deploy can happen without human review.

**The pain**: Approval. Out of scope.

### 7. No deployment service

We use SSH. For production, use ECS/Cloud Run/etc.

**The pain**: Deployment service. Out of scope.

### 8. No changelog

We don't generate release notes.

**The pain**: Changelog. Out of scope.

### 9. No notifications

We don't notify Slack on deploy.

**The pain**: Notifications. Out of scope.

### 10. No secrets management

We use GitHub Secrets. For production, use Vault/AWS Secrets Manager.

**The pain**: Secrets management. Out of scope.

---

## What This Project Forbids Us From Doing

This server can:

- Run tests automatically on every push
- Build and push Docker images on every merge
- Deploy via SSH to a single environment
- Use secrets for sensitive data

It cannot:

- Show metrics
- Be split into microservices
- Deploy to multiple environments
- Auto-rollback on failure
- Do canary deployment
- Require approval before deploy
- Use a deployment service
- Generate changelogs
- Send notifications
- Use a secrets manager

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

Project 39 is the natural next step. We have CI/CD. Now we need to see what's happening in production.

---

## What You Should Do Now

1. **Read the code.** Notice the CI workflow (test on every push), the CD workflow (build and deploy on every merge). The HTTP handlers are unchanged.
2. **Push the workflows.** See the CI run on GitHub Actions.
3. **Merge a PR to main.** See the CD run.
4. **Check the deployed app.** Verify the new version is live.
5. **When you are ready**, move to [Project 39: Observability](../39-observability/).
6. **If anything is unclear**, do not proceed. CI/CD is the foundation of automation. It must be solid.

---

## A Note on the Bigger Picture

You now have a continuously deployed app. Every change is tested. Every merge to main is deployed. The pipeline is automatic.

From here, the path diverges into the final 2 projects of Phase 6 (Production):

- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The app is continuously deployed. The path continues.

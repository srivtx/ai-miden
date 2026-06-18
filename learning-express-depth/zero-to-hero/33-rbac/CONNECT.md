# The Connect

> *"The server knows what you can do. Now we need webhooks, payments, tests, Docker, CI/CD, observability, and microservices."*

This project added RBAC. The pain of "everyone has the same permissions" is solved. The server knows what each user can do in each workspace. Roles are hierarchical. The `requireRole` middleware is composable.

The next 7 projects complete Phase 6 (Production):

| # | Project | Pain Answered |
|---|---------|---------------|
| 34 | Webhook | "I want to push events to other services." |
| 35 | Payment | "I want to charge for premium features." |
| 36 | Tests | "I want to verify everything works automatically." |
| 37 | Container | "I want to deploy reproducibly with Docker." |
| 38 | Pipeline | "I want CI/CD." |
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

After these, the server is a production-ready, real-time, role-based, tested, deployed, observed, distributed system. The complete backend for the final artifact (Cove, the Slack × Notion × Figma-lite hybrid).

## What Works

- `workspaces` and `workspace_members` tables
- 4 roles (owner, admin, member, guest) with hierarchy
- `requireRole(...)` middleware
- Workspace CRUD
- Member management (invite, change role)
- Workspace-scoped posts

## What Doesn't Work

### 1. No webhooks

We can't push events to other services (e.g., "new post created" → notify Slack).

**The pain**: Webhooks. Project 34.

### 2. No payment

No Stripe integration. We can't charge for premium features.

**The pain**: Payment. Project 35.

### 3. No tests

We can't verify anything works automatically. No unit tests, no integration tests.

**The pain**: Tests. Project 36.

### 4. No Docker

We can't deploy reproducibly. Different machines have different Node versions, different OS, etc.

**The pain**: Container. Project 37.

### 5. No CI/CD

We can't run tests automatically on every commit. We can't deploy automatically on merge to main.

**The pain**: Pipeline. Project 38.

### 6. No observability

We can't see metrics (request rate, error rate, latency, etc.). We can't trace a request across services.

**The pain**: Observability. Project 39.

### 7. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

### 8. No resource-level permissions

Workspace-level only. Can't have "Bob can read post 42 but not others."

**The pain**: Resource-level permissions. Out of scope.

### 9. No custom roles

4 fixed roles. Can't define custom roles.

**The pain**: Custom roles. Out of scope.

### 10. No audit log

We don't track who did what when. For compliance, this is important.

**The pain**: Audit log. Out of scope.

---

## What This Project Forbids Us From Doing

This server can:

- Assign roles to users per workspace
- Check the user's role for a workspace-scoped action
- Enforce a role hierarchy
- Combine role checks with ownership checks

It cannot:

- Push events to other services
- Charge for premium features
- Be tested automatically
- Be deployed reproducibly
- Be observed in production
- Be split into microservices
- Have resource-level permissions
- Have custom roles
- Track who did what when

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 34 | Webhook | "I want to push events to other services." |
| 35 | Payment | "I want to charge for premium features." |
| 36 | Tests | "I want to verify everything works automatically." |

Project 34 is the natural next step. We have RBAC. Now we need webhooks — the server notifies external services when events happen.

---

## What You Should Do Now

1. **Read the code.** Notice the `workspaces` and `workspace_members` tables, the `requireRole` middleware, the role hierarchy. The HTTP handlers are extended.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Create a workspace.** Add a member. Try actions as different roles. See the 403s.
4. **Try to add a member as `member` role.** See the rejection.
5. **When you are ready**, move to [Project 34: Webhook](../34-webhook/).
6. **If anything is unclear**, do not proceed. RBAC is the foundation of authorization. It must be solid.

---

## A Note on the Bigger Picture

You now have a server that knows *who you are* (authentication) and *what you can do* (authorization via RBAC). The foundation of every secure multi-user app is in place.

From here, the path diverges into the final 7 projects of Phase 6 (Production):

- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

## The Cove Editor

Project 33 is the recommended server for running the Cove collaborative workspace editor. It serves `../cove/editor.html` at `/cove/editor.html` and handles all real-time features: chat broadcast, canvas draw sync with history replay, collaborative doc sync, presence tracking, WebRTC voice with caller notification, and RBAC workspaces. Two browser tabs with different usernames is all you need to see the full stack in action.

The server knows what you can do. The path continues.

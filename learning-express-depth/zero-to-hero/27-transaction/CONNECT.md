# The Connect

> *"Multi-step writes are atomic. Now we need real-time, RBAC, and the rest of the operations."*

This project added transactions. The pain of "multi-step writes leave the system inconsistent" is solved. Money transfers (and similar multi-step writes) are atomic. Either both writes happen, or neither. The system is always consistent.

**Phase 4 (Real-World Operations) is now complete!** Projects 19-27 added: search, file upload, email, caching, Redis, rate limiting, cron, queue, transactions. The API has all the real-world operations.

But the API is still missing:

1. **No real-time** — every request is one-shot. The server cannot push updates.
2. **No RBAC** — all authenticated users have the same permissions. No "admin" role.
3. **No webhooks** — we can't push events to other services.
4. **No payment** — no Stripe integration.
5. **No tests** — we can't verify anything works automatically.
6. **No Docker / CI/CD** — we can't deploy reproducibly.
7. **No observability** — we can't see metrics.
8. **No microservices** — one big monolith.

Projects 28-40 (Phases 5 and 6) will address these. After Phase 6, the API is a production-ready, real-time, role-based, tested, deployed, observed, distributed system.

## What Works

- Transactions for multi-step writes
- Atomic money transfers
- Cache invalidation after the transaction
- Authorization check before the transaction
- Error rollback

## What Doesn't Work

### 1. No real-time

Every request is one-shot. The server cannot push updates.

**The pain**: Real-time. Project 28 (WebSocket).

### 2. No RBAC

All authenticated users have the same permissions. No "admin" role.

**The pain**: RBAC. Project 33.

### 3. No webhooks

We can't push events to other services.

**The pain**: Webhooks. Project 34.

### 4. No payment

No Stripe integration.

**The pain**: Payment. Project 35.

### 5. No tests

We can't verify anything works automatically.

**The pain**: Tests. Project 36.

### 6. No Docker / CI/CD

We can't deploy reproducibly.

**The pain**: Container. Project 37.

### 7. No observability

We can't see metrics (request rate, error rate, latency, etc.).

**The pain**: Observability. Project 39.

### 8. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

---

## What This Project Forbids Us From Doing

This server can:

- Make multi-step writes atomic
- Ensure data consistency
- Handle money transfers safely

It cannot:

- Push updates to clients in real-time
- Have role-based permissions
- Push events to other services
- Charge for premium features
- Be tested automatically
- Be deployed reproducibly
- Be observed in production
- Be split into microservices

Each is a future project.

---

## The Order of Subsequent Projects

Projects 28-40:

| # | Project | Phase |
|---|---------|-------|
| 28 | WebSocket | 5: Real-Time |
| 29 | SSE | 5: Real-Time |
| 30 | Presence | 5: Real-Time |
| 31 | CRDT | 5: Real-Time |
| 32 | WebRTC | 5: Real-Time |
| 33 | RBAC | 6: Production |
| 34 | Webhook | 6: Production |
| 35 | Payment | 6: Production |
| 36 | Tests | 6: Production |
| 37 | Container | 6: Production |
| 38 | Pipeline | 6: Production |
| 39 | Observability | 6: Production |
| 40 | Microservice | 6: Production |

Project 28 (WebSocket) is the natural next step. The API can do everything except real-time. We need bidirectional communication.

---

## What You Should Do Now

1. **Read the code.** Notice the `db.transaction(async (trx) => { ... })` pattern, the `trx` object, the throw on insufficient funds. The transaction rolls back on error.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Transfer money.** See the balances change.
4. **Try to transfer more than you have.** See the rollback.
5. **When you are ready**, move to [Project 28: The WebSocket](../28-websocket/).
6. **If anything is unclear**, do not proceed. Transactions are the foundation of data integrity. They must be solid.

---

## A Note on the Bigger Picture

You now have a server where **multi-step writes are atomic**. The system is always consistent. Money is conserved. Users and workspaces are created together.

**Phase 4 (Real-World Operations) is complete.** The API has search, file upload, email, caching, Redis, rate limiting, cron, queue, and transactions. It's a real, production-ready backend.

From here, the path diverges into:

- **Phase 5: Real-Time** (28-32) — WebSocket, SSE, presence, CRDT, WebRTC
- **Phase 6: Production** (33-40) — RBAC, webhooks, payments, tests, Docker, CI/CD, observability, microservices

Multi-step writes are atomic. The path continues.

---

## Phase 4 Complete: Real-World Operations

The 9 projects in this phase:

- 19: Searcher (FTS5)
- 20: Uploader (Multer)
- 21: Mailroom (Nodemailer)
- 22: Cache (in-memory)
- 23: Redis (distributed cache)
- 24: Rate Limiter (rate-limiter-flexible)
- 25: Cron (node-cron)
- 26: Queue (BullMQ)
- 27: Transaction (Knex)

The server has *all* the real-world operations. The path continues to Phase 5: Real-Time.

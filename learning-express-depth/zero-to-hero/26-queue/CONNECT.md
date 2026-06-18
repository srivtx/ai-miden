# The Connect

> *"The server has a queue. Now we need transactions, real-time, and the rest of the operations."*

This project added a queue with BullMQ. The pain of "the user waits for slow work" is solved. The welcome email is moved off the request. The user gets a fast response. The work is done reliably in the background.

But the API is still missing:

1. **No transactions** — multi-step writes can fail mid-way, leaving the database in a bad state.

Project 27 (the last in Phase 4) will fix this. After Phase 4, the API has *all* the real-world operations: file upload, email, caching, rate limiting, cron, queue, transactions.

## What Works

- BullMQ queue
- Welcome email moved off the request
- Worker in the same process
- 3 retries with exponential backoff
- Logs job execution and failures

## What Doesn't Work

### 1. No transactions

Multi-step writes can fail mid-way, leaving the database in a bad state.

**The pain**: Transactions. Project 27.

### 2. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 3. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 4. No tests

We can't verify the queue works.

**The pain**: Tests. Project 36.

### 5. No observability

We can't see queue depth, job history, etc.

**The pain**: Observability. Project 39.

### 6. No WebSocket

Every request is one-shot. The server cannot push.

**The pain**: WebSocket. Project 28.

### 7. No real-time

No live updates, no presence, no co-editing.

**The pain**: Real-time. Project 28+.

### 8. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

### 9. No RBAC

All authenticated users have the same permissions. No "admin" role.

**The pain**: RBAC. Project 33.

### 10. No Webhooks

We can't push events to other services.

**The pain**: Webhooks. Project 34.

---

## What This Project Forbids Us From Doing

This server can:

- Move slow work off the request
- Process jobs in the background
- Retry failed jobs with backoff
- Persist jobs in Redis

It cannot:

- Make atomic multi-step writes
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically
- Be observed in production
- Push updates to clients
- Support real-time features
- Be split into microservices
- Have role-based permissions
- Push events to other services

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 27 | The Transaction | "I want to make atomic multi-step writes." |

Project 27 is the last in Phase 4. After that, we move to Phase 5 (Real-Time).

---

## What You Should Do Now

1. **Read the code.** Notice the queue, the worker, the `emailQueue.add(...)` in the signup. The handler returns immediately.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Sign up.** See the fast response.
4. **Check the email preview** in the logs.
5. **Stop the worker** (comment out the worker code). Sign up. The job sits in the queue. Restart the worker. See the job process.
6. **When you are ready**, move to [Project 27: The Transaction](../27-transaction/).
7. **If anything is unclear**, do not proceed. Queues are the foundation of every production app. They must be solid.

---

## A Note on the Bigger Picture

You now have a server with a *queue*. Slow work is off the request. The user is fast. The work is reliable.

From here, the path diverges:

- **Transactions** (project 27): atomic multi-write operations
- **WebSocket** (project 28): bidirectional channel
- **SSE** (project 29): server-push
- **Presence** (project 30): who's online
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server has a queue. The path continues.

# The Connect

> *"The server has automation. Now we need a queue, transactions, and the rest of the operations."*

This project added scheduled tasks with `node-cron`. The pain of "I need to run things on a schedule" is solved. The server runs session cleanup, database vacuum, and daily digest automatically. The user doesn't have to trigger them.

But the API is still missing:

1. **No queue** — slow work (email send, image processing) blocks the request.
2. **No transactions** — multi-step writes can fail mid-way, leaving the database in a bad state.

Projects 26-27 (rest of Phase 4) will fix these. After Phase 4, the API has *all* the real-world operations: file upload, email, caching, rate limiting, cron, queue, transactions.

## What Works

- 3 cron jobs (session cleanup, vacuum, digest)
- Log every job execution
- Catches errors and logs them
- Runs in the same process

## What Doesn't Work

### 1. No queue

Slow work (email send, image processing) blocks the request. The user waits.

**The pain**: Queue. Project 26.

### 2. No transactions

Multi-step writes can fail mid-way, leaving the database in a bad state.

**The pain**: Transactions. Project 27.

### 3. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 4. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 5. No tests

We can't verify the cron jobs work.

**The pain**: Tests. Project 36.

### 6. No observability

We can't see job execution history.

**The pain**: Observability. Project 39.

### 7. No WebSocket

Every request is one-shot. The server cannot push.

**The pain**: WebSocket. Project 28.

### 8. No real-time

No live updates, no presence, no co-editing.

**The pain**: Real-time. Project 28+.

### 9. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

### 10. No RBAC

All authenticated users have the same permissions. No "admin" role.

**The pain**: RBAC. Project 33.

---

## What This Project Forbids Us From Doing

This server can:

- Run scheduled tasks automatically
- Log every job execution
- Catch and log errors

It cannot:

- Move slow work off the request
- Make atomic multi-step writes
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically
- Be observed in production
- Push updates to clients
- Support real-time features
- Be split into microservices
- Have role-based permissions

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 26 | The Queue | "I want to move slow work off the request." |
| 27 | The Transaction | "I want to make atomic multi-step writes." |

Project 26 is the natural next step. We have cron. Now we need a queue for slow work.

---

## What You Should Do Now

1. **Read the code.** Notice the 3 cron jobs, the try/catch, the log. The handlers are unchanged.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Change the schedule to every minute** for testing. See the jobs run.
4. **Add your own cron job.** Something useful for your app.
5. **When you are ready**, move to [Project 26: The Queue](../26-queue/).
6. **If anything is unclear**, do not proceed. Scheduled tasks are the foundation of every production app. They must be solid.

---

## A Note on the Bigger Picture

You now have a server that *automates* tasks. The user doesn't have to trigger them. The work happens on a schedule.

From here, the path diverges:

- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The server has automation. The path continues.

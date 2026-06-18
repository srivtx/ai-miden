# The Connect

> *"The cache is shared. Now we need rate limiting, cron, queue, and transactions."*

This project switched the cache from in-memory to Redis. The pain of "the cache is not shared across processes" is solved. All processes connect to the same Redis. The cache is consistent.

But the API is still vulnerable:

1. **No rate limiting** — a malicious client can hammer endpoints.
2. **No cron** — things that should fire on a schedule don't.
3. **No queue** — slow work blocks the request.
4. **No transactions** — multi-step writes can fail mid-way.

Projects 24-27 (rest of Phase 4) will fix these. After Phase 4, the API has *all* the real-world operations: file upload, email, caching, rate limiting, cron, queue, transactions.

## What Works

- Redis-backed cache (shared across processes)
- Same Cache API (`get`, `set`, `delete`)
- Async (Redis is async)
- Fail open on Redis errors
- Invalidation on PATCH/DELETE

## What Doesn't Work

### 1. No rate limiting

A malicious client can hammer endpoints. 1000 requests per second to `/login` would try 1000 password combinations per second.

**The pain**: Rate limiting. Project 24.

### 2. No cron

Things that should fire on a schedule (session cleanup, daily digest, scheduled posts) don't.

**The pain**: Cron. Project 25.

### 3. No queue

Slow work (email send, image processing, payment processing) blocks the request. The user waits.

**The pain**: Queue. Project 26.

### 4. No transactions

Multi-step writes can fail mid-way, leaving the database in a bad state. For example, "transfer $100 from A to B" could fail after debiting A but before crediting B.

**The pain**: Transactions. Project 27.

### 5. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 6. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 7. No tests

We can't verify the cache works.

**The pain**: Tests. Project 36.

### 8. No observability

We can't see the cache hit rate.

**The pain**: Observability. Project 39.

### 9. No WebSocket

Every request is one-shot. The server cannot push.

**The pain**: WebSocket. Project 28.

### 10. No real-time

No live updates, no presence, no co-editing.

**The pain**: Real-time. Project 28+.

---

## What This Project Forbids Us From Doing

This server can:

- Cache reads in shared memory
- Invalidate on writes
- Survive Redis outages (fail open)

It cannot:

- Rate-limit clients
- Run scheduled jobs
- Move slow work off the request
- Make atomic multi-step writes
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically
- Be observed in production
- Push updates to clients
- Support real-time features

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 24 | The Rate Limiter | "I want to throttle abuse." |
| 25 | The Cron | "I want to run scheduled jobs." |
| 26 | The Queue | "I want to move slow work off the request." |

Project 24 is the natural next step. The cache is shared. Now we need to protect it (and the rest of the API) from abuse.

---

## What You Should Do Now

1. **Read the code.** Notice the Redis client, the `Cache` class, the async operations. The handlers `await` the cache.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Start Redis.** Make sure it's running.
4. **Make some requests.** See the cache in action.
5. **Stop Redis.** Make a request. See the fail-open behavior.
6. **When you are ready**, move to [Project 24: The Rate Limiter](../24-rate-limiter/).
7. **If anything is unclear**, do not proceed. Distributed caching is the foundation of every high-traffic app. It must be solid.

---

## A Note on the Bigger Picture

You now have a *shared cache*. The cache is consistent across processes. The database load is reduced. The user is faster.

From here, the path diverges:

- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The cache is shared. The path continues.

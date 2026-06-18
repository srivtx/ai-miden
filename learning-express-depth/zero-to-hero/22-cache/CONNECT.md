# The Connect

> *"The API has a cache. Now we need shared state, rate limiting, and the rest of the operations."*

This project added in-memory caching with TTL. The pain of "the database is on fire" is solved. Popular reads hit the cache. The database load drops.

But the cache is in memory. Each process has its own cache. A write on process 1 doesn't invalidate the cache on process 2. The cache is not shared.

Projects 23-27 will fix this and more:

1. **Redis** — shared state across processes
2. **Rate limiting** — throttle abuse
3. **Cron** — scheduled jobs
4. **Queue** — move slow work off the request
5. **Transactions** — atomic multi-write operations

After Phase 4, the API has *all* the real-world operations: file upload, email, caching, rate limiting, cron, queue, transactions.

## What Works

- In-memory cache with TTL
- Cache-aside pattern for `GET /posts/:id` and `GET /users/:id`
- Invalidation on PATCH and DELETE
- 1-minute default TTL

## What Doesn't Work

### 1. Cache is not shared

Each process has its own cache. Multi-process / multi-region is hard.

**The pain**: Redis. Project 23.

### 2. No rate limiting

A malicious client can hammer endpoints.

**The pain**: Rate limiting. Project 24.

### 3. No cron

Things that should fire on a schedule (session cleanup, daily digest) don't.

**The pain**: Cron. Project 25.

### 4. No queue

Slow work (email send) blocks the request.

**The pain**: Queue. Project 26.

### 5. No transactions

Multi-step writes can fail mid-way, leaving the database in a bad state.

**The pain**: Transactions. Project 27.

### 6. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 7. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 8. No tests

We can't verify the cache works.

**The pain**: Tests. Project 36.

### 9. No observability

We can't see the cache hit rate.

**The pain**: Observability. Project 39.

### 10. No file upload

We can't attach images to posts.

Wait — we added that in project 20. The cache is the new addition. Let me correct: project 20 (file upload) is done. Project 22 (cache) is the latest.

---

## What This Project Forbids Us From Doing

This server can:

- Cache reads in memory
- Invalidate on writes
- Reduce database load

It cannot:

- Share the cache across processes
- Rate-limit clients
- Run scheduled jobs
- Move slow work off the request
- Make atomic multi-step writes
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically
- Be observed in production

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 23 | The Redis | "I want shared state across processes." |
| 24 | The Rate Limiter | "I want to throttle abuse." |
| 25 | The Cron | "I want to run scheduled jobs." |

Project 23 is the natural next step. The cache is in memory. We need it to be shared.

---

## What You Should Do Now

1. **Read the code.** Notice the `Cache` class, the cache-aside pattern in handlers, the invalidation in PATCH/DELETE.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Make the same request twice.** See the cache hit on the second request.
4. **Update a post.** See the cache invalidate.
5. **Try a different TTL.** See the effect.
6. **When you are ready**, move to [Project 23: The Redis](../23-redis/).
7. **If anything is unclear**, do not proceed. Caching is the foundation of every high-traffic app. It must be solid.

---

## A Note on the Bigger Picture

You now have an API that *caches*. Popular reads are fast. The database load is reduced. The user is faster.

From here, the path diverges:

- **Redis** (project 23): shared state across processes
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The API has a cache. The path continues.

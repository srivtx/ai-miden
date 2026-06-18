# The Connect

> *"The API is protected. Now we need cron, queue, and transactions."*

This project added rate limiting with `rate-limiter-flexible`. The pain of "an attacker can hammer the API" is solved. The token bucket caps the rate. Abusive clients are throttled. Legitimate users are unaffected.

But the API is still missing:

1. **No cron** — things that should fire on a schedule (session cleanup, daily digest, scheduled posts) don't.
2. **No queue** — slow work (email send, image processing) blocks the request.
3. **No transactions** — multi-step writes can fail mid-way, leaving the database in a bad state.

Projects 25-27 (rest of Phase 4) will fix these. After Phase 4, the API has *all* the real-world operations: file upload, email, caching, rate limiting, cron, queue, transactions.

## What Works

- Rate limiting with `rate-limiter-flexible`
- Redis-backed (shared across processes)
- 100 requests per minute per IP (default)
- Returns 429 with `Retry-After` when exceeded
- Logs rate limit hits

## What Doesn't Work

### 1. No cron

Things that should fire on a schedule (session cleanup, daily digest, scheduled posts) don't.

**The pain**: Cron. Project 25.

### 2. No queue

Slow work (email send, image processing) blocks the request.

**The pain**: Queue. Project 26.

### 3. No transactions

Multi-step writes can fail mid-way, leaving the database in a bad state.

**The pain**: Transactions. Project 27.

### 4. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 5. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 6. No tests

We can't verify the rate limit works.

**The pain**: Tests. Project 36.

### 7. No observability

We can't see the rate limit hit rate.

**The pain**: Observability. Project 39.

### 8. No WebSocket

Every request is one-shot. The server cannot push.

**The pain**: WebSocket. Project 28.

### 9. No real-time

No live updates, no presence, no co-editing.

**The pain**: Real-time. Project 28+.

### 10. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

---

## What This Project Forbids Us From Doing

This server can:

- Throttle abusive clients
- Return 429 with Retry-After
- Log rate limit hits
- Share the rate limit across processes (Redis)

It cannot:

- Run scheduled jobs
- Move slow work off the request
- Make atomic multi-step writes
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically
- Be observed in production
- Push updates to clients
- Support real-time features
- Be split into microservices

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 25 | The Cron | "I want to run scheduled jobs." |
| 26 | The Queue | "I want to move slow work off the request." |
| 27 | The Transaction | "I want to make atomic multi-step writes." |

Project 25 is the natural next step. We have rate limiting. Now we need scheduled jobs (cleanup, digests, etc.).

---

## What You Should Do Now

1. **Read the code.** Notice the rate limiter, the middleware, the trust proxy. The handlers are unchanged.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Make 100 requests.** See the 101st fail.
4. **Wait 60 seconds.** See the bucket refill.
5. **Set a stricter limit.** See the effect.
6. **When you are ready**, move to [Project 25: The Cron](../25-cron/).
7. **If anything is unclear**, do not proceed. Rate limiting is the foundation of every production API. It must be solid.

---

## A Note on the Bigger Picture

You now have an API that is *protected*. Abusive clients are throttled. Legitimate users are unaffected. The token bucket caps the rate.

From here, the path diverges:

- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The API is protected. The path continues.

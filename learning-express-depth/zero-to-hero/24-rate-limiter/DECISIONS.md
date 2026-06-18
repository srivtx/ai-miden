# The Decisions

> *"A bucket of tokens. Each request takes one. The bucket refills. When empty, reject."*

## Decision 1: rate-limiter-flexible and not express-rate-limit

**Alternative**: `express-rate-limit` (the simpler Express-specific library).

**Why rate-limiter-flexible: More algorithms (token bucket, fixed window, sliding window). More stores (memory, Redis, Memcached). More flexibility. The standard for non-trivial rate limiting.

**Trade-off**: Slightly more verbose. More features than we need. We accept it.

## Decision 2: Token bucket and not fixed window

**Alternative**: Fixed window (e.g., 100 requests per hour, reset at the top of the hour).

**Why token bucket: Allows bursts (up to the bucket size) but limits sustained rate. More forgiving for legitimate users.

**Trade-off**: More complex. We accept it.

## Decision 3: Redis store and not memory

**Alternative**: In-memory store (each process has its own counter).

**Why Redis: Multi-process / multi-region. The rate limit is consistent across all processes. A single Redis is the source of truth.

**Trade-off**: A Redis outage means the rate limiter is down. We fail open (allow all). For high-security apps, you'd fail closed.

## Decision 4: 100 per minute and not stricter

**Alternative**: 10 per minute (stricter), 1000 per hour (looser).

**Why 100 per minute: A balance between UX and abuse prevention. 100 per minute is enough for a user clicking around. An attacker would need 100 different IPs to bypass.

**Trade-off**: A determined attacker can still try 100 requests per minute per IP. We accept this. For sensitive endpoints, we add stricter limits.

## Decision 5: Fail open on Redis errors

**Alternative**: Fail closed (return 503 if Redis is down).

**Why fail open: The system is available, just unprotected. The database load might spike. We accept this for availability.

**Trade-off**: A Redis outage removes the rate limit. We accept this.

## Decision 6: Global limit, not per-endpoint

**Alternative**: Different limits per endpoint (e.g., 5 per minute for login, 100 per minute for posts).

**Why global for now: Simpler. One middleware. Covers all endpoints. We can add per-endpoint later.

**Trade-off**: Sensitive endpoints (login, password reset) have the same limit as read endpoints. A stricter limit is needed for them. We add per-endpoint in a future project.

## Decision 7: Per-IP, not per-user

**Alternative**: Use `req.user.userId` for authenticated endpoints.

**Why per-IP: It applies to all requests, including unauthenticated. An attacker can't bypass by being unauthenticated.

**Trade-off**: Multiple users behind the same NAT share the same IP. A classroom or office might hit the limit. We accept this.

## Decision 8: trust proxy

`app.set('trust proxy', 1)` tells Express to trust the `X-Forwarded-For` header.

**Why: Behind a load balancer, `req.ip` is the load balancer's IP, not the client's. `trust proxy` makes Express read the real client IP from the header.

**Trade-off**: A malicious client could spoof the header. In a real app, you'd only trust proxies you control.

## Decision 9: Retry-After header

We set `Retry-After: 60` when the limit is exceeded.

**Why: Standard HTTP. Tells the client when to try again. Most HTTP clients respect this.

**Trade-off**: None. It's a small addition.

## Decision 10: Log rate limit hits

We log every rate limit hit.

**Why: For debugging and abuse detection. We can see which IPs are being throttled.

**Trade-off**: Log volume. We accept it.

---

## What We Did Not Decide

- **Per-endpoint limits** — out of scope
- **Per-user limits** — out of scope
- **Captcha** — out of scope
- **IP allowlist/blocklist** — out of scope
- **Distributed rate limiting across regions** — out of scope
- **Custom error responses** — out of scope
- **Adaptive rate limiting** — out of scope
- **Rate limit on file uploads** — out of scope

Each is a future decision.

---

## The Meta-Decision: The API Is Protected

For 23 projects, the API was unprotected. Any client could make unlimited requests. An attacker could brute-force passwords, scrape data, or spam emails.

Now the API is protected. The token bucket caps the rate. Abusive clients are throttled. Legitimate users are unaffected.

This is the foundation of *every* production API. Rate limiting is non-negotiable. The patterns (token bucket, Redis store, per-IP) are universal.

The next 16 projects will assume rate limiting exists. The path diverges:

- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
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

The API is protected. The path continues.

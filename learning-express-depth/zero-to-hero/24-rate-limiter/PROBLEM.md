# The Problem

> *"An API without rate limiting is a public toilet. Everyone uses it. No one is responsible."*

## Why Rate Limiting Is Essential

An API is a public resource. Without rate limiting:

- A **script kiddie** can hammer `/login` with thousands of password attempts per second
- A **scraper** can pull your entire user database in minutes
- A **bot** can spam your `/sessions/forgot` with thousands of emails, costing you money
- A **legit user with a bug** can accidentally hammer the API, causing cascading failures
- A **competitor** can take down your service with a simple attack

The fix: cap the number of requests per client per time window. If the limit is exceeded, return 429 Too Many Requests.

## What Pain Is This Solving?

Imagine your `/login` endpoint is being hit 1000 times per second by a brute-force attacker. Each attempt does a bcrypt compare (slow, ~100ms). 1000 attempts = 100 seconds of CPU time per second. The server is overwhelmed. Legitimate users can't log in. The site is down.

With rate limiting (e.g., 10 login attempts per minute per IP), the attacker is throttled. 10 attempts per minute is useless for brute-force. Legitimate users are unaffected.

## The Deeper Problem: Distributed Rate Limiting

Rate limiting must work across processes. If you have 10 server processes and each has its own counter, an attacker can distribute 100 requests per second across 10 processes (10 each). Each process sees 10 requests, well under the limit.

The fix: a shared counter. All processes increment the same counter (in Redis). If the counter exceeds the limit, the request is rejected.

This is exactly what `rate-limiter-flexible` with the Redis store provides.

## The Token Bucket Algorithm

The most common rate limiting algorithm is the **token bucket**:

- Each client has a bucket of N tokens (e.g., 100)
- The bucket refills at a rate of M tokens per second (e.g., 1 per second)
- Each request consumes one token
- If the bucket is empty, the request is rejected

For example:
- 100 tokens, refilling 1 per second
- The client can make 100 requests immediately (bucket starts full)
- After 100 requests, the bucket is empty
- The bucket refills 1 token per second
- The client can make 1 request per second after that

This allows bursts (up to N requests) but limits sustained rate (1 per second).

## What This Project Will Solve

This project will:

1. Add `rate-limiter-flexible` as a dependency
2. Configure it with Redis as the store
3. Add a rate limit middleware
4. Apply it to all routes
5. Return 429 when the limit is exceeded

By the end, the API is protected from abuse.

## What This Project Will *Not* Solve

- **Per-endpoint limits** — we use a global limit. For per-endpoint, you'd add multiple limiters.
- **Per-user limits** — we limit by IP. For authenticated users, you'd limit by user ID.
- **Custom responses** — we return 429 with a generic message. You could return `Retry-After` header.
- **Distributed rate limiting with multiple regions** — we use a single Redis. For multi-region, you'd use a global Redis.
- **Captcha** — out of scope. After exceeding the limit, a captcha could be required.
- **IP allowlist/blocklist** — out of scope. You could allow certain IPs to bypass.

## The Question This Project Answers

> *"How do I prevent a single client from making too many requests?"*

If you can answer: "use a token bucket, store in Redis, apply as middleware, return 429," you are ready for project 25.

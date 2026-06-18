# Project 24: The Rate Limiter

> *"A client making 1000 requests per second is not a user. It's an attack."*

In projects 22-23, we have a cache. But a malicious client can:

- Make 1000 requests per second to `/login`, trying 1000 passwords per second
- Make 1000 requests per second to `/users`, scraping user data
- Make 1000 requests per second to `/sessions/forgot`, spamming emails

We need **rate limiting**: a maximum number of requests per IP (or per user) per time window. If the limit is exceeded, we return `429 Too Many Requests`.

We use `rate-limiter-flexible` — the de-facto rate limiter for Node. It uses Redis as the store, so the rate limit is shared across processes. The most common algorithm is the **token bucket**: each IP has a bucket of N tokens. Each request consumes one token. The bucket refills at a rate of M tokens per second. If the bucket is empty, the request is rejected.

By the end, abusive clients are throttled. Legitimate clients are unaffected.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is rate limiting essential? What is a token bucket?
2. [The Thought](./THOUGHT.md) — How does rate-limiter-flexible work? What is 429?
3. [The Build](./BUILD.md) — Line-by-line construction of the rate limiter
4. [The Decisions](./DECISIONS.md) — Why rate-limiter-flexible? Why token bucket? Why Redis?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Rate limiting caps the number of requests per IP (or per user) per time window. We use the token bucket algorithm: each IP has a bucket of N tokens. Each request consumes one token. The bucket refills at a rate of M tokens per second. If the bucket is empty, the request is rejected with 429. We use `rate-limiter-flexible` with Redis as the store, so the rate limit is shared across processes.

---

## The Code

```bash
npm install rate-limiter-flexible
```

```js
const { RateLimiterRedis } = require('rate-limiter-flexible');

const rateLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'rl',
  points: 100, // 100 requests
  duration: 60, // per 60 seconds
});

async function rateLimitMiddleware(req, res, next) {
  try {
    const key = req.ip;
    await rateLimiter.consume(key, 1);
    next();
  } catch (err) {
    res.status(429).json({ error: 'Too Many Requests', code: 'RATE_LIMIT' });
  }
}

app.use(rateLimitMiddleware);
```

Test it:

```bash
# First 100 requests succeed
for i in {1..100}; do curl -s http://localhost:3000/ > /dev/null; done

# 101st request fails
curl -i http://localhost:3000/
# HTTP/1.1 429 Too Many Requests
# {"error":"Too Many Requests","code":"RATE_LIMIT"}
```

The pain of "an attacker can hammer the API" is solved. The attacker is throttled. Legitimate users are unaffected.

---

## What You Will Have Learned

- Why rate limiting is essential
- The token bucket algorithm
- The `rate-limiter-flexible` library
- How to use Redis as the rate limit store
- The `429 Too Many Requests` status code
- How to apply rate limits per IP, per user, or per endpoint

These are the foundations of *abuse prevention*. From here, every production API has rate limiting.

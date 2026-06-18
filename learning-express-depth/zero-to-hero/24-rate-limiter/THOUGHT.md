# The Thought

> *"A bucket of tokens. Each request takes one. The bucket refills. When empty, reject."*

## How rate-limiter-flexible Works

`rate-limiter-flexible` is a generic rate limiter. It supports multiple backends (memory, Redis, Memcached) and multiple algorithms (token bucket, fixed window, sliding window).

The basic usage:

```js
const { RateLimiterRedis } = require('rate-limiter-flexible');

const rateLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'rl',
  points: 100, // 100 tokens
  duration: 60, // 60 seconds
});

// In a handler
try {
  await rateLimiter.consume(req.ip, 1);
  // proceed
} catch (err) {
  // 429 Too Many Requests
}
```

`consume(key, points)` tries to consume `points` tokens from the bucket identified by `key`. If the bucket has enough tokens, it succeeds. If not, it throws `RateLimiterError`.

The `key` is what identifies the client. We use `req.ip`. For authenticated users, you could use `req.user.userId`.

## The Token Bucket

The configuration:

- `points: 100` — bucket size
- `duration: 60` — refill window

This means: each IP gets a bucket of 100 tokens, refilling over 60 seconds. So the rate is 100/60 ≈ 1.67 tokens per second. After 100 requests in 60 seconds, the bucket is empty.

You can tune:
- `points: 10, duration: 60` — 10 per minute (strict)
- `points: 1000, duration: 3600` — 1000 per hour (loose)

For different endpoints, you can have different limiters. `/login` might be 10 per minute; `/posts` might be 100 per minute.

## Redis as the Store

`rate-limiter-flexible` with `RateLimiterRedis` stores the counters in Redis. This means:

- Multi-process: all processes see the same counter
- Multi-region: all regions see the same counter (with global Redis)
- Persistence: counters survive Redis restarts (if persistence is enabled)

The store is a simple counter per key. `INCR` and `EXPIRE` are used.

## The Middleware

```js
async function rateLimitMiddleware(req, res, next) {
  try {
    const key = req.ip;
    await rateLimiter.consume(key, 1);
    next();
  } catch (err) {
    res.set('Retry-After', '60');
    res.status(429).json({ error: 'Too Many Requests', code: 'RATE_LIMIT' });
  }
}

app.use(rateLimitMiddleware);
```

The middleware:
- Gets the IP from `req.ip` (Express trusts X-Forwarded-For if `trust proxy` is set)
- Consumes 1 token
- On success, calls `next()`
- On failure, returns 429 with a `Retry-After` header

The `Retry-After` header tells the client when to try again. Standard HTTP behavior.

## trust proxy

`req.ip` requires `trust proxy` to be set if you're behind a load balancer:

```js
app.set('trust proxy', 1);
```

This tells Express to trust the `X-Forwarded-For` header. Without it, `req.ip` is the load balancer's IP, and all clients look the same.

## Common Confusions (read these)

**Confusion 1: "Why not use Express's built-in `express-rate-limit`?"**
You can. `express-rate-limit` is simpler but has fewer features. We use `rate-limiter-flexible` because it has more algorithms, more stores, and more flexibility.

**Confusion 2: "What if Redis is down?"**
The rate limiter throws an error. We could fail open (allow all) or fail closed (block all). We fail open: the system is available, just unprotected during the Redis outage.

**Confusion 3: "Why 100 per minute?"**
A balance between UX and abuse prevention. 100 per minute is enough for a user clicking around. An attacker would need 100 different IPs to bypass.

**Confusion 4: "What about per-user limits?"**
For authenticated endpoints, you could use `req.user.userId` as the key. Per-user limits prevent one user from hammering the API.

**Confusion 5: "What about per-endpoint limits?"**
You can have multiple limiters. One global limiter, plus per-endpoint limiters for sensitive endpoints (login, signup, password reset).

**Confusion 6: "What about the `Retry-After` header?"**
Standard HTTP. Tells the client how many seconds to wait before retrying. We set it to 60 (the duration).

**Confusion 7: "What if the IP is a proxy (Cloudflare, etc.)?"**
`req.ip` returns the proxy's IP, not the client's. You need to set `trust proxy` correctly or use a header like `CF-Connecting-IP` (Cloudflare).

**Confusion 8: "What about IPv6?"**
`req.ip` works for both IPv4 and IPv6. The rate limiter keys are strings.

## What We Are About to Build

A ~400-line Express app that:

1. Has a Redis-backed rate limiter
2. Has a rate limit middleware
3. Applies the limiter to all routes
4. Returns 429 with a `Retry-After` header when the limit is exceeded
5. Logs rate limit hits

The handlers are unchanged. The new piece is the middleware.

In [BUILD.md](./BUILD.md) we will go line by line.

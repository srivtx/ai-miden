# The Build

> *"A bucket of tokens. Each request takes one. The bucket refills. When empty, reject."*

We are going to add rate limiting. The change from project 23: add `rate-limiter-flexible`, configure it with Redis, add a middleware.

## Setup

```bash
# Install the rate limiter
npm install rate-limiter-flexible
```

## The Code

### Imports

```js
const { RateLimiterRedis } = require('rate-limiter-flexible');
```

### The Rate Limiter

```js
const rateLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'rl',
  points: 100, // 100 requests
  duration: 60, // per 60 seconds
});
```

- `storeClient: redis` — use our existing Redis connection
- `keyPrefix: 'rl'` — namespace for the keys (so they don't collide with cache keys)
- `points: 100` — bucket size (100 tokens)
- `duration: 60` — refill window (60 seconds)

### Trust Proxy

```js
app.set('trust proxy', 1);
```

Tells Express to trust the `X-Forwarded-For` header. Required if you're behind a load balancer. Without it, `req.ip` is the load balancer's IP, not the client's.

### The Middleware

```js
async function rateLimitMiddleware(req, res, next) {
  try {
    const key = req.ip;
    await rateLimiter.consume(key, 1);
    next();
  } catch (err) {
    req.log.warn({ ip: req.ip }, 'rate limit exceeded');
    res.set('Retry-After', '60');
    res.status(429).json({ error: 'Too Many Requests', code: 'RATE_LIMIT' });
  }
}

app.use(rateLimitMiddleware);
```

- `req.ip` is the client IP (with `trust proxy` set)
- `rateLimiter.consume(key, 1)` tries to consume 1 token
- On success, `next()` (proceed to the route)
- On failure, log, set `Retry-After`, return 429

### Where to apply

`app.use(rateLimitMiddleware)` applies the limiter to all routes. This is the safest default. For per-endpoint limits, you'd add the middleware to specific routes.

### Per-endpoint limits (optional)

```js
const loginRateLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'rl:login',
  points: 5,
  duration: 60,
});

app.post('/sessions', loginRateLimiterMiddleware, validate(...), asyncHandler(...));

async function loginRateLimiterMiddleware(req, res, next) {
  try {
    await loginRateLimiter.consume(req.ip, 1);
    next();
  } catch (err) {
    res.status(429).json({ error: 'Too many login attempts' });
  }
}
```

A stricter limit on login. 5 attempts per minute per IP. Prevents brute-force.

## Run It

```bash
# Start Redis
redis-server

# Start the server
node server.js

# Make 100 requests (all should succeed)
for i in {1..100}; do curl -s http://localhost:3000/ > /dev/null; done
# All 200 OK

# 101st request fails
curl -i http://localhost:3000/
# HTTP/1.1 429 Too Many Requests
# Retry-After: 60
# {"error":"Too Many Requests","code":"RATE_LIMIT"}

# Wait 60 seconds, try again
sleep 60
curl -i http://localhost:3000/
# HTTP/1.1 200 OK
```

The rate limiter works. The first 100 requests succeed. The 101st is rejected. After 60 seconds, the bucket refills.

---

## Experiments

### Experiment 1: Inspect the rate limit in Redis

```bash
redis-cli keys 'rl:*'
# 1) "rl:127.0.0.1"
```

The key is `rl:127.0.0.1` (the IP). The value is the count.

### Experiment 2: Set a stricter limit

```js
const rateLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'rl',
  points: 5, // 5 requests
  duration: 60, // per 60 seconds
});
```

Now 5 requests per minute. Much stricter.

### Experiment 3: Per-endpoint limit

Add a separate limiter for `/sessions` with 5 per minute. Login attempts are throttled.

### Experiment 4: Different limits for different user roles

Authenticated users get a higher limit (e.g., 1000 per minute). Anonymous users get a lower limit (e.g., 10 per minute). You can use the JWT to determine the user role.

### Experiment 5: Reset the rate limit for a specific IP

```js
await rateLimiter.delete(req.ip);
```

Useful for support cases: "I was throttled, please unblock me."

---

## Summary

You now have rate limiting. The API is protected from abuse. Abusive clients are throttled. Legitimate users are unaffected.

This is the foundation of *abuse prevention*. From here, every production API has rate limiting. The patterns (token bucket, Redis store, per-IP / per-user) are universal.

In project 25, we will add cron jobs. We will run scheduled tasks (session cleanup, daily digest, scheduled posts).

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

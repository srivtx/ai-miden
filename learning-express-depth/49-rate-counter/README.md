# 49 — Rate Counter

**New concept:** count requests per time window. Different from rate limiting — this just observes, doesn't block.

Useful for:
- Analytics: which endpoints are most popular
- Capacity planning: which endpoints need more resources
- Detecting abuse: which clients are making lots of requests

## Run it

```bash
npm install
node server.js
```

```bash
# Make some requests
curl http://localhost:3000/api/users
curl http://localhost:3000/api/users
curl http://localhost:3000/api/users
curl http://localhost:3000/api/orders

# See the counts
curl http://localhost:3000/admin/stats
# { "GET /api/users": { "count": 3, "windowAge": "5.2s" }, "GET /api/orders": { "count": 1, "windowAge": "5.2s" } }

# Reset
curl -X POST http://localhost:3000/admin/reset
```

## How to think about it

The middleware approach: every request passes through a function that increments a counter. The function runs before the route handler. This is the same pattern as logging or rate limiting — middleware that runs on every request.

## How to build it (line by line)

```js
app.use((req, res, next) => {
  const key = req.method + ' ' + req.path;
  // ... increment counter ...
  next();
});
```

**Lines 14-27.** Middleware that runs on every request. It increments a counter keyed by method + path.

**`app.use` without a path** — runs for every request.

```js
const c = counters.get(key);
if (now - c.windowStart > WINDOW_MS) {
  c.count = 0;
  c.windowStart = now;
}
c.count += 1;
```

**Lines 21-26.** Reset the counter if the window has passed. Otherwise, increment.

## What we learned

1. Middleware runs on every request
2. We can track counts per route
3. Sliding window: reset every N seconds
4. This is how Prometheus, DataDog, etc. work
5. For multi-server, store counters in Redis

## What's next

In **50-jwt-auth** we add authentication with JSON Web Tokens.

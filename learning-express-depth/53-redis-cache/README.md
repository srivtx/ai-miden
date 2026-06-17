# 53 — Redis Cache

**New concept:** external cache (Redis).

We built an in-memory cache in project 48. That works for one server. But what if you have 10 servers? Each one has its own cache. They get out of sync.

Redis is a separate service that all your servers can talk to. The cache is shared.

## Setup (requires Redis)

```bash
# Install Redis
brew install redis   # macOS
# or apt install redis  # Linux
# or run via Docker: docker run -p 6379:6379 redis

# Start Redis
redis-server

# Then in another terminal:
npm install
node server.js
```

## Try it

```bash
# First request: cache miss
curl http://localhost:3000/products/1
# { "data": { "id": 1, "name": "Laptop", "price": 999 }, "cached": false }
# Server logs: [db] Loading product 1

# Second request: cache hit
curl http://localhost:3000/products/1
# { "data": {...}, "cached": true }

# Invalidate
curl -X DELETE http://localhost:3000/cache/product/1
# Next request is a cache miss again

# See all cached products
curl http://localhost:3000/admin/cache
```

## How to think about it

In-memory cache = your desk. Fast, but only you can use it. When you leave, it's gone.
Redis = a shared filing cabinet. Slower than your desk, but everyone can access it, and it survives your shift.

## How to build it (line by line)

```js
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
```

**Line 9.** Connect to Redis. `ioredis` is a popular client.

**`process.env.REDIS_URL`** — usually set in production. The `||` provides a default for dev.

```js
async function getWithCache(key, fetchFn, ttlSeconds = 60) {
  const cached = await redis.get(key);
  if (cached) return { data: JSON.parse(cached), cached: true };

  const data = await fetchFn();
  await redis.setex(key, ttlSeconds, JSON.stringify(data));
  return { data, cached: false };
}
```

**Lines 12-19.** The same cache-aside pattern as project 48, but using Redis.

**`redis.get(key)`** — get the value (or null if not in cache).

**`redis.setex(key, ttl, value)`** — set with expiration. The `ex` means "expire after N seconds."

```js
const result = await getWithCache(
  `product:${req.params.id}`,
  () => products[req.params.id],  // The "fetch" function
  300
);
```

**Lines 25-29.** Use the helper. Pass the cache key, a function to fetch the data, and the TTL.

## What we learned

1. Redis is a fast in-memory store that persists
2. Multiple servers can share a Redis cache
3. The pattern is the same as in-memory cache, just the storage is different
4. `setex` sets a value with an expiration
5. Real systems always use Redis or similar for caching

## What's next

In **54-graphql** we build a GraphQL API (different from REST).

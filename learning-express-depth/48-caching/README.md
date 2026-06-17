# 48 — Caching

**New concept:** cache-aside. Some data is expensive to fetch (database query, API call, computation). Cache the result. Next time, serve from cache.

## Run it

```bash
npm install
node server.js
```

```bash
# First request: slow (cache miss)
time curl http://localhost:3000/items/foo
# { "key": "foo", "value": "value for foo", "cached": false }
# real    0m0.518s

# Second request: fast (cache hit)
time curl http://localhost:3000/items/foo
# { "key": "foo", "value": "value for foo", "cached": true }
# real    0m0.005s

# Manually invalidate
curl -X DELETE http://localhost:3000/cache/foo
# Next request will be slow again (cache miss)
```

## How to think about it

When you visit a webpage, the browser caches images, CSS, JS. Next visit, the browser doesn't re-download them. The web would be unbearably slow without caching.

Same idea on the server. If 1000 users all ask for the same product, don't hit the database 1000 times. Hit it once, cache the result, serve from cache.

## How to build it (line by line)

```js
const cache = new Map();  // key -> { data, expiresAt }
```

**Line 14.** A simple in-memory cache. Real systems use Redis (works across multiple servers).

```js
async function getWithCache(key) {
  const cached = cache.get(key);
  if (cached && cached.expiresAt > Date.now()) {
    return { ...cached.data, cached: true };
  }
  // Cache miss
  const data = await slowQuery(key);
  cache.set(key, { data, expiresAt: Date.now() + 60 * 1000 });
  return { ...data, cached: false };
}
```

**Lines 17-27.** The cache-aside pattern:
1. Check the cache. If hit (and not expired), return it.
2. If miss, query the slow source.
3. Store the result in the cache with a TTL.
4. Return the data.

**TTL (Time To Live)** — how long the cache entry is valid. After that, it's considered stale and we re-query.

**`expiresAt > Date.now()`** — is the entry still valid? If not, treat as a miss.

## What we learned

1. Cache-aside: check cache first, fall back to source
2. TTL: how long to keep the data
3. Cache invalidation: delete the entry when the data changes
4. Real systems: Redis, Memcached, Varnish
5. Cache hit = fast, cache miss = slow

## What's next

In **49-rate-counter** we count requests per endpoint, useful for analytics.

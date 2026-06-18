# The Thought

> *"A cache is a Map with a TTL. Check the map first. If miss, query the database, store the result, return."*

## The Cache as a Map

The simplest cache is a `Map<string, value>`. To cache a result:

```js
const cache = new Map();

cache.set('post:42', { id: 42, title: 'Hello' });
const post = cache.get('post:42'); // { id: 42, title: 'Hello' }
```

That's it. `get` and `set`. O(1) lookup. The data is in memory, not on disk. The access time is microseconds.

## Adding TTL

A pure `Map` cache has a problem: the data never expires. If the underlying data changes, the cache is stale. Forever.

The solution: add an **expiration time** to each entry. When you `set`, record `expiresAt = now + ttl`. When you `get`, check if `now > expiresAt`. If yes, delete the entry and return `undefined`.

```js
class Cache {
  constructor(ttlMs = 60 * 1000) {
    this.store = new Map();
    this.ttl = ttlMs;
  }

  get(key) {
    const entry = this.store.get(key);
    if (!entry) return undefined;
    if (Date.now() > entry.expiresAt) {
      this.store.delete(key);
      return undefined;
    }
    return entry.value;
  }

  set(key, value, ttlMs) {
    const expiresAt = Date.now() + (ttlMs || this.ttl);
    this.store.set(key, { value, expiresAt });
  }

  delete(key) {
    this.store.delete(key);
  }
}
```

This is the standard pattern. Most cache libraries do something similar.

## Cache Key Design

The cache key is what identifies the cached value. For `GET /posts/:id`, the key is `post:42` (the resource and the ID). For `GET /users/:id`, the key is `user:42`.

The key should be:
- Unique per request (different IDs, different keys)
- Deterministic (same request, same key)
- Short (less memory)

A good pattern: `${resource}:${id}`. For list endpoints, you'd include the query parameters: `posts:limit=20&offset=0`.

## The Cache-Aside Pattern

The standard pattern for caching is **cache-aside**:

1. Check the cache for the key
2. If hit, return the cached value
3. If miss, query the database
4. Store the result in the cache
5. Return the result

The code:

```js
async function getPost(id) {
  const key = `post:${id}`;
  const cached = cache.get(key);
  if (cached) return cached;

  const post = await db('posts').where({ id }).first();
  if (!post) return null;

  cache.set(key, post);
  return post;
}
```

This is the simplest caching pattern. The application code does the cache check, the database query, and the cache write. The cache is *alongside* the database, not in front of it.

## Cache Invalidation on Write

When the data is written (PATCH, DELETE), the cache must be invalidated. Otherwise, the cache serves stale data forever.

```js
async function updatePost(id, updates) {
  const post = await db('posts').where({ id }).update(updates);
  cache.delete(`post:${id}`); // invalidate
  return post;
}
```

After the write, we delete the cache entry. The next read will re-query the database and re-populate the cache.

This is called **write-through invalidation**: every write invalidates the cache. The next read re-populates it.

## Common Confusions (read these)

**Confusion 1: "Why not just update the cache directly?"**
You can. But it's a race condition: what if two requests update the same data at the same time? Invalidation is simpler: delete the cache, let the next read re-populate it. The race is on the database, where it's handled by the database's concurrency control.

**Confusion 2: "Why a TTL? Just delete on write."**
TTL is a safety net. If you forget to invalidate (or the invalidation fails), the cache will eventually expire. Without TTL, stale data lives forever.

**Confusion 3: "Why not cache everything?"**
Memory. Each cache entry takes memory. For 1M users, the cache could be GBs. We only cache what's read often. For write-heavy data, the cache is often wrong.

**Confusion 4: "What about the cache stampede?"**
When a popular key expires, 1000 requests hit the database at once. The mitigation: lock the cache during re-population, or use a stale-while-revalidate pattern. Out of scope.

**Confusion 5: "What about negative caching?"**
A 404 result. We don't cache it. A malicious client could fill the cache with 404s. We accept this.

**Confusion 6: "What about cache size?"**
Our cache is unbounded. For a long-running server, it could grow. The mitigation: an LRU eviction policy. We don't add this.

**Confusion 7: "What if the cache and the database disagree?"**
They can. The TTL bounds the disagreement. After TTL, the cache is re-populated from the database. Stale data is at most TTL old.

**Confusion 8: "What about multi-process?"**
Each process has its own cache. A write on process 1 doesn't invalidate the cache on process 2. The mitigation: Redis (project 23), which is shared.

## What We Are About to Build

A ~400-line Express app that:

1. Has a `Cache` class with TTL
2. Caches `GET /posts/:id` and `GET /users/:id`
3. Invalidates the cache on PATCH and DELETE
4. Has a default TTL of 1 minute
5. Logs cache hits and misses (so we can see the effect)

The handlers are slightly different. They check the cache first, query the database on miss, and store the result.

In [BUILD.md](./BUILD.md) we will go line by line.

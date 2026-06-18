# Project 22: The Cache

> *"Don't hit the database for the same data 1000 times. Hit it once, then hit memory."*

In project 19, the `GET /posts/:id` handler queries the database every time. For a popular post, this is 1000 queries per second. The database is the bottleneck.

This project adds **caching**. We cache the result of a database query in memory. The next request gets the cached result, no database hit. The cache has a **TTL** (Time To Live) so the data eventually expires and we re-query.

We use a simple in-memory `Map` with a TTL. No external dependencies. For multi-process / multi-region caching, we'd use Redis (project 23).

By the end, popular queries are O(1) instead of O(log n). The database load drops.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why hit the database for the same data? What is a cache?
2. [The Thought](./THOUGHT.md) — How does a cache work? What is TTL? What is cache invalidation?
3. [The Build](./BUILD.md) — Line-by-line construction of the cache
4. [The Decisions](./DECISIONS.md) — Why in-memory? Why a Map? Why TTL?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A cache is a *fast* storage layer in front of a *slow* storage layer. We check the cache first. If the data is there, we return it. If not, we query the database, store the result in the cache, and return it. The cache has a TTL so stale data eventually expires. For popular data, the cache hit rate is high. The database load is low.

---

## The Code

```js
// Simple in-memory cache with TTL
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

  clear() {
    this.store.clear();
  }
}

const cache = new Cache(60 * 1000); // 1 minute default TTL

// In the handler
app.get('/posts/:id', asyncHandler(async (req, res) => {
  const cacheKey = `post:${req.params.id}`;
  const cached = cache.get(cacheKey);
  if (cached) {
    return res.json(cached);
  }

  const post = await db('posts')
    .join('users', 'posts.user_id', 'users.id')
    .select('posts.*', 'users.username as author')
    .where('posts.id', req.params.id)
    .first();
  if (!post) {
    throw new NotFoundError('Post not found');
  }

  cache.set(cacheKey, post);
  res.json(post);
}));
```

The pain of "the database is on fire" is solved. Popular queries hit the cache. The database load drops.

---

## What You Will Have Learned

- What a cache is (a fast storage layer in front of a slow one)
- The `get`, `set`, `delete` operations
- TTL (Time To Live) and why it's needed
- Cache invalidation (the hard problem)
- Why we cache read-heavy data
- Why we don't cache write-heavy data

These are the foundations of *caching*. From here, every project that reads from the database can be cached.

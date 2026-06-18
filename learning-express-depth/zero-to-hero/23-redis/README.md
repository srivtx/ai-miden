# Project 23: The Redis Switch

> *"A cache in memory is fast. A cache shared across processes is faster."*

In project 22, our cache is in memory. Each process has its own cache. A write on process 1 doesn't invalidate the cache on process 2. The cache is not shared.

This project switches the cache to **Redis** — an in-memory data store that's shared across processes. Redis is fast (sub-millisecond), persistent (optional), and has built-in TTL, pub/sub, sorted sets, and more.

We use `ioredis` — the de-facto Redis client for Node. We replace our `Cache` class with a Redis-backed implementation. The API is the same (`get`, `set`, `delete`). The implementation is different.

By the end, the cache is shared. A write on any process invalidates the cache for all processes. Multi-process caching just works.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is in-memory not enough? What is Redis?
2. [The Thought](./THOUGHT.md) — How does Redis work? What is pub/sub? What is sorted set?
3. [The Build](./BUILD.md) — Line-by-line construction of the Redis cache
4. [The Decisions](./DECISIONS.md) — Why Redis? Why not Memcached? Why ioredis?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Redis is an in-memory data store. It supports strings, hashes, lists, sets, sorted sets, with TTL, pub/sub, transactions, and Lua scripting. We use it as a shared cache. `ioredis` is the Node client. We replace our `Cache` class with one that uses `redis.get`, `redis.set`, `redis.del`. The API is the same; the backend is shared. Optionally, we use Redis pub/sub for cache invalidation: when a process writes, it publishes an invalidation message; all processes (including itself) subscribe and invalidate.

---

## The Code

```bash
npm install ioredis
```

```js
const Redis = require('ioredis');

const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT) || 6379,
});

redis.on('error', (err) => logger.error({ err }, 'Redis error'));
redis.on('connect', () => logger.info('Connected to Redis'));

class Cache {
  constructor(redis, ttlSeconds = 60) {
    this.redis = redis;
    this.ttl = ttlSeconds;
  }

  async get(key) {
    const value = await this.redis.get(key);
    return value ? JSON.parse(value) : undefined;
  }

  async set(key, value, ttlSeconds) {
    const ttl = ttlSeconds || this.ttl;
    await this.redis.set(key, JSON.stringify(value), 'EX', ttl);
  }

  async delete(key) {
    await this.redis.del(key);
  }
}

const cache = new Cache(redis, 60);

// In the handler (now async)
app.get('/posts/:id', asyncHandler(async (req, res) => {
  const cacheKey = `post:${req.params.id}`;
  const cached = await cache.get(cacheKey);
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

  await cache.set(cacheKey, post);
  res.json(post);
}));
```

The pain of "the cache is not shared" is solved. All processes see the same cache. Invalidation is consistent.

---

## What You Will Have Learned

- What Redis is (in-memory data store)
- The data types: strings, hashes, lists, sets, sorted sets
- The TTL feature (`SET key value EX seconds`)
- The `ioredis` client
- How to use Redis as a shared cache
- Optional: pub/sub for cache invalidation across processes

These are the foundations of *distributed caching*. From here, every project that needs shared state can use Redis.

# The Thought

> *"Redis is an in-memory data store on a separate server. All your processes connect to it. The cache is shared."*

## What Redis Is

Redis (REmote DIctionary Server) is an in-memory data store. It runs as a separate service. It supports:

- **Strings** — key-value pairs
- **Hashes** — field-value pairs within a key
- **Lists** — ordered collections
- **Sets** — unordered collections of unique values
- **Sorted sets** — sets with a score
- **TTL** — automatic expiration
- **Pub/sub** — publish/subscribe messaging
- **Transactions** — atomic multi-command execution
- **Lua scripting** — server-side scripting

For our purposes, we use Redis as a **shared cache**. We store JSON-serialized values with TTL. All processes connect to the same Redis. The cache is shared.

## Redis as a Cache

The basic operations:

```js
// Set a value with TTL
redis.set('post:42', JSON.stringify(post), 'EX', 60); // expires in 60 seconds

// Get a value
const value = await redis.get('post:42');
const post = value ? JSON.parse(value) : null;

// Delete a value
await redis.del('post:42');
```

The `EX` argument sets the TTL in seconds. After 60 seconds, the key is automatically deleted.

## ioredis

`ioredis` is the de-facto Redis client for Node. It supports:

- Promises (async/await)
- Pipelines (batching commands)
- Transactions (MULTI/EXEC)
- Pub/sub
- Cluster
- Sentinel

The basic usage:

```js
const Redis = require('ioredis');
const redis = new Redis({ host: 'localhost', port: 6379 });

await redis.set('key', 'value', 'EX', 60);
const value = await redis.get('key');
await redis.del('key');
```

## Async API

Redis is async. The `get`, `set`, `del` methods return Promises. Our cache must be async.

```js
class Cache {
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
```

The handlers must be async (they already are).

## JSON Serialization

Redis stores strings. We want to store objects. We use `JSON.stringify` and `JSON.parse`:

```js
await redis.set('post:42', JSON.stringify(post));
const value = await redis.get('post:42');
const post = JSON.parse(value);
```

This works for any JSON-serializable value. For binary data, you'd use Buffers.

## Pub/Sub for Invalidation (Optional)

If you have multiple processes, a write on process 1 should invalidate the cache on processes 2, 3, etc. We can use Redis pub/sub for this:

```js
const subscriber = new Redis(...);
const publisher = new Redis(...);

subscriber.subscribe('cache:invalidate');
subscriber.on('message', (channel, key) => {
  cache.delete(key);
});

// On write, publish
async function invalidate(key) {
  await cache.delete(key);
  await publisher.publish('cache:invalidate', key);
}
```

Every process subscribes to `cache:invalidate`. When a process writes, it publishes the key. All subscribers (including itself) delete the key.

This is more complex but more correct. For this project, we don't add pub/sub. We accept the TTL-based staleness (60 seconds). In a future project, we add pub/sub.

## Common Confusions (read these)

**Confusion 1: "Why Redis and not Memcached?"**
Memcached is similar but simpler. It doesn't have data types beyond strings, no TTL granularity, no pub/sub. Redis is more featureful. We use Redis.

**Confusion 2: "Why not just use Postgres as a cache?"**
Postgres is on disk (or in memory with caching, but it's not designed for it). Redis is in-memory by design. Sub-millisecond latency.

**Confusion 3: "What if Redis is down?"**
The cache misses. The handler queries the database. The system works, just slower. We log the error.

**Confusion 4: "What about cache stampede?"**
Same as project 22. When a popular key expires, 1000 requests hit the database at once.

**Confusion 5: "Why ioredis and not node-redis?"**
Both are good. `ioredis` has a more modern API (Promise-first) and better TypeScript support. We use ioredis.

**Confusion 6: "What about Redis Cluster?"**
A single Redis instance has limits (memory, throughput). For scale, use Redis Cluster (sharded across multiple instances). Out of scope.

**Confusion 7: "What about persistence?"**
Redis can save to disk (RDB snapshots, AOF logs). For a cache, we don't need persistence (cache loss is acceptable). For other use cases (sessions, queues), you'd enable persistence.

**Confusion 8: "What about security?"**
Redis has no auth by default. For production, set a password and use TLS. Out of scope.

## What We Are About to Build

A ~400-line Express app that:

1. Uses `ioredis` to connect to Redis
2. Has a `Cache` class backed by Redis
3. The same cache-aside pattern in handlers
4. The same invalidation in PATCH/DELETE
5. Handles Redis errors gracefully (cache misses on error)

The handlers are slightly different (they `await` the cache). The behavior is the same.

In [BUILD.md](./BUILD.md) we will go line by line.

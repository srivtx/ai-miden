# The Decisions

> *"Redis is the shared cache. All processes see the same data. The database load is reduced."*

## Decision 1: Redis and not Memcached

**Alternative**: Memcached.

**Why Redis: It's more featureful. TTL granularity. Data types. Pub/sub. Transactions. Lua scripting. For our use case, Redis is the standard.

**Trade-off**: Memcached is simpler and slightly faster for pure key-value. We use Redis for the features.

## Decision 2: ioredis and not node-redis

**Alternative**: node-redis (the official client).

**Why ioredis: Better API. Promise-first. Better TypeScript support. More features (cluster, sentinel). It's the de-facto standard in 2024-2026.

**Trade-off**: Slightly heavier than node-redis. We accept it.

## Decision 3: Fail open on Redis errors

**Alternative**: Fail closed (return 503 if Redis is down).

**Why fail open: The system continues to work when Redis is down. The cache just misses. The database load increases, but the system is available.

**Trade-off**: A Redis outage causes high database load. We accept this for availability.

## Decision 4: No pub/sub for invalidation

**Alternative**: Use Redis pub/sub to invalidate the cache across processes.

**Why not: Adds complexity. We accept the TTL-based staleness (60 seconds). For correctness, we'd add pub/sub. For now, TTL is enough.

**Trade-off**: A write on process 1 doesn't invalidate the cache on processes 2-N until they hit the cache (TTL) or until they read the same key. We accept this.

## Decision 5: No Redis Cluster

**Alternative**: Use Redis Cluster (sharded across multiple instances).

**Why not: A single Redis instance is enough for our scale. Cluster is for thousands of requests per second.

**Trade-off**: A single Redis is a single point of failure. For production, you'd add a replica (read-only) or a Sentinel setup.

## Decision 6: No persistence

**Alternative**: Configure Redis to save to disk (RDB, AOF).

**Why not: For a cache, persistence is optional. Cache loss is acceptable. The system re-populates from the database.

**Trade-off**: A Redis restart loses the cache. We accept this.

## Decision 7: JSON serialization

**Alternative**: Use a binary format (MessagePack, Protocol Buffers).

**Why JSON: Simple. Standard. Readable. For most apps, JSON is fine.

**Trade-off**: JSON is larger than binary formats. For high-throughput apps, you'd use binary.

## Decision 8: No connection pooling tweaks

**Alternative**: Configure ioredis with specific pool settings.

**Why not: ioredis handles this automatically. For our scale, defaults are fine.

**Trade-off**: None.

## Decision 9: Single Redis instance

**Alternative**: Multiple Redis instances for read/write splitting.

**Why not: A single instance is enough. For scale, add replicas.

**Trade-off**: A single instance is a bottleneck. Acceptable for our scale.

## Decision 10: Same Cache API

**Alternative**: Rewrite the handlers to use Redis directly.

**Why not: The Cache class abstracts the backend. We could swap to Memcached or another store without changing the handlers.

**Trade-off**: Slight indirection. We accept it for flexibility.

---

## What We Did Not Decide

- **Redis Cluster** — out of scope
- **Redis persistence** — out of scope
- **Pub/sub for invalidation** — out of scope
- **Fail closed** — out of scope
- **Connection pooling** — out of scope
- **Binary serialization** — out of scope
- **TLS / auth** — out of scope (production concern)
- **Sentinel** — out of scope
- **Multi-region Redis** — out of scope
- **Redis as a queue** — out of scope (project 26)

Each is a future decision.

---

## The Meta-Decision: The Cache Is Shared

For 22 projects, our cache was in memory. Each process had its own. A write on one process didn't invalidate the cache on others. The system worked for single-process; multi-process was chaos.

Now the cache is shared. All processes connect to the same Redis. A write on any process invalidates the cache for all (via TTL). Multi-process / multi-region works.

This is the foundation of *distributed systems*. Shared state via Redis. Pub/sub for events. Sorted sets for leaderboards. Streams for queues. Sets for tags. The data types are tools. We use them.

The next 17 projects will assume Redis exists (when needed). The path diverges:

- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request (using BullMQ on Redis)
- **Transactions** (project 27): atomic multi-write operations
- **WebSocket** (project 28): bidirectional channel
- **SSE** (project 29): server-push
- **Presence** (project 30): who's online (using Redis pub/sub)
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The cache is shared. The path continues.

# The Problem

> *"A cache in memory is fast. A cache in memory on every process is chaos."*

## Why In-Memory Cache Is Not Enough

In project 22, our cache is a `Map` in the Node process. This works for a single process. But:

1. **Multi-process**: If you run 3 server processes (e.g., behind a load balancer), each has its own `Map`. A write on process 1 doesn't invalidate the cache on process 2 or 3. Users on process 2 and 3 see stale data.

2. **Multi-region**: If you have servers in the US and EU, the US cache doesn't see writes from EU and vice versa. Users see stale data.

3. **Restart**: Restart the process, the cache is empty. The first request after restart is a miss for everything. The database gets a thundering herd.

4. **Memory limits**: Each process has its own memory. A 1 GB cache on each of 10 processes = 10 GB of memory used (with high duplication).

## What Pain Is This Solving?

Imagine you have 10 server processes. A user updates their profile on process 1. The write hits the database. Process 1 invalidates its cache. But processes 2-10 still have the old profile in their cache. Users on those processes see stale data for up to 60 seconds (the TTL).

**The fix**: a shared cache. All processes read from and write to the same cache. A write on any process invalidates the cache for all processes.

This is **Redis**. An in-memory data store that runs as a separate service. All your processes connect to the same Redis. The cache is shared.

## The Deeper Problem: Distributed State

An in-memory cache is local. A shared cache is distributed. The fundamental difference:

- **Local cache**: each process has its own state. No coordination needed.
- **Distributed cache**: all processes share state. Coordination is required.

Coordination is the hard part. With Redis, we get coordination out of the box (Redis is a single source of truth). With pub/sub, we can also broadcast invalidation events to all subscribers.

## What This Project Will Solve

This project will:

1. Add `ioredis` as a dependency
2. Replace the in-memory `Map` cache with a Redis-backed cache
3. Keep the same `Cache` API (`get`, `set`, `delete`)
4. Make the cache async (Redis is async)
5. Optionally, use Redis pub/sub for cache invalidation

By the end, the cache is shared. Multi-process / multi-region works. The database load is reduced.

## What This Project Will *Not* Solve

- **Redis cluster / sharding** — we use a single Redis instance. For scale, use Redis Cluster.
- **Redis persistence** — we use Redis in-memory. For persistence, configure Redis to save to disk.
- **Cache stampede** — same as project 22.
- **Negative caching** — same as project 22.
- **Multi-level cache** — same as project 22.

## The Question This Project Answers

> *"How do I share cache state across multiple processes?"*

If you can answer: "use Redis as a shared in-memory store, all processes connect to the same Redis, the cache is shared," you are ready for project 24.

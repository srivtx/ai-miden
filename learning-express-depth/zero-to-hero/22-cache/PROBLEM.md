# The Problem

> *"A query takes 5ms. 1000 queries take 5 seconds. Caching turns 1000 queries into 1."*

## Why Caching Is Essential

In project 19, every `GET /posts/:id` query goes to the database. For a popular post with 1000 requests per second, that's 1000 database queries per second. The database has to:

- Parse the query
- Look up the index
- Read the row
- Return the data

Each query takes 1-5ms. 1000 queries take 1-5 seconds (concurrently). The database is the bottleneck.

But here's the thing: the data is the same every time. The post doesn't change between requests. We're querying for the same data over and over.

**The solution**: cache the result. The first request queries the database. The next 999 requests get the cached result. The database is hit once. The cache serves the rest.

## What Pain Is This Solving?

Imagine you have a viral post. 100,000 people view it. Without caching, the database serves 100,000 identical queries. With caching, the database serves 1 query, and the cache serves 99,999.

The cost reduction is dramatic:

- Without cache: 100,000 × 5ms = 500,000ms of database time
- With cache: 1 × 5ms + 99,999 × 0.1ms = 10,005ms of total time
- **Speedup: 50x**

For high-traffic apps, caching is non-negotiable.

## The Deeper Problem: Cache Invalidation

The hard part of caching is **invalidation**: when the underlying data changes, how do you update the cache?

There are several strategies:

1. **TTL (Time To Live)** — the cache entry expires after a fixed time. After expiration, the next request re-queries the database.
2. **Write-through** — when the data is written, the cache is also updated.
3. **Write-behind** — the data is written to the cache; the cache asynchronously writes to the database.
4. **Event-based** — the data source emits events; the cache listens and updates.

For this project, we use TTL. It's the simplest. It's not perfect (data can be stale for up to TTL), but it's predictable.

For correctness, you'd use write-through. The cache is updated whenever the data is written. We add this in a future project.

## What This Project Will Solve

This project will:

1. Add a `Cache` class with TTL
2. Cache `GET /posts/:id` and `GET /users/:id` (read-heavy)
3. Invalidate the cache on `PATCH` and `DELETE` (write-through)
4. Set a default TTL of 1 minute

By the end, popular reads hit the cache. Writes update the cache. The database load drops.

## What This Project Will *Not* Solve

- **Multi-process caching** — we cache in memory. Each process has its own cache. For shared caching, use Redis (project 23).
- **Cache stampede** — when a popular key expires, 1000 requests hit the database at once. We accept this for now.
- **Negative caching** — we don't cache 404s. A malicious client could request 1000 different missing IDs and fill the cache. We accept this.
- **Cache size limit** — our cache is unbounded. For a long-running server, it could grow indefinitely. We accept this.
- **Cache analytics** — we don't track hit rate, miss rate, etc. We accept this.

## The Question This Project Answers

> *"How do I serve the same data 1000 times without hitting the database 1000 times?"*

If you can answer: "cache the result in memory with a TTL, check the cache first, query the database on miss," you are ready for project 23.

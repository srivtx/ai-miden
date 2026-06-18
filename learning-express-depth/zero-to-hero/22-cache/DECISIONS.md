# The Decisions

> *"A cache is a Map with a TTL. Check the map first. If miss, query, store, return."*

## Decision 1: In-memory cache, not Redis

**Alternative**: Use Redis from the start.

**Why in-memory: Simpler. No external service. For a single process, this is enough.

**Trade-off**: For multi-process / multi-region, we'd need Redis (project 23). We use in-memory for now and switch in the next project.

## Decision 2: Cache-aside, not write-through

**Alternative**: Write-through — every write updates the cache directly.

**Why cache-aside: Simpler. Less code. The race conditions are on the database, where they're handled.

**Trade-off**: There's a window where the cache is stale (between the write and the next read). The TTL bounds this window.

## Decision 3: Invalidate on write, not update

**Alternative**: Update the cache entry with the new value on write.

**Why invalidate: Simpler. No race conditions. The next read re-populates from the database (the source of truth).

**Trade-off**: The next read after a write is a cache miss. We accept this for simplicity.

## Decision 4: 1-minute TTL

**Alternative**: 1 second, 1 hour, 1 day.

**Why 1 minute: A balance between freshness and hit rate. Longer = more hits, but stale data. Shorter = fresher, but fewer hits.

**Trade-off**: Data can be stale for up to 1 minute. For most apps, this is fine.

## Decision 5: No LRU eviction

**Alternative**: Use an LRU cache (`lru-cache` npm).

**Why no LRU: Out of scope. Our cache is unbounded. For a long-running server, it could grow. We accept this.

**Trade-off**: Memory could grow indefinitely. Add LRU in a future project.

## Decision 6: No cache for list endpoints

**Alternative**: Cache `GET /posts` and `GET /users` too.

**Why no list caching: The query parameters (limit, offset) make the key complex. Each unique query has a unique cache entry. The cache could be large.

**Trade-off**: List endpoints always hit the database. We accept this for now.

## Decision 7: No negative caching

**Alternative**: Cache 404 results.

**Why no: A malicious client could fill the cache with 404s. We accept the risk.

**Trade-off**: Missing IDs cause database queries. We accept this.

## Decision 8: No cache stampede mitigation

**Alternative**: Lock the cache during re-population. Or use stale-while-revalidate.

**Why no: Out of scope. The stampede is rare (when a popular key expires). We accept the risk.

**Trade-off**: A brief spike in database load when a popular key expires. We accept this.

## Decision 9: No analytics

**Alternative**: Track hit rate, miss rate, cache size.

**Why no: Out of scope. The logs are enough for now.

**Trade-off**: We don't have metrics to tune the TTL. We accept this.

## Decision 10: No multi-level cache

**Alternative**: Browser cache, CDN cache, server cache, database cache. Multiple layers.

**Why no: Out of scope. A single server cache is enough for now.

**Trade-off**: We don't benefit from browser or CDN caching. We accept this.

---

## What We Did Not Decide

- **Redis** — out of scope (project 23)
- **LRU eviction** — out of scope
- **Negative caching** — out of scope
- **Cache stampede mitigation** — out of scope
- **Cache analytics** — out of scope
- **Multi-level cache** — out of scope
- **Cache pre-warming** — out of scope
- **Stale-while-revalidate** — out of scope
- **CDN integration** — out of scope
- **Browser cache headers** (ETag, Last-Modified) — out of scope

Each is a future decision.

---

## The Meta-Decision: The API Has a Cache

For 21 projects, every read hit the database. For 1M users, the database was on fire. The user waited.

Now the API has a cache. Popular reads are O(1). The database load is reduced. The user is faster.

This is the foundation of *every* high-traffic app. Caching is non-negotiable. The patterns (cache-aside, TTL, invalidation) are universal.

The next 18 projects will assume caching exists. The path diverges:

- **Redis** (project 23): shared state across processes
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations
- **WebSocket** (project 28): bidirectional channel
- **SSE** (project 29): server-push
- **Presence** (project 30): who's online
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

The API has a cache. The path continues.

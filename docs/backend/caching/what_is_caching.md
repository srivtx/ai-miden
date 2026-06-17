## Why it exists (THE PROBLEM)

Your database is fast for a single query. But the same query, run 1000 times a second, melts the database. The query is: `SELECT * FROM products WHERE category = ?` and it returns the same 100 products every time. 99% of those queries are wasted work.

**Caching** is storing the result of an expensive operation somewhere faster, so the next request gets the result without re-doing the work. The cache is faster (in-memory vs disk), the cache is closer (same process vs across the network), or both.

Three problems caching solves:
1. **Latency**: cache hit = 1ms, cache miss = 100ms. 100x faster.
2. **Load on the database**: 1000 req/s with 99% hit rate = 10 actual DB queries/s. The DB can handle 10 QPS easily.
3. **Cost**: less DB CPU = smaller DB instance = less money.

The trade-off: cache is a copy. If the source of truth changes, the cache is stale. You have to invalidate the cache. "Cache invalidation" is one of the two hard problems in computer science (the other two are naming things and off-by-one errors).

## Definition (very simple)

**Cache hit** = the data is in the cache. Return it. Fast.
**Cache miss** = the data is NOT in the cache. Go to the source (DB), get the data, store it in the cache, return it. Slower.
**Hit rate** = hits / (hits + misses). 95% hit rate = 95% of requests are fast.
**TTL (time-to-live)** = how long the cache entry is valid. After TTL, it's expired. Next read is a miss.
**Cache invalidation** = removing or updating the cache when the source changes.
**Cache stampede** = 1000 requests miss the cache at the same time, all hit the DB. The DB dies. Solution: lock, request coalescing, or pre-warming.

## Real-life analogy

**No cache = a librarian who runs to the warehouse every time you ask for a book.** "Where is the SQL book?" *runs to warehouse* "It's in aisle 42." *runs back* "Aisle 42." You ask again. *runs to warehouse again*. The librarian is exhausted.

**Cache = a librarian who keeps popular books at the desk.** "Where is the SQL book?" "It's right here." No run. After 100 asks, the librarian thinks "this is popular" and keeps it always.

**TTL = a librarian who returns books to the shelf after a week.** "It's been 7 days, I'm putting it back." The book might be updated (newer edition), so the librarian checks next time.

**Cache invalidation = when the librarian gets a new edition of a book.** Old copy goes back to shelf. New copy goes to the desk. Customers see the new edition.

## Tiny numeric example

A query `SELECT * FROM products WHERE category = 'electronics'`:
- DB query: 50ms
- Cache lookup: 0.5ms
- Without cache: 50ms × 1000 req/s = 50 seconds of DB CPU per second → DB dies
- With cache (95% hit rate): 50ms × 50 req/s = 2.5 seconds of DB CPU per second → DB is fine

Cache hit ratio: 95%. DB load: 20x lower. Latency: 100x lower on hits.

## Common confusion (5+ bullet points)

1. **"Cache everything forever."** Memory is finite. Cache everything FOREVER and your cache fills up. Then the cache evicts (LRU, LFU, FIFO). Then the hit rate drops. Pick a TTL based on how often the data changes. Product listings: 5 min. User session: 1 hour. Static config: 24 hours.

2. **"Cache and DB are always in sync."** No. The cache is eventually consistent. If you update the DB without invalidating the cache, the cache returns stale data. Solution: invalidate cache on write, OR write-through (update cache when DB updates).

3. **"In-memory is always faster than Redis."** For a single process, yes. For multi-process or multi-server, no. Each process has its own cache. Invalidation is hard. Redis is shared, so all servers see the same cache. The "in-process" speed win is often lost to "users see different data from different servers."

4. **"I'll cache user-specific data globally."** Don't. User A's profile in the global cache means User B sees User A's data (if cache key is wrong). Cache by user ID: `cache.get('user:42:profile')`. Always include the user ID in the key.

5. **"Cache invalidation is just 'delete the key.'"** Sometimes. But if the cache is for a list ("products in category X"), deleting the key is easy. If the cache is for an aggregate ("user order count"), deleting all keys that might depend on the count is hard. "Delete the right keys" is the hard part.

6. **"The cache is faster, so the read is atomic."** No. Two requests miss the cache, both go to the DB, both store the result. The DB does 2x the work. Solution: lock or "request coalescing" — only one request goes to the DB, the other waits and gets the result.

## Key properties

| Property | In-memory (Map) | Redis | Memcached |
|---|---|---|---|
| Speed | Fastest (no network) | Fast (~0.5ms) | Fast (~0.5ms) |
| Capacity | Limited by RAM | Limited by Redis RAM | Limited by Memcached RAM |
| Shared across servers | No (per-process) | Yes | Yes |
| Persistence | No (lost on restart) | Optional (RDB, AOF) | No |
| Eviction policy | You implement | LRU, LFU, etc. | LRU only |
| Data structures | Whatever | Strings, hashes, lists, sets, sorted sets | Strings only |
| Use | Single-process, dev | Production, multi-server | Simple key-value |

## Cache patterns

**1. Cache-aside (lazy loading)**
```
1. Check cache
2. If miss: read DB, store in cache, return
3. On write: update DB, invalidate cache
```
Most common. Simple. Stale data is possible (DB update without cache invalidation).

**2. Write-through**
```
1. Update DB
2. Update cache (same operation)
```
Always fresh. Slower writes. Cache might have data never read.

**3. Write-behind (write-back)**
```
1. Update cache
2. Async: write to DB
```
Fastest writes. Risk: if the cache dies before writing, data is lost.

**4. Read-through**
```
1. Cache-aside but cache itself knows how to load from DB
```
The cache library handles the miss (calls a loader function).

## Connection to our projects

For our 73 apps, add caching to:
- `GET /products` — cache the list for 5 min
- `GET /products/:id` — cache the product for 5 min
- `GET /user/profile` — cache for 1 hour (invalidate on update)
- `GET /categories` — cache for 24 hours (rarely changes)

The `caching-demo/` project in apps/level1 shows cache-aside with both in-memory (Map) and Redis patterns. For our SQLite-based demos, in-memory Map is fine. For production, use Redis.

For CortexCode: cache the tokenized training data (it's the same for every training run). Cache = Map<string, int[]>. Saves 10 seconds of tokenization per run.

For logogen: cache the model weights (load once, reuse across requests).

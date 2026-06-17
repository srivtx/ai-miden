## Why it exists (THE PROBLEM)

User makes 1000 requests. Each request calls the database: `SELECT * FROM products WHERE id = ?`. The database is fast (5ms) but you pay 5 seconds total. Plus the DB connection pool is exhausted. You can scale the database, but it costs $200/month per replica. Why compute the same answer 1000 times when the answer rarely changes?

**Caching** stores the answer in memory after the first call. Next 999 calls: hit the memory cache in 0.1ms. Same answer. 50× faster. The database sees 1 request, not 1000. Free.

This is the single highest-impact optimization in backend engineering. Twitter, Instagram, GitHub — all cache aggressively. Most queries should be cache hits, not database hits.

## Definition (very simple)

**Cache** = a fast in-memory store of recent results. The handler asks the cache first: "Have I computed this before? Return it. If not, compute it (hit database), store it in the cache, return it."

Three patterns:

### 1. Cache-aside (read-through)
```
Read:  Get from cache. If miss, get from DB, set in cache, return.
Write: Set in DB, INVALIDATE cache (delete the entry).
```

### 2. Write-through
```
Write: Set in DB, set in cache (in one operation).
Read:  Get from cache. If miss, get from DB, set in cache, return.
```

### 3. Write-behind
```
Write: Set in cache. Async worker writes to DB.
Read:  Get from cache. If miss, get from DB, set in cache, return.
```

## Real-life analogy

**Cache = a calculator on your desk.** You have a math problem. You COULD walk to the bookshelf, find your math textbook, look up the formula, do the calculation (5 minutes). OR you check the calculator on your desk (0.1 seconds). The calculator was put there by an earlier calculation. It might be slightly out of date (textbook has new edition), but for most cases it's good enough.

When the textbook changes (database updates), you **throw away** the calculator result (invalidate cache). The next calculation gets a fresh answer.

## Tiny numeric example

Without cache:
```
Request 1:  SELECT count(*) FROM products   → 5ms
Request 2:  SELECT count(*) FROM products   → 5ms
Request 3:  SELECT count(*) FROM products   → 5ms
...
Request 1000: SELECT count(*) FROM products → 5ms
Total: 5000ms of database time
```

With cache:
```
Request 1:  cache miss → SELECT count() from products → 5ms → set cache → return
Request 2:  cache hit → return immediately → 0.1ms
Request 3:  cache hit → return immediately → 0.1ms
...
Request 1000: cache hit → return immediately → 0.1ms
Total: 5ms + 999 × 0.1ms = 105ms
```

**47× speedup.** And the database handles 1 request instead of 1000.

## Common confusion (5+ bullet points)

1. **"Just cache everything forever."** Stale data. A product price changes in the database, but your cache still has the old price for hours. You must invalidate (delete or update) the cache on every write. This is the hardest part of caching — knowing WHEN to invalidate.

2. **"Cache invalidation is one of the two hard problems in computer science."** It's a famous quote (along with naming) because it's true. The pattern: invalidate on EVERY write. Don't try to be clever. Just delete the cache key. The next read repopulates.

3. **"Stale-while-revalidate."** When you read, if cache exists return it (might be slightly stale). In the background, refresh the cache for next time. Users get speed. Data is eventually consistent. This is what CDN cache headers do (`Cache-Control: max-age=3600, stale-while-revalidate=86400`).

4. **"Cache stampede."** Cache expires. 1000 requests arrive simultaneously. All 1000 miss the cache, all 1000 query the database, the database crashes. The pattern: lock the cache. First request that misses acquires a lock, queries the DB, sets the cache. Other 999 requests wait, then read the new value. In Node.js: use `node-cache` or Redis with `SETNX` (set if not exists).

5. **"What's the TTL?"** Time-to-live. After this many seconds, the cache entry expires. Trade-off: short TTL = fresh data, more DB load. Long TTL = stale data, less DB load. Default: 60-300 seconds. Critical data (auth tokens): shorter. Public data (product names): longer.

6. **"Cache size grows forever."** Use LRU eviction (least-recently-used). When cache hits max size, evict the entry that was used longest ago. `node-cache` and Redis do this automatically. Without eviction: out-of-memory crash.

## Key properties

| Property | Without cache | With cache |
|---|---|---|
| Read latency | 5-50ms (DB) | 0.1-1ms (memory) |
| DB load | 100% of reads | 1-10% of reads (cache hit rate) |
| Cost | $200/mo (scale DB) | $0 (memory is cheap) |
| Data freshness | Always | Up to TTL old |
| Complexity | Simple | High (invalidation, stampede) |

## Tech comparison

| Store | Best for | Persistence | Speed |
|---|---|---|---|
| **In-memory Map** | Single server, dev | No (lost on restart) | Fastest |
| **node-cache** | Single server, simple | Optional (disk) | 0.01ms |
| **Redis** | Multiple servers | Yes (RDB snapshots) | 0.5ms |
| **Memcached** | Multi-server cache | No | 0.5ms |
| **CDN (CloudFront)** | Static assets | Yes (edge) | 10ms |

For CortexCode/local: in-memory Map. For production with multiple servers: Redis.

## Connection to our projects

logogen uses in-memory cache for embeddings. cortexcode_api could cache the model output (one of the 80-token completions → don't recompute for the same prompt). Add `Map<key, {value, expiresAt}>` to both. The user-facing effect: identical prompts are 100× faster.

For 73 backend projects: many of them (task-api, blog-platform, ecommerce) could use cache for `/products?category=electronics` (rarely changes), `/users/me` (session data), `/posts/:id` (until edit). Add caching selectively — not for every endpoint, just the hot reads.

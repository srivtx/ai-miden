# 09 — Todo (caching)

Add a cache in front of the database. List endpoints return cached data. Writes invalidate the cache.

**What's new:**
- In-memory cache with TTL (30 seconds)
- `X-Cache: HIT` or `MISS` header tells you if it was cached
- Writes (POST/PATCH/DELETE) invalidate the cache
- `/admin/cache` to inspect

**Why cache?** Most apps read way more than they write. The list endpoint is hit on every page load. We can serve the same data 1000 times in 30 seconds without hitting the DB.

**The invalidation pattern:** on any write, clear the cache. Next read goes to the DB, refills the cache.

## Run
```bash
npm install && node server.js
```

```bash
# First list: cache miss
curl -i http://localhost:3000/todos
# X-Cache: MISS

# Second list: cache hit
curl -i http://localhost:3000/todos
# X-Cache: HIT

# Add a todo (invalidates cache)
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title": "New"}'

# Next list: miss again
curl -i http://localhost:3000/todos
# X-Cache: MISS
```

## What this stage teaches
- Cache-aside pattern
- TTL (time to live)
- Cache invalidation on write
- `X-Cache` header for debugging

## Next
**10-todo-rate-limit** — per-user rate limits. Prevent abuse.

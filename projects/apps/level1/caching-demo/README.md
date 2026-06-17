# Caching — Cache-aside pattern with SQLite backend

A complete cache-aside demo using SQLite as the "slow" source and in-memory Map as the cache.

## Run
```
node server.js
```

## Endpoints
```
GET    /products              List all (cached 60s)
GET    /products/:id          Single product (cached 60s)
POST   /products              Create new (invalidates cache)
PATCH  /products/:id          Update (invalidates specific cache key)
DELETE /products/:id          Delete (invalidates)
GET    /admin/cache           View cache stats
POST   /admin/cache/clear     Clear all cache
```

## What this teaches
1. Cache-aside pattern (read, check cache, miss → DB, set cache)
2. TTL expiration
3. Cache invalidation on write
4. Cache key generation (different per query)
5. Cache statistics (hits, misses, hit rate)
6. Manual cache management endpoints

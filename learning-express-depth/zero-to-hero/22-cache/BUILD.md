# The Build

> *"A cache is a Map with a TTL. Check the map first. If miss, query, store, return."*

We are going to add caching to the read-heavy endpoints. The change from project 21: add a `Cache` class, cache reads, invalidate on writes.

## The Cache Class

```js
class Cache {
  constructor(ttlMs = 60 * 1000) {
    this.store = new Map();
    this.ttl = ttlMs;
  }

  get(key) {
    const entry = this.store.get(key);
    if (!entry) return undefined;
    if (Date.now() > entry.expiresAt) {
      this.store.delete(key);
      return undefined;
    }
    return entry.value;
  }

  set(key, value, ttlMs) {
    const expiresAt = Date.now() + (ttlMs || this.ttl);
    this.store.set(key, { value, expiresAt });
  }

  delete(key) {
    this.store.delete(key);
  }

  clear() {
    this.store.clear();
  }

  size() {
    return this.store.size;
  }
}

const cache = new Cache(60 * 1000); // 1 minute default TTL
```

### The methods

- `get(key)` — return the value if not expired, `undefined` otherwise
- `set(key, value, ttlMs?)` — store the value with TTL
- `delete(key)` — remove the entry
- `clear()` — remove all entries
- `size()` — number of entries

### The TTL

The default TTL is 60 seconds. You can override per call: `cache.set('key', value, 5 * 1000)` for 5 seconds.

## The Cached Handler

```js
app.get('/posts/:id', asyncHandler(async (req, res) => {
  const cacheKey = `post:${req.params.id}`;
  const cached = cache.get(cacheKey);
  if (cached) {
    req.log.debug({ cacheKey }, 'cache hit');
    return res.json(cached);
  }

  req.log.debug({ cacheKey }, 'cache miss');
  const post = await db('posts')
    .join('users', 'posts.user_id', 'users.id')
    .select('posts.*', 'users.username as author')
    .where('posts.id', req.params.id)
    .first();
  if (!post) {
    throw new NotFoundError('Post not found');
  }

  cache.set(cacheKey, post);
  res.json(post);
}));
```

### The flow

1. Build the cache key (`post:42`)
2. Check the cache
3. If hit, return the cached value
4. If miss, query the database
5. Store the result in the cache
6. Return the result

### Logging

We log cache hits and misses. In production, you'd track these metrics (project 39). For now, the logs are enough.

## Invalidation on Write

```js
app.patch('/posts/:id', authMiddleware, validate(postUpdateSchema), asyncHandler(async (req, res) => {
  // ... existing code ...
  await db('posts').where({ id: req.params.id }).update(updates);
  cache.delete(`post:${req.params.id}`); // invalidate
  const updated = await db('posts').where({ id: req.params.id }).first();
  res.json(updated);
}));

app.delete('/posts/:id', authMiddleware, asyncHandler(async (req, res) => {
  // ... existing code ...
  await db('posts').where({ id: req.params.id }).delete();
  cache.delete(`post:${req.params.id}`); // invalidate
  res.status(204).end();
}));
```

After every write, we delete the cache entry. The next read will re-populate.

## Apply to Users

The same pattern for `GET /users/:id`, `PATCH /users/:id`, `DELETE /users/:id`.

```js
app.get('/users/:id', asyncHandler(async (req, res) => {
  const cacheKey = `user:${req.params.id}`;
  const cached = cache.get(cacheKey);
  if (cached) return res.json(cached);

  const user = await db('users').select('id', 'username', 'email', 'created_at').where({ id: req.params.id }).first();
  if (!user) {
    throw new NotFoundError('User not found');
  }

  cache.set(cacheKey, user);
  res.json(user);
}));
```

## Run It

```bash
# First request: cache miss, query the database
curl http://localhost:3000/posts/1
# (log: "cache miss")
# {"id":1,"title":"Hello",...}

# Second request: cache hit, no database query
curl http://localhost:3000/posts/1
# (log: "cache hit")
# {"id":1,"title":"Hello",...}

# Update the post
curl -X PATCH http://localhost:3000/posts/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated"}'
# (log: cache invalidated)

# Next request: cache miss, query the database, see the new title
curl http://localhost:3000/posts/1
# (log: "cache miss")
# {"id":1,"title":"Updated",...}
```

The cache works. Hits are fast. Writes invalidate.

---

## Experiments

### Experiment 1: Set a very short TTL

```js
const cache = new Cache(1000); // 1 second
```

The cache expires every second. You'll see a miss every second.

### Experiment 2: Cache the list endpoint

The list endpoint is harder to cache because the query parameters (limit, offset) make the key complex. We don't cache it here. For caching list endpoints, you'd use a different key strategy.

### Experiment 3: Log cache stats

```js
app.use((req, res, next) => {
  res.on('finish', () => {
    if (req.cacheHit) {
      logger.debug({ url: req.url, size: cache.size() }, 'cache hit');
    }
  });
  next();
});
```

Track cache hits in a more structured way.

### Experiment 4: Add a hit counter

```js
let hits = 0;
let misses = 0;

cache.get = (key) => {
  const v = originalGet(key);
  if (v !== undefined) hits++;
  else misses++;
  return v;
};
```

Track hit rate. Useful for tuning the TTL.

### Experiment 5: Use LRU

For a long-running server with many cache entries, the cache could grow. Use an LRU (Least Recently Used) eviction policy. Libraries: `lru-cache` (npm).

```bash
npm install lru-cache
```

```js
const LRU = require('lru-cache');
const cache = new LRU({ max: 1000, ttl: 60 * 1000 });
```

LRU evicts the least recently used entry when the cache is full.

---

## Summary

You now have caching. Popular reads hit the cache. Writes invalidate the cache. The database load drops.

This is the foundation of *every* high-traffic app. From here, every project that reads from the database can be cached. The patterns (cache-aside, TTL, write-through invalidation) are universal.

In project 23, we will replace the in-memory cache with Redis. The cache will be shared across processes. Multi-process caching, distributed caching, pub/sub for invalidation.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

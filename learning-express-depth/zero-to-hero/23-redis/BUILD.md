# The Build

> *"Redis is an in-memory data store on a separate server. All your processes connect to it."*

We are going to switch the cache from in-memory to Redis. The change from project 22: replace the `Cache` class with a Redis-backed one. The handlers get a small update (they `await` the cache).

## Setup

```bash
# Install Redis
brew install redis
redis-server

# In another terminal, verify it works
redis-cli ping
# PONG

# Install the ioredis client
npm install ioredis
```

## The Code

### Imports

```js
const Redis = require('ioredis');
```

### Connection

```js
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT) || 6379,
  password: process.env.REDIS_PASSWORD,
});

redis.on('error', (err) => logger.error({ err }, 'Redis error'));
redis.on('connect', () => logger.info('Connected to Redis'));
```

`new Redis(...)` creates a client. It connects automatically. The `on('error')` handler logs errors. The `on('connect')` handler logs successful connections.

### The Cache Class

```js
class Cache {
  constructor(redis, ttlSeconds = 60) {
    this.redis = redis;
    this.ttl = ttlSeconds;
  }

  async get(key) {
    try {
      const value = await this.redis.get(key);
      return value ? JSON.parse(value) : undefined;
    } catch (err) {
      logger.error({ err, key }, 'Cache get error');
      return undefined; // fail open: treat as miss
    }
  }

  async set(key, value, ttlSeconds) {
    try {
      const ttl = ttlSeconds || this.ttl;
      await this.redis.set(key, JSON.stringify(value), 'EX', ttl);
    } catch (err) {
      logger.error({ err, key }, 'Cache set error');
    }
  }

  async delete(key) {
    try {
      await this.redis.del(key);
    } catch (err) {
      logger.error({ err, key }, 'Cache delete error');
    }
  }
}

const cache = new Cache(redis, 60);
```

### Fail open

The `try/catch` blocks return `undefined` on error. This is **fail open**: if Redis is down, we treat the cache as a miss and fall through to the database. The system still works, just slower.

This is a deliberate choice. The alternative is **fail closed**: if Redis is down, return 503. That's safer for some apps (e.g., a paid service that requires a cache), but most apps prefer fail open.

### The Handlers

```js
app.get('/posts/:id', asyncHandler(async (req, res) => {
  const cacheKey = `post:${req.params.id}`;
  const cached = await cache.get(cacheKey);
  if (cached) {
    return res.json(cached);
  }

  const post = await db('posts')
    .join('users', 'posts.user_id', 'users.id')
    .select('posts.*', 'users.username as author')
    .where('posts.id', req.params.id)
    .first();
  if (!post) {
    throw new NotFoundError('Post not found');
  }

  await cache.set(cacheKey, post);
  res.json(post);
}));
```

The only changes from project 22:
- `await cache.get(...)` (was synchronous)
- `await cache.set(...)` (was synchronous)

The behavior is the same. The cache is now shared.

### Invalidation

```js
app.patch('/posts/:id', authMiddleware, validate(postUpdateSchema), asyncHandler(async (req, res) => {
  // ... existing code ...
  await db('posts').where({ id: req.params.id }).update(updates);
  await cache.delete(`post:${req.params.id}`); // now async
  const updated = await db('posts').where({ id: req.params.id }).first();
  res.json(updated);
}));
```

`cache.delete` is now `await`ed. Same behavior.

## Run It

```bash
# Start Redis
redis-server

# Start the server
node server.js
# (log: "Connected to Redis")

# Make a request (cache miss, query the database)
curl http://localhost:3000/posts/1
# {"id":1,"title":"Hello",...}

# Make another request (cache hit, no database query)
curl http://localhost:3000/posts/1
# {"id":1,"title":"Hello",...}

# Inspect the cache
redis-cli get post:1
# {"id":1,"title":"Hello",...}

# Update the post
curl -X PATCH http://localhost:3000/posts/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated"}'
# (log: cache invalidated)

# Inspect the cache (should be gone)
redis-cli get post:1
# (empty)
```

The cache is shared. Other processes can see the same data.

---

## Experiments

### Experiment 1: Use redis-cli to inspect

```bash
redis-cli keys '*'
# 1) "post:1"
# 2) "user:1"

redis-cli get post:1
# {"id":1,"title":"Hello",...}

redis-cli ttl post:1
# 47 (seconds until expiration)
```

### Experiment 2: Set a longer TTL

```js
const cache = new Cache(redis, 600); // 10 minutes
```

### Experiment 3: Test fail-open

```bash
# Stop Redis
redis-cli shutdown

# Make a request (cache miss, query the database)
curl http://localhost:3000/posts/1
# (works, but logs the Redis error)
# {"id":1,"title":"Hello",...}

# Start Redis again
redis-server
```

The system continues to work when Redis is down. The cache just misses.

### Experiment 4: Pub/sub for cross-process invalidation

```js
const subscriber = redis.duplicate();
subscriber.subscribe('cache:invalidate');
subscriber.on('message', (channel, key) => {
  cache.delete(key);
  logger.info({ key }, 'Cache invalidated via pub/sub');
});

async function invalidate(key) {
  await cache.delete(key);
  await redis.publish('cache:invalidate', key);
}
```

Now writes invalidate the cache on all processes.

### Experiment 5: Use redis-cli to populate the cache

```bash
redis-cli set user:1 '{"id":1,"username":"alice"}' EX 60
curl http://localhost:3000/users/1
# (cache hit, returns the manually set value)
```

The cache can be populated from outside the app. Useful for warm-up.

---

## Summary

You now have a shared cache. All processes see the same cache. The database load is reduced. Multi-process / multi-region works.

This is the foundation of *distributed caching*. From here, every project that needs shared state can use Redis. The patterns (cache-aside, TTL, JSON serialization) are universal.

In project 24, we will add rate limiting. We will throttle abuse (a malicious client making thousands of requests per second).

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

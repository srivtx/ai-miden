# Connection Pooling Demo — Naive vs Pooled with SQLite

Demonstrates the connection pooling concept with three modes. SQLite is in-process, so a "pool" is mostly a queue, but the pattern is the same as `pg.Pool`, `mysql2.createPool`, etc.

## Endpoints
```
GET /naive           # new connection per request
GET /pooled          # reuse one connection
GET /realpool        # real pool pattern: queue, max size, async acquire/release
GET /pool-stress     # 10 concurrent, pool size 5, see queueing
GET /pool/stats      # current pool state
```

## Run
```
node server.js
```

## What this teaches
1. **Cost of connection setup**: even with SQLite (no TCP), creating a new connection has cost. For Postgres, the cost is 10-50ms per connection.
2. **Pool pattern**: max size, acquire/release, queue when full
3. **Connection leak prevention**: `try/finally` to always release
4. **Queueing**: when pool is exhausted, requests wait
5. **When to use what**: SQLite = single connection fine. Postgres = pool essential.

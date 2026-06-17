## Why it exists (THE PROBLEM)

Every HTTP request to your server needs to talk to the database. Naive: open a connection, run query, close connection. Open = 50ms. Query = 1ms. Close = 10ms. Total: 61ms. Database can handle 16 queries per second. Your app can handle 10,000 req/s. They don't match.

**Connection pooling fixes this.** Pre-open 20 connections, keep them alive, reuse them. Query = 1ms. Total: 1ms. Database handles 20,000 queries per second. 1000x faster.

The second problem: opening a new connection is a TCP handshake, then auth, then session setup. Often 10-100ms. A pool reuses the connection. Skip all of that. The first query is slow (50ms), all subsequent are fast (1ms).

The third problem: too many connections overwhelm the database. PostgreSQL default max_connections = 100. If you have 200 app servers each opening 5 connections, you have 1000 connections waiting. The database starts queueing. Latency goes up. Eventually the database refuses new connections. A pool limits each app server to a max of 20. So 200 servers × 20 = 4000. Wait, that's worse. Solution: server-side pooler (pgbouncer) in front of the DB. 4000 client connections, multiplexed onto 100 server connections. Each client gets a connection when needed, returns it when done.

## Definition (very simple)

**Connection** = a TCP socket between your app and the database. Has session state, prepared statements, transaction context. Heavy to create.

**Pool** = a collection of pre-opened connections, ready to be used. Borrow one, do work, return it. The pool manages lifecycle.

**Pool size** = how many connections to keep open. Too few = queries wait. Too many = database overload. Common: 10-30 per app server.

**Pool timeout** = how long to wait for a connection from the pool before giving up. Default 30s. If it takes longer, your app is overloaded.

**Connection leak** = borrowed but never returned. The pool runs out, app hangs. Always `release()` in a `finally` block.

## Real-life analogy

**Without a pool = a restaurant where every customer has to build their own table.** Walk in, get lumber, build a table, eat, tear down the table, walk out. The host (database) spends all its time building and tearing down. No one eats.

**With a pool = a restaurant with 20 tables, ready to go.** Customer walks in, sits at an empty table, eats, leaves, table is ready for the next customer. Host manages the tables. Customers eat fast.

**Connection pool = the host/hostess.** Tracks which tables are free. Sits customers at free tables. If all tables are full, customers wait (or leave if they're impatient).

**Connection leak = a customer who takes the table home.** Now there's one less table forever. Eventually no tables. Customers leave. Restaurant closes.

## Tiny numeric example

Same workload: 10,000 queries/second, each query takes 1ms.

| Approach | Latency | Max QPS | Cost |
|---|---|---|---|
| No pool (open/close per query) | 50ms | 200 | 100x more DB CPU |
| Pool of 20 (no queueing) | 1ms | 20,000 | 1x |
| Pool of 20 (queueing) | varies | 20,000 | queries wait |

A pool of 20 means the database can do 20 queries in parallel. If each takes 1ms, that's 20,000/sec. If queries are CPU-bound on the DB, add more cores; the pool can grow.

## Common confusion (5+ bullet points)

1. **"More connections = faster."** No. There's a point where the DB is saturated. Beyond that, more connections make it slower (context switching, lock contention). For a single CPU database, 50-100 connections is the max useful pool. For a 32-core database, maybe 200-400.

2. **"I should set pool size = max DB connections."** No. Multiple app servers share the DB. If you have 10 app servers and DB allows 100 connections, set each pool to 10. Total = 100. If you set each to 100, total = 1000. DB chokes.

3. **"Pool size = number of CPUs."** In the app, yes (you can't do more work in parallel than CPUs). In the DB, no. The DB has its own concurrency limits. Postgres can use 100 connections on a small box. The ratio of app connections to DB cores is the thing to tune. Common: 4-8 connections per DB core.

4. **"Async apps don't need pools."** They do. Async means non-blocking in your app. The DB connection is still blocking on the DB side. An async app with pool=1 still serializes queries. Async + pool=20 = 20 queries in parallel.

5. **"Connection leaks are rare."** They're the #1 cause of "the app is hanging" in production. A forgotten `release()` in an error path. A timeout that doesn't release. Always use `try/finally` or `with` statements. Always set `connectionTimeout` so leaks eventually time out.

6. **"Prepared statements and pooling don't mix."** They do, with care. Most modern drivers (pg, mysql2) handle this transparently. The pool knows the connection has prepared statements, runs them on borrow.

## Key properties

| Property | Naive | Pool |
|---|---|---|
| Connection setup cost | 50ms per query | 0ms (reuse) |
| Max queries/sec | 20 (DB bound) | 10000+ |
| DB connection count | Unbounded | Bounded |
| Memory in app | None (released after each) | Pool size × connection memory |
| Failure mode | "too many connections" | "pool exhausted, retry later" |

## When to use a pool (almost always)

Use a pool for: web servers, workers, batch jobs, anything that talks to a DB more than once. Don't use a pool for: long-running batch jobs that hold a connection for hours (use a single connection, or a server-side pooler).

For SQLite specifically: a pool is less useful because SQLite uses file locks, not TCP. better-sqlite3 is synchronous and very fast (millions of ops/sec). For Postgres, MySQL, MongoDB, Redis: a pool is essential.

## Connection pooler (pgbouncer, ProxySQL)

When you have many app servers and a small DB:
- 50 app servers × 20 pool = 1000 connections to DB
- DB has max_connections = 100
- Add pgbouncer in front: 1000 client connections, multiplexed onto 100 server connections
- Each app server thinks it has 20 connections, pgbouncer manages

## Connection to our projects

For our 73 apps using SQLite (better-sqlite3), a pool is less critical (SQLite is in-process). For our apps that we port to Postgres later, use `pg.Pool` (Node) or `psycopg2.pool` (Python) or `sqlalchemy.create_engine` (Python). Same pattern: create a pool, get a connection, do work, return it.

For CortexCode and logogen, the model inference doesn't use a DB. But the API logs (we built an observability service) DO use a DB. Apply the same pooling pattern there.

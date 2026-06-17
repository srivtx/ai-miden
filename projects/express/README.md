# Backend Development (Express/Node.js)

## Learning path — 10 projects, one concept each

| # | Project | What you learn | Lines |
|---|---|---|---|
| 1 | `01_hello_routes.js` | GET, POST, PUT, DELETE, params, query, JSON body, 404 | 35 |
| 2 | `02_middleware.js` | Middleware pipeline, auth check, error handler, `next()` | 30 |
| 3 | `03_crud_memory.js` | Full CRUD with array storage, validation, sorting | 55 |
| 4 | `04_crud_sqlite.js` | SQL database, prepared statements, pagination, constraints | 65 |
| 5 | `05_jwt_auth.js` | Register, login, bcrypt, JWT, role middleware | 80 |
| 6 | `06_websocket_chat.js` | Socket.io, rooms, events, online tracking, typing | 55 |
| 7 | `07_file_upload.js` | Multer, single/multi upload, validation, size limits | 65 |
| 8 | `08_redis_cache.js` | Redis cache, sliding window rate limiter, invalidation | 60 |
| 9 | `09_background_jobs.js` | Bull queue, job processing, retry, progress, dashboard | 65 |
| 10 | `10_testing.test.js` | Jest, Supertest, unit tests, API tests, mocks | 70 |

**Total: ~580 lines of executable code. Run each file with `node filename.js`.**

## Progression

```
01 (routes) → 02 (middleware) → 03 (CRUD in memory) → 04 (CRUD SQLite)
    ↓
05 (JWT auth: register, login, protected routes)
    ↓
06 (WebSocket: real-time chat) ← independent
07 (File upload: multer)        ← independent
    ↓
08 (Redis: cache + rate limit)
    ↓
09 (Background jobs: Bull queues)
    ↓
10 (Testing: Jest + Supertest)  ← test everything above
```

## What each project teaches that jobs require

| Job requirement | Project that teaches it |
|---|---|
| REST API design | 01, 03, 04 |
| Authentication (JWT) | 05 |
| Authorization (roles) | 05 |
| Middleware patterns | 02, 05 |
| SQL databases | 04 |
| File handling | 07 |
| Caching (Redis) | 08 |
| Rate limiting | 08 |
| WebSockets / real-time | 06 |
| Background processing | 09 |
| Testing (unit + integration) | 10 |
| Error handling | 02, 03 |
| Input validation | 01, 03, 05, 07 |
| Pagination | 04 |

## How to run

```bash
cd projects/express

# Each project has its own directory with required packages
cd 01_crud_api && npm install express uuid && node 01_hello_routes.js
cd 02_auth_jwt && npm install express jsonwebtoken bcryptjs && node 05_jwt_auth.js
cd 03_websocket  && npm install express socket.io && node 06_websocket_chat.js
cd 04_file_upload && npm install express multer && node 07_file_upload.js
cd 05_redis_cache && npm install express ioredis && node 08_redis_cache.js
# requires Redis running on localhost:6379

cd 06_background_jobs && npm install express bull @bull-board/api @bull-board/express && node 09_background_jobs.js
# requires Redis

cd 07_production_api && npm install jest supertest && npx jest 10_testing.test.js
```

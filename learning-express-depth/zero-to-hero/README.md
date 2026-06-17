# Zero-to-Hero: The Sequential Path

> **One project at a time. Each project solves a pain the previous one revealed.**

This is a book-level learning path. It is not a reference library. It is a *journey* — you walk it in order, and by the end you have built a real-time collaborative workspace (Slack × Notion × Figma-lite hybrid) and you understand every piece of it because each piece answered a pain you personally felt.

## The Philosophy

Most curricula fail for one reason: **they teach topics, not problems**.

A course says "Week 4: Databases" and you dutifully write `SELECT * FROM users`. But you never feel the *necessity*. You never stand in front of a problem that says "I need SQL right now." So when the concept arrives, it lands in your head as a definition, not a tool.

This path is different. It is **pain-driven**:

- Project 1 has no framework. You parse HTTP by hand. You will *never* take `express.json()` for granted again.
- Project 6 stores a `userId` in a cookie. Project 7 shows you that a malicious user can forge that cookie. *Now* you need sessions.
- Project 7 puts sessions in memory. Project 9 restarts the server and everyone is logged out. *Now* you need JWT.
- Project 16's chat polls every 500ms and burns 10,000 DB queries. *Now* you need WebSockets.

Every concept is introduced only when its absence hurts. You will not learn anything you don't immediately use. You will not use anything you didn't just learn.

## The Final Artifact

By project 40, you will have built **Cove** — a real-time collaborative workspace:

- Authenticated workspaces with role-based access
- Threaded chat channels with live presence, typing indicators, read receipts
- Notion-style pages that multiple users co-edit (cursor + CRDT)
- Figma-lite whiteboard with sticky notes, shapes, and live cursors
- Voice huddles (WebRTC peer-to-peer)
- Full-text search with relevance ranking
- File uploads to S3
- Email notifications and digests
- Stripe payments for premium tier
- Outbound webhooks for integrations
- Deployed via Docker + CI/CD with metrics, traces, error tracking
- Split into chat / presence / docs / billing microservices behind a message queue

This is achievable scope. Every project feeds into it. Nothing is dead weight.

## The 40 Projects

### Phase 1 — The HTTP Substrate (raw `node:http`)

| # | Project | Concept | Pain it answers |
|---|---------|---------|-----------------|
| 01 | [The Echo Server](./01-echo-server/) | `node:http`, status codes | Genesis. A 30-line server that says hello. |
| 02 | [The Router](./02-router/) | Routing, method dispatch | "if (url === '/a') ... else if" collapses at 5 routes. |
| 03 | [The JSON API](./03-json-api/) | Content-Type, JSON | Project 2's HTML responses can't be `fetch()`'d. |
| 04 | [The Query-String Reader](./04-query-reader/) | `URLSearchParams` | "GET /users?role=admin" — project 3 has no way to filter. |
| 05 | [The Body Parser](./05-body-parser/) | Streams, JSON body | Every endpoint is read-only. We can't accept input. |
| 06 | [The Cookie Jar](./06-cookie-jar/) | `Set-Cookie`, attributes | Server has no memory of who you are between calls. |

### Phase 2 — Identity & Persistence

| # | Project | Concept | Pain it answers |
|---|---------|---------|-----------------|
| 07 | [The Framework Pivot + Session](./07-framework-session/) | Express, sessions, middleware | Cookies are forgeable; reinventing routing is waste. |
| 08 | [The Bcrypt Vault](./08-bcrypt-vault/) | Hashing, salts, slow KDFs | Plaintext passwords. Rainbow tables. Criminal. |
| 09 | [The JWT](./09-jwt/) | Stateless tokens, claims, refresh | Sessions vanish on restart; don't share across pods. |
| 10 | [The SQLite Notebook](./10-sqlite-notebook/) | SQL, prepared statements | `Ctrl+C` erases everything. We need disk. |
| 11 | [The Foreign Key](./11-foreign-key/) | Relational schema, joins | Users and posts live in silos. No "posts by user X." |
| 12 | [The Migration](./12-migration/) | Schema versioning | First prod deploy adds a column. Old instances break. |
| 13 | [The ORM Detour](./13-orm-detour/) | Prisma or Drizzle, query builder | `db.exec(\`...${id}\`)` is an SQL injection bomb. |

### Phase 3 — Robustness & Quality

| # | Project | Concept | Pain it answers |
|---|---------|---------|-----------------|
| 14 | [The Validator](./14-validator/) | Zod / Joi, request DTOs | The ORM happily writes `email: "not-an-email"`. |
| 15 | [The Error Wall](./15-error-wall/) | Error middleware, custom errors | Stack traces leak to clients. Unhandled throws crash the process. |
| 16 | [The Logger](./16-logger/) | Structured logging, request IDs | `console.log` is unsearchable. "What failed for user 42 at 3am?" |
| 17 | [The REST Refactor](./17-rest-refactor/) | Resource-shaped URLs, idempotency | `/getUser`, `/createUser` are RPC-in-a-tuxedo. |
| 18 | [The Paginator](./18-paginator/) | Offset + cursor, Link headers | `GET /posts` returns 80K rows and OOMs the worker. |
| 19 | [The Searcher](./19-searcher/) | FTS5, BM25, ranking | `WHERE title LIKE '%foo%'` is O(n) and gives no relevance. |

### Phase 4 — Real-World Operations

| # | Project | Concept | Pain it answers |
|---|---------|---------|-----------------|
| 20 | [The Uploader](./20-uploader/) | `multipart/form-data`, S3 pre-signed URLs | The avatar URL field is just a string. We need real bytes. |
| 21 | [The Mailroom](./21-mailroom/) | SMTP, transactional providers | Signup verification, password reset, alerts — all need email. |
| 22 | [The Cache](./22-cache/) | In-memory LRU + TTL, cache-aside | "Popular posts" runs 5,000×/sec. DB is on fire. |
| 23 | [The Redis Switch](./23-redis-switch/) | Redis, TTL, pub/sub, sorted sets | 3 pods, 3 in-memory caches, 3 truths. We need shared state. |
| 24 | [The Rate Limiter](./24-rate-limiter/) | Token bucket, sliding window | The search endpoint is being scraped 10k/min by a bot. |
| 25 | [The Cron](./25-cron/) | Scheduled jobs, locking | Sessions pile up forever. Weekly digest needs a clock. |
| 26 | [The Queue](./26-queue/) | BullMQ, retries, dead-letter | Email send blocks signup for 2s. On timeout, user retries → 2 emails. |
| 27 | [The Transaction](./27-transaction/) | ACID, isolation, deadlocks | "Transfer $100 from A to B" — A debited, server crashes, B never credited. |

### Phase 5 — Real-Time & Collaboration

| # | Project | Concept | Pain it answers |
|---|---------|---------|-----------------|
| 28 | [The WebSocket](./28-websocket/) | `ws`, rooms, heartbeat | Chat polls every 500ms. 10K DB queries. The final artifact needs Slack. |
| 29 | [The SSE Stream](./29-sse-stream/) | `EventSource`, half-duplex | WS is overkill for "live notifications." |
| 30 | [The Presence Layer](./30-presence/) | Redis pub/sub, heartbeat, typing | Chat works but feels dead. No green dots. No "Anna is typing…" |
| 31 | [The Co-Editor](./31-co-editor/) | Yjs CRDT, awareness, persistence | Last-write-wins destroys data. Two people edit → one's changes vanish. |
| 32 | [The Voice Channel](./32-voice-channel/) | WebRTC, signaling, STUN/TURN | The canvas needs "join a huddle." Slack does this. So must we. |

### Phase 6 — Production & Scale

| # | Project | Concept | Pain it answers |
|---|---------|---------|-----------------|
| 33 | [The RBAC](./33-rbac/) | Roles, permission tables, policy middleware | A `viewer` can `DELETE /workspaces/:id`. |
| 34 | [The Webhook](./34-webhook/) | Outbound hooks, HMAC signing, retries | Stripe must tell *us* when payment succeeded. GitHub too. |
| 35 | [The Payment](./35-payment/) | Stripe Checkout, idempotency, webhooks → state machine | Premium tier exists. We need to charge for it. |
| 36 | [The Test Suite](./36-test-suite/) | Unit, integration, fixtures, coverage | The payment webhook has 8 branches and zero tests. |
| 37 | [The Container](./37-container/) | Dockerfile, multi-stage, docker-compose | "Works on my machine" is unfixable without a container. |
| 38 | [The Pipeline](./38-pipeline/) | GitHub Actions, secrets, rollback | Image built by hand at 2am. Manual deploys cause outages. |
| 39 | [The Observability](./39-observability/) | Metrics, traces, health probes, Sentry | You can't fix what you can't see. "The p99 spiked" must be answerable. |
| 40 | [The Microservice Split](./40-microservice-split/) | Bounded contexts, service-to-service auth, broker, sagas | One team's hotfix ships everyone else's bugs. The monolith must split. |

## How to Use This Path

1. **Walk in order.** Project 1 builds on nothing. Project 40 builds on all 39 before it.
2. **Read the .md files in this order**:
   - `PROBLEM.md` — what pain does this project answer?
   - `THOUGHT.md` — chain of reasoning, options, trade-offs
   - `BUILD.md` — line-by-line build instructions
   - `DECISIONS.md` — why this stack, what we rejected
   - `CONNECT.md` — what pain this project leaves for the next one
3. **Run the code.** Every project has a `server.js` (or `index.js`) you can `node` directly.
4. **Break the code.** The point of a tutorial is to read it. The point of a path is to *understand* it. Change a line. Predict what happens. Run.
5. **Do not skip.** If you skip project 14 (validation), project 35 (payment) will be a black box. The chain is the point.

## What is Deliberately Absent

- **GraphQL** — REST covers 95% of the path. Can be a project 41 bonus.
- **Kubernetes** — single-node Docker is enough. k8s is a 6-month rabbit hole of its own.
- **Kafka / RabbitMQ** — collapsed with microservices into one project.
- **Microservices frameworks (gRPC, tRPC)** — HTTP/JSON is enough for the learning path.
- **Graph databases, time-series DBs, vector DBs** — out of scope; appear in a future path.

These omissions are intentional. The path is opinionated.

## The Companion Library

Alongside this path, `learning-express-depth/` keeps the older `0X-name/` (60 single-concept demos) and `incremental*/` (10 incremental apps, 102 stages). Use them as a *reference library* — when you finish project 27 (transactions) and want to see the same concept applied to a different shape, look in `incremental-blog/` for how a blog does it. The library is depth. The path is sequence. They complement each other.

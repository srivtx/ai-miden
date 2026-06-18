# The Decisions

> *"Express is the inflection point. We didn't replace the foundation; we adopted it. The mystery is gone because we built it."*

## Decision 1: Express and not Fastify, Hono, Koa, Nest, etc.

**Alternatives**:
- **Fastify** — faster, schema-first, more modern
- **Hono** — very fast, edge-runtime-friendly, very modern
- **Koa** — by the Express team, more minimal (no middleware in core)
- **Nest** — opinionated, TypeScript-first, DI, structured
- **Deno / Bun native** — different runtimes, different frameworks

**Why Express**: It is the most popular Node framework. It has the most middleware. It is the lowest-friction to learn. The concepts transfer to all the others. The community is enormous.

**Trade-off**: Express is not the fastest. It's not the most modern. But it is the standard. The trade-off is worth it for the learning path.

## Decision 2: Adopt now, not earlier

**Alternative**: Use Express from project 01.

**Why we didn't**: We wanted to understand what Express does. By building the dispatch by hand for 6 projects, we know exactly what `express.json()` does, what `cookieParser` does, what `express-session` does. The mystery is gone.

**Trade-off**: We wrote more code in projects 01-06. We learned more.

## Decision 3: `express-session` and not custom sessions

**Alternative**: Keep our hand-rolled `SESSIONS` Map.

**Why we didn't**: `express-session` is battle-tested. It handles edge cases (session expiry, cookie signing, store interface, etc.). We don't need to write it.

**Trade-off**: We trust the middleware. We don't see the internals. That's fine for the in-memory default; we'll see the store interface in project 23 (Redis).

## Decision 4: In-memory session store

**Alternative**: Redis, database, file-based store.

**Why in-memory**: Default. Simple. Works for development.

**Trade-off**: Sessions don't survive restarts. They don't share across processes. We'll feel this in project 10+ (DB) and project 23 (Redis).

## Decision 5: `saveUninitialized: false`

**Alternative**: `saveUninitialized: true` (creates sessions for every visitor).

**Why we use false**: Don't create empty sessions. Saves memory. Better privacy.

**Trade-off**: None. Always use `false` in modern apps.

## Decision 6: `resave: false`

**Alternative**: `resave: true` (re-save session on every request).

**Why we use false**: Don't re-save unmodified sessions. Performance.

**Trade-off**: None. Always use `false` in modern apps.

## Decision 7: A dev secret

**Alternative**: A long random string from an environment variable.

**Why we use a placeholder**: For development. We'll discuss env vars in project 14 (Validator) or a config project.

**Trade-off**: In production, this secret would let attackers forge session cookies. We always use env vars in production.

## Decision 8: No CSRF protection

**Alternative**: `csurf` middleware or `SameSite=Strict` cookies.

**Why we don't**: Out of scope for this project. We'll add `SameSite` in a later project (probably 57, CORS).

**Trade-off**: The app is vulnerable to CSRF. We'll fix it.

## Decision 9: No HTTPS

**Alternative**: `https.createServer` with TLS certificates.

**Why we don't**: HTTPS requires certificates. For development, plain HTTP is fine. We'll discuss TLS in project 38 (Pipeline).

**Trade-off**: Cookies are sent in plaintext. In production, this is unacceptable. We always use HTTPS in production.

## Decision 10: No helmet

**Alternative**: `helmet()` middleware (sets security headers).

**Why we don't**: Out of scope for this project. We'll add it in project 58 (Helmet).

**Trade-off**: The app is missing security headers. We'll fix it.

---

## What We Did Not Decide

- **Path parameters** (`/users/:id`) — we have it via `req.params`, but we don't use it yet
- **Validation** — out of scope (project 14)
- **Error handling** — we have basic 500 handling, but not custom error classes
- **Logging** — out of scope (project 16)
- **CORS** — out of scope (project 57)
- **Compression** — out of scope
- **Rate limiting** — out of scope (project 24)
- **Static files** — out of scope

Each is a future decision.

---

## The Meta-Decision: This Is the Inflection Point

For 6 projects, we built a web framework by hand. We know what `express.json()` does. We know what `cookieParser` does. We know what `express-session` does. We built them in miniature.

Now we adopt them in full. The mystery is gone. The framework is no longer magic. It is the dispatch we built, with more features.

This is the moment to notice: **the handler interface `(req, res) => { ... }` will not change in the next 33 projects.** We will add middleware, helpers, and patterns. The handlers will stay the same shape. This is the power of a small, well-defined contract.

The rest of the path is:

- **Identity & Persistence** (08-13): bcrypt, JWT, SQLite, foreign keys, migrations, ORM
- **Robustness & Quality** (14-19): validation, error handling, logging, REST, pagination, search
- **Real-World Operations** (20-27): file uploads, email, caching, Redis, rate limiting, cron, queues, transactions
- **Real-Time & Collaboration** (28-32): WebSockets, SSE, presence, CRDTs, WebRTC
- **Production & Scale** (33-40): RBAC, webhooks, payments, tests, Docker, CI/CD, observability, microservices

Each project adds *one* concept, on top of the same Express foundation. The handlers stay the same. The middleware grows. The architecture is stable.

This is the inflection point. The rest is depth.

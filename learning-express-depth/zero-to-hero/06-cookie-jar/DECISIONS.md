# The Decisions

> *"Cookies are tiny. The protocol is simple. The implications are deep."*

## Decision 1: Cookies and not Authorization header

**Alternative**: `Authorization: Bearer <token>` header.

**Why we use cookies**: Browsers send cookies automatically. Setting custom headers requires JavaScript, which means CORS preflight, which is more friction for a browser-based frontend. For server-to-server APIs, `Authorization` is cleaner. For browsers, cookies win.

**Trade-off**: Cookies are vulnerable to CSRF. We'll mitigate with `SameSite` (project 57) and CSRF tokens (a later project).

## Decision 2: In-memory `SESSIONS` Map and not a database

**Alternative**: Store sessions in Redis or a database.

**Why in-memory**: For development. It's fast and simple. We don't have a database yet (project 10).

**Trade-off**: Sessions don't survive restarts. They don't share across processes. In production, you'd use Redis (project 23) or a database (project 10). We'll feel this pain in project 07+.

## Decision 3: Integer session IDs, not UUIDs

**Alternative**: `crypto.randomUUID()`.

**Why integers**: For development. Easy to debug. Easy to read.

**Trade-off**: Predictable. An attacker could try IDs 1, 2, 3, ... and might find a valid session. In production, you'd use `crypto.randomUUID()` or `crypto.randomBytes(32).toString('hex')` for high-entropy IDs.

## Decision 4: `HttpOnly` and `Path=/`

**Why `HttpOnly`**: Protects against XSS cookie theft.

**Why `Path=/`**: The cookie is sent for every URL on this domain. Without it, the cookie is only sent for the path that set it.

**Why not `Secure`**: We use plain HTTP in development. `Secure` requires HTTPS. We'll add it in production.

**Why not `SameSite=Strict`**: It would break some legitimate cross-site flows. We use the default (which is `Lax` in modern browsers). We'll discuss `SameSite` in project 57 (CORS).

**Why not `Max-Age`**: Session cookies (no `Max-Age`) are fine for development. They die when the browser closes. For "remember me" functionality, you'd set `Max-Age` to a long duration.

## Decision 5: One cookie at a time

`setCookie` overwrites the `Set-Cookie` header. If we need multiple cookies, we'd need an array.

**Why we don't worry about this**: Our app has one cookie (`sessionId`). If we needed more (e.g., `theme`, `lang`), we'd extend `setCookie` to handle arrays. We don't need to.

## Decision 6: No `expires` and no cleanup

Sessions live forever in `SESSIONS`. They accumulate as users log in.

**Why we don't clean up**: For development. In production, you'd expire sessions after a timeout (e.g., 30 days), and run a cron job to remove expired sessions. We'll do that in project 25 (Cron).

## Decision 7: Cookie value is just the ID

The cookie is `sessionId=abc123`. The session data (`{ username, createdAt }`) is in `SESSIONS`.

**Why not put the data in the cookie?**: The data could be tampered with. We'd need to *sign* the cookie to prevent tampering. That's JWT (project 09).

**Why is this the simpler approach?**: The cookie is just a pointer. The server has the data. The user can't see or edit the data without breaking the link.

## Decision 8: No CSRF protection

A malicious site could trick the user's browser into making a `POST /logout` request. The cookie would be sent automatically, and the user would be logged out without their consent.

**Why we don't add CSRF protection now**: It's a separate concern (project 57 or later). The standard mitigation is `SameSite=Strict` on the cookie. We'll add it.

## Decision 9: Parse cookies synchronously

`req.headers.cookie` is available immediately (it's a header, not the body). We parse it in the dispatch, before the body listener. This is correct.

## Decision 10: Hand-rolled cookie parser

**Alternative**: Use the `cookie` npm package or `cookie-parser` (Express middleware).

**Why hand-rolled**: We want to understand the protocol. The parser is 7 lines. We can replace it later.

**Trade-off**: The hand-rolled parser doesn't handle all edge cases (e.g., values with `=` in them, escaped characters). The `cookie` package does. For production, use the package.

---

## What We Did Not Decide

- **CSRF tokens** — out of scope for this project (project 57)
- **Session expiration** — out of scope (project 25)
- **Refresh tokens** — out of scope (project 09)
- **Multiple cookies** — out of scope
- **Signed cookies** — out of scope (project 09, JWT)
- **Encrypted cookies** — out of scope
- **Same-origin policy** — out of scope (project 57)
- **Database storage** — out of scope (project 10)
- **Redis storage** — out of scope (project 23)

Each is a future decision.

---

## The Meta-Decision: This Is the Last Project in the HTTP Substrate

Look at the dispatch now. It does:

- URL parsing (path + query)
- Cookie parsing
- Body parsing (with error handling)
- Route lookup
- 404 fallback

Plus we have:

- A `Map` of routes
- A `Map` of sessions
- Helpers: `json`, `setCookie`, `parseCookies`

This is a *complete* web framework's core. It is ~80 lines. It is *exactly* what Express does, just with more code.

In project 07, we will *replace* this with Express. The hand-rolled dispatch goes away. Express takes over. The handlers stay the same. The same patterns — `req.query`, `req.body`, `req.cookies` — are now provided by Express middleware.

The HTTP substrate is *done*. We have:

- A router
- JSON I/O
- Query strings
- Body parsing
- Cookies
- Sessions (in-memory)

From here, the path diverges into:

- **Identity & Persistence** (projects 07-13): real auth, real DB, real migrations
- **Robustness & Quality** (projects 14-19): validation, error handling, logging, REST, pagination, search
- **Real-World Operations** (projects 20-27): file uploads, email, caching, Redis, rate limiting, cron, queues, transactions
- **Real-Time & Collaboration** (projects 28-32): WebSockets, SSE, presence, CRDTs, WebRTC
- **Production & Scale** (projects 33-40): RBAC, webhooks, payments, tests, Docker, CI/CD, observability, microservices

Each of these is a *specialization* on top of the substrate. The substrate is solid. Now we build the rest of the system.

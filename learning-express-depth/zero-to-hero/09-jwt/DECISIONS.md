# The Decisions

> *"Stateless tokens scale. Server-side sessions don't. The trade-off is revocation."*

## Decision 1: JWT and not opaque tokens

**Alternative**: Generate a random session ID, store it in a database, send to client. The client sends the ID back. The server looks it up.

**Why JWT**: The token is self-contained. No database lookup on every request. Any server can verify. Multi-process, multi-region, restart-safe — all solved.

**Trade-off**: Cannot revoke. Cannot invalidate. Token contains data (so don't put secrets in it). For these limitations, see decision 4.

## Decision 2: `Authorization: Bearer` and not cookies

**Alternative**: Send the token in a cookie. Browser auto-sends it.

**Why `Authorization: Bearer`**: Cleaner separation. The token is an *API credential*, not a browser cookie. No CSRF (browsers don't auto-send `Authorization` headers). Easier to use from mobile apps, server-to-server, etc.

**Trade-off**: The client (JavaScript) must add the header to every request. For browser apps, you can store the token in a cookie instead, but then you have CSRF.

## Decision 3: HS256 and not RS256

**Alternative**: RS256 (asymmetric — different keys for signing and verifying).

**Why HS256**: Simpler. One secret. The same server signs and verifies.

**Trade-off**: If you have multiple services that need to verify but only one should sign, use RS256. For a single-service app, HS256 is fine.

## Decision 4: 7-day TTL

**Alternative**: 15 minutes, 1 hour, 30 days, never.

**Why 7 days**: Balance between UX and security. Long enough that the user doesn't log in daily. Short enough that a leaked token is only useful for a week.

**Trade-off**: If a token leaks, it's valid for 7 days. For high-security apps, use 15 minutes + refresh tokens. For low-security apps, 30 days is fine.

## Decision 5: No refresh tokens

**Alternative**: Issue a short-lived JWT (15 min) + a long-lived refresh token (stored in DB). The client uses the JWT for normal requests, exchanges the refresh token for a new JWT when it expires.

**Why we don't**: Out of scope for this project. We'll add it in a future project.

**Trade-off**: The user has to log in every 7 days. With refresh tokens, the user only has to log in every 30 days (or whatever the refresh TTL is).

## Decision 6: No revocation list

**Alternative**: Maintain a list of revoked tokens (by `jti` or by user). On every request, check the list. Reject if revoked.

**Why we don't**: A revocation list is server-side state. It defeats the purpose of stateless JWT. We'll add it as an optional feature later.

**Trade-off**: A leaked token is valid until `exp`. We accept this for simplicity.

## Decision 7: No password change invalidation

**Alternative**: Include a `passwordVersion` in the token. On every request, check the token's version against the current user's version. If they don't match, reject.

**Why we don't**: Out of scope. We don't have a way to change passwords yet (would need a `PATCH /users/me` endpoint, which is a different project).

**Trade-off**: If a user changes their password, old tokens are still valid. We accept this for now.

## Decision 8: `req.user` and not `req.session`

**Alternative**: Use `req.session` for compatibility with project 08.

**Why `req.user`**: The convention. After auth middleware, `req.user` is the authenticated user. This is what most APIs use. The handler reads `req.user.userId` or `req.user.username`.

**Trade-off**: None. Standard convention.

## Decision 9: `authMiddleware` as a function, not a route decorator

**Alternative**: Express has route decorators (e.g., `@RequireAuth` in TypeScript). In vanilla JS, you can use libraries like `express-router-typer`.

**Why a function**: Plain JavaScript. Easy to read. Easy to compose with other middleware.

**Trade-off**: The handler signature is `app.get('/me', authMiddleware, handler)` — three arguments. A bit verbose. We accept it.

## Decision 10: Dev secret in source

**Alternative**: Read from environment variable.

**Why we don't**: We haven't introduced env vars yet. We'll do that in project 14 (Validator) or a config project.

**Trade-off**: The secret is in the source. If the source is leaked (e.g., pushed to a public repo), the secret is leaked. We always use env vars in production.

---

## What We Did Not Decide

- **Refresh tokens** — out of scope (future project)
- **Revocation list** — out of scope (future project)
- **Password change invalidation** — out of scope
- **Token storage on the client** — client decides
- **OAuth / OIDC** — out of scope
- **JWE (encrypted JWT)** — out of scope
- **Algorithm flexibility** — we use HS256 only
- **Multi-tenant tokens** — out of scope
- **Persistent user storage** — out of scope (project 10)

Each is a future decision.

---

## The Meta-Decision: The Server Has No State

Look at the server. It has:

- `SECRET` — the signing key
- `USERS` — the user database (in memory)
- `TOKEN_TTL` — the token expiration

That's it. The server doesn't know who's logged in. It doesn't track active sessions. It doesn't keep a list of issued tokens. Every request is independent — the token contains the data.

This is *radically* different from session-based auth. The server is a *verifier*, not a *store*. The token is the source of truth.

This is the foundation of scale. You can run 1000 servers. The token works on all of them. You can survive restarts. You can survive multi-region. The server is dumb; the token is smart.

The trade-offs (revocation, invalidation, logout) are real. For most apps, they're acceptable. For high-security apps, you add a revocation layer (a database check on every request). The token is still the credential; the database is the revocation list.

This is the inflection point of identity. Sessions are state. JWT is stateless. Stateless scales. The next 31 projects will assume JWT auth. The patterns are stable.

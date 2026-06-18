# The Problem

> *"Sessions are state. State is a burden. Stateless tokens are the future."*

## Why Server-Side State Is Painful

In projects 06-08, we used server-side sessions. The flow:

1. User logs in
2. Server creates a session, stores it in memory (or Redis, or DB)
3. Server sends a session ID cookie
4. User makes a request with the cookie
5. Server looks up the session in memory
6. Server uses the session data

This works. It also has problems:

### Problem 1: Memory pressure

Every active user has a session in memory. 1 million users = 1 million sessions. Each session is small, but multiplied, it adds up. The server has to look up the session on *every* request.

### Problem 2: Sticky sessions

If you have 3 server processes behind a load balancer, each has its own session store. A user logged in to process 1 might be routed to process 2 on the next request. Process 2 has no session for that user. The user is logged out.

The fix is *sticky sessions* (the load balancer always routes the user to the same process). But sticky sessions are fragile — if a process dies, all its users are logged out.

### Problem 3: Restart wipes state

Restart the server. All sessions are gone. Every user is logged out. Annoying in development, fatal in production.

### Problem 4: Multi-region is hard

If you have servers in the US and EU, sessions in the US are not visible to the EU. You need shared session storage (Redis) across regions, which is more infrastructure.

## What Pain Is This Solving?

We want authentication that:

1. Doesn't require server-side lookup
2. Works across multiple server processes
3. Survives restarts
4. Works across regions

**Stateless tokens** solve all four. The token contains the session data, signed. The server doesn't need to look anything up — it just verifies the signature and trusts the data.

## The Deeper Problem: Trust and Tampering

If the token contains the data ("user is alice, userId is 42"), and the data is in the token, what's stopping an attacker from creating a fake token?

```
fake_token = "userId: 42, username: alice"
```

The answer: **signing**. The server signs the token with a secret. The signature is part of the token. If the attacker tampers with the data, the signature doesn't match. The server rejects the token.

The server has the secret. The client doesn't. So the client can read the token, but can't forge one. This is the trust model.

## What This Project Will Solve

This project will:

1. Replace `express-session` with JWT
2. Sign a token on successful login
3. Send the token in the response body (not a cookie)
4. Add an `authMiddleware` that reads the `Authorization: Bearer <token>` header
5. Verify the token on protected routes
6. The server has *zero* session state

By the end, any server with the `SECRET` can verify any token. Multi-process, multi-region, restart-safe — all solved.

## What This Project Will *Not* Solve

- **Token refresh** — the token expires in 7 days. We don't have a refresh flow. We'll add it in a future project.
- **Token revocation** — once issued, the token is valid for 7 days. We can't revoke it (it's stateless). We'll add a revocation list in a future project.
- **Token storage on the client** — the client decides where to store it (localStorage, cookie, etc.). We don't dictate.
- **CSRF** — if the token is in a cookie, we still have CSRF. If it's in `Authorization: Bearer`, no CSRF (browsers don't auto-send it). We use `Authorization: Bearer`.
- **Refresh tokens** — out of scope.
- **OAuth / OIDC** — out of scope.
- **Persistent storage** — users are still in memory. Project 10.

## The Question This Project Answers

> *"How do I scale authentication across multiple servers?"*

If you can answer: "issue a signed JWT, send it in `Authorization: Bearer`, verify with the secret on every request," you are ready for project 10.

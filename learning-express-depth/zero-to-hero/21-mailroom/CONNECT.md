# The Connect

> *"The API talks to users. Now we need caching, Redis, rate limiting, and the rest of the operations."*

This project added email with Nodemailer. The pain of "the user has no idea what happened" is solved. The user gets a welcome email on signup. They can request a password reset. They receive a reset email with a one-time token. They reset their password.

But the API is still limited:

1. **No caching** — every request hits the database. For "popular posts" or "user profile," we re-query the same data.
2. **No Redis** — sessions and cache are in memory. Multi-process / multi-region is hard.
3. **No rate limiting** — a malicious client can hammer endpoints.
4. **No cron** — things that should fire on a schedule don't.
5. **No queue** — slow work (email send) blocks the request.
6. **No transactions** — multi-step writes can fail mid-way.

Projects 22-27 (rest of Phase 4) will fix these. After Phase 4, the API has *all* the real-world operations: file upload, email, caching, rate limiting, cron, queue, transactions.

## What Works

- Email via Nodemailer (Ethereal in dev, real provider in production)
- Welcome email on signup
- `POST /sessions/forgot` (request password reset)
- `POST /sessions/reset` (reset password with token)
- Hashed tokens with expiration
- No email enumeration

## What Doesn't Work

### 1. No caching

Every request hits the database. For "popular posts" or "user profile," we re-query the same data.

**The pain**: Caching. Project 22 (Cache).

### 2. No Redis

Sessions and cache are in memory. Multi-process / multi-region is hard.

**The pain**: Redis. Project 23.

### 3. No rate limiting

A malicious client can hammer endpoints.

**The pain**: Rate limiting. Project 24.

### 4. No cron

Things that should fire on a schedule (session cleanup, daily digest) don't.

**The pain**: Cron. Project 25.

### 5. No queue

Slow work (email send, image processing) blocks the request.

**The pain**: Queue. Project 26.

### 6. No transactions

Multi-step writes can fail mid-way, leaving the database in a bad state.

**The pain**: Transactions. Project 27.

### 7. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 8. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 9. No tests

We can't verify the email flow works.

**The pain**: Tests. Project 36.

### 10. No observability

We can't see what's happening in production.

**The pain**: Observability. Project 39.

---

## What This Project Forbids Us From Doing

This server can:

- Send emails (welcome, password reset)
- Hash tokens, store with expiration
- Send via Ethereal (dev) or real provider (prod)
- Prevent email enumeration

It cannot:

- Cache responses
- Share state across processes
- Rate-limit clients
- Run scheduled jobs
- Move slow work off the request
- Make atomic multi-step writes
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically
- Be observed in production

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 22 | The Cache | "I want to reduce DB load." |
| 23 | The Redis | "I want shared state across processes." |
| 24 | The Rate Limiter | "I want to throttle abuse." |

Project 22 is the natural next step. We have email, but every request still hits the database. We need caching.

---

## What You Should Do Now

1. **Read the code.** Notice the mailer setup, the welcome email, the password reset flow. The handlers are slightly different.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Sign up** with an email. Check the server logs for the Ethereal preview URL. Open it in a browser.
4. **Request a password reset.** Check the email. Reset the password.
5. **Try to use the token twice.** See the rejection.
6. **Try to use an expired token.** See the rejection.
7. **When you are ready**, move to [Project 22: The Cache](../22-cache/).
8. **If anything is unclear**, do not proceed. Email is the foundation of every user-facing product. It must be solid.

---

## A Note on the Bigger Picture

You now have an API that *talks to users*. The user gets a welcome email. They can request a password reset. They receive a reset email. They reset their password.

From here, the path diverges:

- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The API talks to users. The path continues.

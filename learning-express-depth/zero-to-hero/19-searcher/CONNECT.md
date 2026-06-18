# The Connect

> *"The API has search. Now we need file uploads, email, caching, and the rest of the operations."*

This project added FTS5 full-text search. The pain of "LIKE is slow and dumb" is solved. The `GET /posts?q=` endpoint searches an inverted index. Results are ranked by BM25. The query is fast.

But the API is still limited:

1. **No file upload** — can't attach images to posts.
2. **No email** — can't notify users.
3. **No caching** — every request hits the database.
4. **No real-time** — every request is one-shot.

Projects 20-27 (rest of Phase 4) will fix these. After Phase 4, the API has *all* the real-world operations: search, file upload, email, caching, rate limiting, cron, queue, transactions.

## What Works

- FTS5 virtual table (`posts_fts`) indexes `title` and `body`
- Triggers keep the FTS table in sync with `posts`
- `GET /posts?q=` searches the FTS table
- Results are ranked by BM25 (`posts_fts.rank`)
- Pagination still works
- The auth and post flows are unchanged

## What Doesn't Work

### 1. No file upload

Can't attach images to posts.

**The pain**: File upload. Project 20 (Uploader).

### 2. No email

Can't notify users (password reset, signup confirmation, etc.).

**The pain**: Email. Project 21 (Mailroom).

### 3. No caching

Every request hits the database. For "popular posts" or "user profile," we re-query the same data.

**The pain**: Caching. Project 22 (Cache).

### 4. No Redis

Sessions and cache are in memory. Multi-process / multi-region is hard.

**The pain**: Redis. Project 23.

### 5. No rate limiting

A malicious client can hammer endpoints.

**The pain**: Rate limiting. Project 24.

### 6. No cron

Things that should fire on a schedule (session cleanup, daily digest) don't.

**The pain**: Cron. Project 25.

### 7. No queue

Slow work (email send, image processing) blocks the request.

**The pain**: Queue. Project 26.

### 8. No transactions

Multi-step writes can fail mid-way, leaving the database in a bad state.

**The pain**: Transactions. Project 27.

### 9. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 10. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

---

## What This Project Forbids Us From Doing

This server can:

- Search by text with relevance ranking
- Return BM25-ranked results
- Paginate search results
- Keep the FTS index in sync with the source

It cannot:

- Accept file uploads
- Send email
- Cache responses
- Share state across processes
- Rate-limit clients
- Run scheduled jobs
- Move slow work off the request
- Make atomic multi-step writes
- Be called from a browser on a different origin
- Be protected by security headers

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 20 | The Uploader | "I want to accept files." |
| 21 | The Mailroom | "I want to send notifications." |
| 22 | The Cache | "I want to reduce DB load." |

Project 20 is the natural next step. We have a text API, but we can't accept images. Real apps need file uploads.

---

## What You Should Do Now

1. **Read the code.** Notice the FTS table, the triggers, the `MATCH` query, the `rank` column. The handlers are slightly updated.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Create some posts** with different content.
4. **Search for various terms.** See the ranking.
5. **Try phrase queries** (`"hello world"`), boolean queries (`hello AND world`), prefix queries (`hel*`).
6. **When you are ready**, move to [Project 20: The Uploader](../20-uploader/).
7. **If anything is unclear**, do not proceed. Search is the foundation of every user-facing API. It must be solid.

---

## A Note on the Bigger Picture

You now have a *searchable* API. The user can find by text. The results are ranked. The query is fast.

From here, the path diverges:

- **File upload** (project 20): accept files
- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The API has search. The path continues.

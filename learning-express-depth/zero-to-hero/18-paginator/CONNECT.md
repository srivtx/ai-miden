# The Connect

> *"The API scales to lists. Now we need search, file uploads, and the rest of the operations."*

This project added pagination. The pain of "GET /posts returns 1M rows" is solved. List endpoints return a page at a time. The client can navigate pages. The server doesn't OOM.

But the API is still limited:

1. **No search** — `GET /posts?search=hello` is a slow `LIKE` query. No relevance.
2. **No filtering** — `?author=42` is a simple addition. We don't have it.
3. **No sorting** — we hardcode `ORDER BY created_at DESC`.
4. **No file upload** — can't attach images to posts.
5. **No email** — can't notify users.

Project 19 (Searcher) will fix the search. After Phase 3, the API is *robust*: validated input, validated output, structured logging, REST-shaped URLs, paginated, searchable.

## What Works

- All list endpoints are paginated with `?limit=&offset=`
- Response is `{ data, meta }` with `total`, `limit`, `offset`, `page`, `totalPages`
- The limit is capped at 100
- The data and count queries run in parallel
- The client can navigate pages
- The server doesn't OOM

## What Doesn't Work

### 1. No search

`GET /posts?search=hello` is a slow `LIKE` query. No relevance ranking.

**The pain**: Search. Project 19 (Searcher).

### 2. No filtering

`?author=42` would be a simple addition.

**The pain**: Filtering. Future project.

### 3. No sorting

We hardcode `ORDER BY created_at DESC`. Can't sort by title, author.

**The pain**: Sorting. Future project.

### 4. No file upload

Can't attach images to posts.

**The pain**: File upload. Project 20.

### 5. No email

Can't notify users.

**The pain**: Email. Project 21.

### 6. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 7. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 8. No rate limiting

A malicious client can hammer endpoints.

**The pain**: Rate limiting. Project 24.

### 9. No tests

We can't verify the pagination works.

**The pain**: Tests. Project 36.

### 10. No caching

Every request hits the database.

**The pain**: Caching. Project 22.

---

## What This Project Forbids Us From Doing

This server can:

- Paginate list endpoints
- Return `{ data, meta }` with full metadata
- Cap the limit
- Run data + count queries in parallel

It cannot:

- Search with relevance
- Filter by arbitrary fields
- Sort by arbitrary columns
- Accept file uploads
- Send email
- Be called from a browser on a different origin
- Be protected by security headers
- Be rate-limited
- Be tested automatically
- Cache responses

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 19 | The Searcher | "I want to find with relevance." |
| 20 | The Uploader | "I want to accept files." |
| 21 | The Mailroom | "I want to send notifications." |

Project 19 is the natural next step. We have lists, but no way to find specific items. We need search.

---

## What You Should Do Now

1. **Read the code.** Notice the `limit`, `offset`, `Promise.all`, the `meta` object. The handlers are slightly updated.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Try various pages**. See how the data and meta change.
4. **Try `?limit=10000`**. See the cap kick in.
5. **Try `?offset=1000000`**. See the empty data with correct meta.
6. **When you are ready**, move to [Project 19: The Searcher](../19-searcher/).
7. **If anything is unclear**, do not proceed. Pagination is the foundation of every list API. It must be solid.

---

## A Note on the Bigger Picture

You now have a *scalable* API. Lists are paginated. The server doesn't OOM. The client can navigate pages.

From here, the path diverges:

- **Search** (project 19): find with relevance
- **File upload** (project 20): accept files
- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The API scales. The path continues.

---

## Phase 3 Complete: Robustness & Quality

With project 18, we finish Phase 3 (Robustness & Quality). The 7 projects in this phase:

- 13: ORM Detour (Knex)
- 14: Validator (Zod)
- 15: Error Wall (HttpError)
- 16: Logger (pino)
- 17: REST Refactor
- 18: Paginator
- 19: Searcher (next)

The server is *robust*: validated input, validated output, structured logging, REST-shaped URLs, paginated, searchable. The path continues to Phase 4: Real-World Operations.

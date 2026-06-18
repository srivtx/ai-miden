# The Connect

> *"The server is observable. Now we need REST-shaped URLs, pagination, and search."*

This project added structured logging with pino. The pain of "I have no visibility into production" is solved. Every request is logged. Every error is logged with context. The request ID ties everything together. The logs are JSON, queryable, and aggregatable.

But the server still has structural issues:

1. **Ad-hoc URLs** — `/posts` and `/users/:id/posts` are inconsistent.
2. **No pagination** — `GET /posts` returns all posts.
3. **No search** — `GET /posts?search=hello` is a slow `LIKE` query.

Projects 17-19 (rest of Phase 3) will fix these. After Phase 3, the server is *robust*: validated input, validated output, structured logging, REST-shaped URLs, paginated, searchable.

## What Works

- Structured JSON logging with pino
- Request IDs for correlation
- `req.log` for child context
- `pino-http` for automatic request logging
- The error wall logs errors with context
- Pretty-printing in development
- The auth and post flows are unchanged

## What Doesn't Work

### 1. Ad-hoc URLs

`GET /posts` and `GET /users/:id/posts` are inconsistent. REST APIs use resource-shaped URLs.

**The pain**: REST. Project 17 (REST Refactor).

### 2. No pagination

`GET /posts` returns all posts.

**The pain**: Pagination. Project 18 (Paginator).

### 3. No search

`GET /posts?search=hello` is a slow `LIKE` query.

**The pain**: Search. Project 19 (Searcher).

### 4. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 5. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 6. No rate limiting

A malicious client can hammer endpoints.

**The pain**: Rate limiting. Project 24.

### 7. No tests

We can't verify the logging works.

**The pain**: Tests. Project 36.

### 8. No file upload

We can't accept files.

**The pain**: File upload. Project 20.

### 9. No email

We can't send notifications.

**The pain**: Email. Project 21.

### 10. No caching

Every request hits the database.

**The pain**: Caching. Project 22.

---

## What This Project Forbids Us From Doing

This server can:

- Log every request with method, URL, status, duration, request ID
- Log every error with stack trace and request context
- Pretty-print logs in development
- Search and filter logs in production

It cannot:

- Have REST-shaped URLs
- Paginate large lists
- Search with relevance
- Be called from a browser on a different origin
- Be protected by security headers
- Be rate-limited
- Be tested automatically
- Accept file uploads
- Send email
- Cache responses

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 17 | The REST Refactor | "I want resource-shaped endpoints." |
| 18 | The Paginator | "I want to handle large lists." |
| 19 | The Searcher | "I want to find with relevance." |

Project 17 is the natural next step. We have a working API, but the URLs are ad-hoc. We want REST.

---

## What You Should Do Now

1. **Read the code.** Notice the logger, the `pino-http` middleware, the `req.log` in handlers. The error wall uses `req.log.error(...)`.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Look at the logs.** See the JSON structure. See the request IDs. See the error context.
4. **Try `LOG_LEVEL=debug`**. See the request start logs.
5. **Try `NODE_ENV=production`**. See the raw JSON.
6. **When you are ready**, move to [Project 17: The REST Refactor](../17-rest-refactor/).
7. **If anything is unclear**, do not proceed. Structured logging is the foundation of every observable service. It must be solid.

---

## A Note on the Bigger Picture

You now have an *observable* server. Every event is logged. The logs are queryable. The patterns are universal.

From here, the path diverges:

- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

The server is observable. The path continues.

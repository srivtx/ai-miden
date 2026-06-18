# The Connect

> *"The wall is built. Now we need to log what happens, structure the URLs, paginate, and search."*

This project added an error wall. The pain of "errors crash the response" is solved. Custom error classes. The wall catches. JSON responses. No stack traces leaked.

But the server is still opaque:

1. **No logging** — `console.error(err)` is unstructured. We can't search, filter, or analyze. We don't log requests, successes, or timings.
2. **URLs are ad-hoc** — `/posts` and `/users/:id/posts` are inconsistent. A REST API would have a convention.
3. **No pagination** — `GET /posts` returns all posts.
4. **No search** — `GET /posts?search=hello` is a slow `LIKE` query.

Projects 16-19 (rest of Phase 3) will fix these. After Phase 3, the server is *robust*: validated input, validated output, structured logging, REST-shaped URLs, paginated, searchable.

## What Works

- Custom error classes (`HttpError`, `NotFoundError`, `ConflictError`, etc.)
- `asyncHandler` wrapper for async error catching
- `errorHandler` middleware (the wall)
- Handlers throw instead of returning 4xx JSON
- `validate` throws `ValidationError`
- `authMiddleware` throws `UnauthorizedError`
- Consistent error response shape
- No stack traces leaked

## What Doesn't Work

### 1. No structured logging

`console.error(err)` is unstructured. We can't search, filter, or analyze. We don't log requests, successes, or timings.

**The pain**: Observability. Project 16 (Logger).

### 2. Ad-hoc URLs

`GET /posts` and `GET /users/:id/posts` are inconsistent.

**The pain**: REST. Project 17 (REST Refactor).

### 3. No pagination

`GET /posts` returns all posts.

**The pain**: Pagination. Project 18 (Paginator).

### 4. No search

`GET /posts?search=hello` is a slow `LIKE` query.

**The pain**: Search. Project 19 (Searcher).

### 5. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 6. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 7. No rate limiting

A malicious client can hammer endpoints.

**The pain**: Rate limiting. Project 24.

### 8. No tests

We can't verify the error handling works.

**The pain**: Tests. Project 36.

### 9. No file upload

We can't accept files.

**The pain**: File upload. Project 20.

### 10. No email

We can't send notifications.

**The pain**: Email. Project 21.

---

## What This Project Forbids Us From Doing

This server can:

- Catch every error with the wall
- Map errors to status codes
- Return consistent JSON responses
- Throw at the source, catch at the wall

It cannot:

- Log requests in a structured way
- Have REST-shaped URLs
- Paginate large lists
- Search with relevance
- Be called from a browser on a different origin
- Be protected by security headers
- Be rate-limited
- Be tested automatically
- Accept file uploads
- Send email

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 16 | The Logger | "I want to see what's happening in production." |
| 17 | The REST Refactor | "I want resource-shaped endpoints." |
| 18 | The Paginator | "I want to handle large lists." |
| 19 | The Searcher | "I want to find with relevance." |

Project 16 is the natural next step. We have errors caught, but we don't have visibility. We need structured logs.

---

## What You Should Do Now

1. **Read the code.** Notice the error classes, the `asyncHandler`, the `errorHandler`. The handlers throw; the wall catches.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Trigger different errors** (validation, conflict, not found, unauthorized). See the consistent response shape.
4. **Trigger a 500** (e.g., a bug in a handler). See the generic 500 with no stack trace.
5. **Look at the server logs.** Notice they're unstructured. Feel the pain of "no logging."
6. **When you are ready**, move to [Project 16: The Logger](../16-logger/).
7. **If anything is unclear**, do not proceed. The error wall is the foundation of every robust API. It must be solid.

---

## A Note on the Bigger Picture

You now have a *robust* error story. Every error is caught. The response is clean. The status code is correct.

From here, the path diverges:

- **Logging** (project 16): structured logs
- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

The wall is built. The errors are caught. The path continues.

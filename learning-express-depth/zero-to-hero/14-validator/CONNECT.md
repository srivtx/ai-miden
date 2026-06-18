# The Connect

> *"The gate is closed. Now we need to handle the errors that pass through, log what happens, and structure the URLs."*

This project added Zod validation. The pain of "I accept any input" is solved. Bad input is rejected with 400 and structured errors. Good input is normalized. The handlers are simpler.

But the server is still fragile:

1. **No error handling** — if a database constraint fails (e.g., unique violation), the user sees a 500 with a stack trace. We want clean 409s.
2. **No logging** — we don't know what's happening in production.
3. **URLs are ad-hoc** — `/posts` and `/users/:id/posts` are inconsistent.

Projects 15-19 (the rest of Phase 3) will fix these.

## What Works

- Zod schemas for each endpoint
- `validate(schema)` middleware
- 400 with structured errors on bad input
- `req.validated` in handlers
- The auth and post flows are unchanged

## What Doesn't Work

### 1. No error handling for unexpected errors

If `db('users').insert(...)` fails with a unique constraint violation, the user gets a 500 with a stack trace. We want a 409 with a friendly message.

**The pain**: Error handling. Project 15 (Error Wall).

### 2. No logging

We don't log signups, logins, failed validation, or database errors. In production, we have no visibility.

**The pain**: Observability. Project 16 (Logger).

### 3. Ad-hoc URLs

`GET /posts` and `GET /users/:id/posts` are inconsistent. A REST API would have `GET /posts?author=1` or `GET /users/1/posts`. We need a convention.

**The pain**: REST. Project 17 (REST Refactor).

### 4. No pagination

`GET /posts` returns all posts. For 1M posts, this is huge.

**The pain**: Pagination. Project 18 (Paginator).

### 5. No search

`GET /posts?search=hello` would be a slow `LIKE` query.

**The pain**: Search. Project 19 (Searcher).

### 6. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 7. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 8. No rate limiting

A malicious client can hammer `/login` with thousands of attempts.

**The pain**: Rate limiting. Project 24.

### 9. No tests

We can't verify the validation works.

**The pain**: Tests. Project 36.

### 10. No file upload

We can't accept images or files.

**The pain**: File upload. Project 20.

---

## What This Project Forbids Us From Doing

This server can:

- Validate input with Zod
- Reject bad input with 400
- Normalize good input
- Use `req.validated` in handlers

It cannot:

- Handle database errors gracefully (no error handling)
- Log requests
- Have REST-shaped URLs
- Paginate large lists
- Search with relevance
- Be called from a browser on a different origin
- Be protected by security headers
- Be rate-limited
- Be tested automatically
- Accept file uploads

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 15 | The Error Wall | "I want to handle errors with proper status codes." |
| 16 | The Logger | "I want to see what's happening." |
| 17 | The REST Refactor | "I want resource-shaped endpoints." |
| 18 | The Paginator | "I want to handle large lists." |

Project 15 is the natural next step. We validate input, but we don't handle output errors. We need consistent error responses.

---

## What You Should Do Now

1. **Read the code.** Notice the schemas, the `validate` middleware, the use of `req.validated`. The auth and post flows are unchanged.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Try to sign up with bad input** (short username, invalid email). See the 400 with structured errors.
4. **Try to sign up with the same username twice.** The first time succeeds; the second should fail. Currently it fails with a 500 (Knex error). Feel the pain of "no error handling."
5. **When you are ready**, move to [Project 15: The Error Wall](../15-error-wall/).
6. **If anything is unclear**, do not proceed. Validation is the foundation of every API. It must be solid.

---

## A Note on the Bigger Picture

You now have *validated* inputs. The gate is closed. The handlers are simple.

From here, the path diverges:

- **Error handling** (project 15): handle database errors, exceptions
- **Logging** (project 16): see what's happening
- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

The validation is solid. The path continues.

# The Connect

> *"The database has an API. Now we need validation, error handling, and a logger."*

This project introduced Knex. The pain of "I have to write prepared statements for every query" is solved. The database has a clean JavaScript API. SQL is generated. Parameters are safe.

But the handlers are still fragile. They accept any input. They don't validate. They don't handle errors well. They don't log. We want:

- **Validation** (project 14): reject bad input with 400
- **Error handling** (project 15): handle constraint violations with 409, 500, etc.
- **Logging** (project 16): see what's happening

Project 14 (Validator) is the next step. We will add a schema validation library (Zod or Joi) and reject bad input before it reaches the database.

## What Works

- Database operations are JavaScript expressions
- Schema changes are JavaScript objects
- The handlers are slightly simpler (no prepared statements)
- Knex handles parameterization (no SQL injection)
- Migrations are in JavaScript (idempotent)
- The auth flow is unchanged
- The post flow is unchanged

## What Doesn't Work

### 1. We don't validate input

`POST /signup` accepts any `username`, `password`, `email`. Empty strings, 1MB strings, weird unicode — all accepted.

**The pain**: Validation. Project 14 (Validator).

### 2. We have no error handling

If the unique constraint on `username` fails, we get a Knex error. We want a clean 409 with a friendly message.

**The pain**: Error handling. Project 15 (Error Wall).

### 3. We have no logging

We don't log signups, logins, or DB queries.

**The pain**: Observability. Project 16 (Logger).

### 4. We have no REST structure

Our URLs are ad-hoc. `GET /posts` and `GET /users/:id/posts` are not consistent.

**The pain**: REST. Project 17 (REST Refactor).

### 5. We have no pagination

`GET /posts` returns all posts.

**The pain**: Pagination. Project 18 (Paginator).

### 6. We have no search

`GET /posts?search=hello` would be a slow `LIKE` query.

**The pain**: Search. Project 19 (Searcher).

### 7. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 8. We have no security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 9. We have no tests

We can't verify the database code works.

**The pain**: Tests. Project 36.

### 10. We have no rate limiting

A malicious client can hammer `/login` with thousands of attempts.

**The pain**: Rate limiting. Project 24.

---

## What This Project Forbids Us From Doing

This server can:

- Use a query builder for clean database code
- Generate SQL from JavaScript
- Migrate the schema with idempotent JavaScript

It cannot:

- Validate input strictly
- Handle errors gracefully
- Log requests
- Have REST-shaped URLs
- Paginate large lists
- Search with relevance
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically
- Be rate-limited

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 14 | The Validator | "I want to reject bad input with 400." |
| 15 | The Error Wall | "I want to handle errors with proper status codes." |
| 16 | The Logger | "I want to see what's happening." |
| 17 | The REST Refactor | "I want resource-shaped endpoints." |

Project 14 is the natural next step. We accept any input. We want to reject it with a 400 before it reaches the database.

---

## What You Should Do Now

1. **Read the code.** Notice the `db('users').where({...}).first()` pattern. The handlers are slightly different but the patterns are stable.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Try to insert a post with a non-existent user_id.** See how the foreign key error is propagated. Feel the pain of "no error handling."
4. **Try to sign up with an empty username.** See how it's accepted. Feel the pain of "no validation."
5. **When you are ready**, move to [Project 14: The Validator](../14-validator/).
6. **If anything is unclear**, do not proceed. The query builder is the foundation of every modern database layer. It must be solid.

---

## A Note on the Bigger Picture

You now have a *modern* data layer. Knex is a query builder. The patterns are universal. The handlers are clean.

From here, the path diverges:

- **Validation** (project 14): reject bad input
- **Error handling** (project 15): handle constraint violations
- **Logging** (project 16): observe the database
- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

The data layer is solid. The query builder is in place. The path continues.

# Project 15: The Error Wall

> *"Errors will happen. The question is: do they crash the process, or do they return a clean response?"*

Projects 10-14 have us handling happy paths. The user sends good input. The database responds. We return 200. Life is good.

But errors happen:

- The user sends a malformed JSON body (we return 400 — handled in project 14)
- The user signs up with a username that already exists (we return 409 — handled in project 10)
- The database is locked (SQLite SQLITE_BUSY)
- The database file is corrupt
- The token is expired (we return 401 — handled in project 09)
- The handler throws an unexpected error
- The database connection drops
- The process is out of memory

For some of these, we have specific handlers. For others, we don't. Without a generic error handler, Express's default is to:

1. Log the error to stderr
2. Return a 500 with an HTML stack trace (in dev) or a generic 500 (in prod)
3. The handler doesn't know what happened

We want a *consistent error response shape*. We want *all* errors to be JSON. We want *specific status codes* for known errors (validation 400, conflict 409, not found 404, unauthorized 401, forbidden 403). We want *generic 500* for unknown errors. We want *no stack traces leaked to clients* in production.

This project adds an **error wall**: a single error-handling middleware that catches everything, maps known errors to status codes, and returns a clean JSON response.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why do errors crash our responses? What is an error wall?
2. [The Thought](./THOUGHT.md) — How does Express handle errors? What are error classes?
3. [The Build](./BUILD.md) — Line-by-line construction of the error handler
4. [The Decisions](./DECISIONS.md) — Why a single error handler? Why not try/catch everywhere?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

An *error wall* is a single Express middleware that catches every error in the request pipeline. It uses Express's 4-argument middleware signature: `(err, req, res, next)`. When a handler calls `next(err)`, Express skips to the error wall. The error wall inspects the error, maps it to a status code (using `instanceof` for custom error classes or a `status` property), and returns a clean JSON response. The client never sees a stack trace in production. The error is logged server-side. The response shape is consistent.

---

## The Code

```js
// server.js
// ... imports and setup ...

class HttpError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

class NotFoundError extends HttpError {
  constructor(message = 'Not Found') {
    super(404, 'NOT_FOUND', message);
  }
}

class ConflictError extends HttpError {
  constructor(message = 'Conflict') {
    super(409, 'CONFLICT', message);
  }
}

class UnauthorizedError extends HttpError {
  constructor(message = 'Unauthorized') {
    super(401, 'UNAUTHORIZED', message);
  }
}

class ValidationError extends HttpError {
  constructor(issues) {
    super(400, 'VALIDATION', 'Validation failed');
    this.issues = issues;
  }
}

function errorHandler(err, req, res, next) {
  console.error(err);
  if (err instanceof HttpError) {
    const body = { error: err.message, code: err.code };
    if (err.issues) body.issues = err.issues;
    return res.status(err.status).json(body);
  }
  res.status(500).json({ error: 'Internal Server Error', code: 'INTERNAL' });
}

app.use(errorHandler);
```

Test it:

```bash
# Trigger a NotFoundError
curl http://localhost:3000/posts/9999
# {"error":"Not Found","code":"NOT_FOUND"}

# Trigger a ValidationError (handled by validate middleware)
curl -X POST http://localhost:3000/signup -H "Content-Type: application/json" -d '{"username":"a"}'
# {"error":"Validation failed","code":"VALIDATION","issues":[...]}

# Trigger an unexpected error (kill the database, then make a request)
# (returns 500 with a clean response, no stack trace leaked)
```

The pain of "I get a 500 with a stack trace" is solved. Errors are caught, mapped, and returned cleanly.

---

## What You Will Have Learned

- How Express's 4-argument middleware handles errors
- How to create custom error classes (extend `Error`)
- How to throw errors in handlers and have them caught
- How to map errors to status codes
- How to return a consistent error response shape
- How to avoid leaking stack traces in production

These are the foundations of *error handling*. From here, every project assumes a single error wall. The handlers throw; the wall catches.

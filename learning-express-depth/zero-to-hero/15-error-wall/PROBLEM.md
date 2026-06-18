# The Problem

> *"Errors are inevitable. The question is whether they take down the response or get caught at the wall."*

## Why Errors Break Things

In projects 10-14, our handlers do their best, but:

- A unique constraint violation throws an error inside `db('users').insert(...)`. The handler doesn't catch it. The error propagates to Express. Express's default is to return a 500 with an HTML stack trace.
- A database connection drop throws an error. Same.
- A bug in the handler (e.g., `undefined.foo`) throws. Same.
- A third-party API call fails. Same.

Without a generic error handler, every error becomes a 500 with a stack trace. The client sees the stack trace (in dev). The user is confused. The error is logged to stderr (somewhere). We have no consistent error response.

**The pain**: We want a single place to handle all errors. We want consistent JSON responses. We want specific status codes for known errors.

## What Pain Is This Solving?

Imagine the alternative. You have 30 handlers. Each handler does its own try/catch:

```js
app.post('/signup', async (req, res) => {
  try {
    const existing = await db('users').where({ username }).first();
    if (existing) throw new Error('Username taken');
    // ... insert ...
    res.json({ ... });
  } catch (err) {
    if (err.message === 'Username taken') {
      return res.status(409).json({ error: 'Username taken' });
    }
    console.error(err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});
```

This works. It's also repetitive. Every handler has the same try/catch boilerplate. The error logic is duplicated. The response shape is inconsistent (some return `{ error }`, others return `{ message }`).

**The fix**: a single error-handling middleware. The handler throws (or calls `next(err)`). The middleware catches. The response shape is consistent. The status codes are consistent.

## The Deeper Problem: Express's Error Handling

Express has a *built-in* error handling mechanism. Middleware with 4 arguments — `(err, req, res, next)` — is treated as an error handler. When a handler calls `next(err)`, Express skips to the next error handler.

If no error handler is registered, Express's default is:
1. Log to stderr
2. Send a 500 with the stack trace (in dev) or a generic 500 (in prod)

We can register our own error handler as the last `app.use(...)`. It catches all errors. It maps them to status codes. It returns JSON.

## What This Project Will Solve

This project will:

1. Add a base `HttpError` class with `status` and `code`
2. Add subclasses: `NotFoundError`, `ConflictError`, `UnauthorizedError`, `ValidationError`
3. Add an `errorHandler` middleware that catches everything
4. Update handlers to throw these errors instead of returning 4xx JSON
5. Update `validate` middleware to throw `ValidationError`
6. Update `authMiddleware` to throw `UnauthorizedError`

By the end, every error is caught by the wall. The response shape is `{ error, code, issues? }`. The status code is correct. No stack traces leak in production.

## What This Project Will *Not* Solve

- **Logging** — we still `console.error(err)`. Project 16 will add structured logging.
- **Sentry / error tracking** — out of scope. We'd send errors to Sentry in production.
- **Async error handling** — Express 4 doesn't automatically catch async errors. We need to wrap async handlers or use Express 5. Project 36 (tests) will address this.
- **Custom error pages** — out of scope. JSON only.
- **i18n for error messages** — out of scope.

## The Question This Project Answers

> *"How do I handle errors consistently across all endpoints?"*

If you can answer: "custom error classes, single error middleware, throw to fail, the wall catches and maps to status codes," you are ready for project 16.

# The Decisions

> *"Throw at the source. Catch at the wall. The wall is the last line of defense."*

## Decision 1: A single error wall, not try/catch in every handler

**Alternative**: Wrap each handler in try/catch.

**Why a wall**: Centralized logic. The response shape is consistent. The status code mapping is in one place. The handlers are simpler.

**Trade-off**: Requires a custom error class hierarchy. Requires the `asyncHandler` wrapper. We accept this for the cleanliness.

## Decision 2: Custom error classes, not `{ status, message }` objects

**Alternative**: Throw plain objects with `status` and `message`.

**Why classes**: `instanceof` checks. Stack traces. Inheritance. `err.code` is consistent across the hierarchy. Easier to extend.

**Trade-off**: A bit more code (the class definitions). We accept this for the structure.

## Decision 3: The `code` property is a string, not a number

**Alternative**: Use the HTTP status code as the code.

**Why a string: `code` is a *machine-readable identifier* (e.g., `NOT_FOUND`, `CONFLICT`). The status code is a number. They're different things. `code` is stable across versions; status codes could change.

**Trade-off**: Two ways to identify an error (status and code). We accept this for the explicitness.

## Decision 4: No stack traces in responses

**Alternative**: Include `err.stack` in the response (in dev).

**Why no: Stack traces can leak sensitive info (file paths, internal structure). We log them server-side but don't expose them. In a real app, you might expose in dev only.

**Trade-off**: Harder to debug from the client. We accept this for security.

## Decision 5: `console.error` for now, pino later

**Alternative**: Use pino (structured logger) from the start.

**Why console.error: Project 16 will add pino. We use `console.error` in this project as a placeholder. The wall catches; we just log.

**Trade-off**: The error format is unstructured. Project 16 will fix this.

## Decision 6: `asyncHandler` wrapper, not Express 5

**Alternative**: Use Express 5 (which catches async errors automatically).

**Why the wrapper: Express 5 is newer. Many tutorials and codebases still use Express 4. The wrapper is the standard pattern. We use it.

**Trade-off**: A bit of boilerplate (`asyncHandler(async (req, res) => ...)`). We accept this for compatibility.

## Decision 7: Default messages for error classes

```js
class NotFoundError extends HttpError {
  constructor(message = 'Not Found') { ... }
}
```

**Alternative**: Require a message every time.

**Why default: Common cases are short. `throw new NotFoundError()` is fine. We can override with a custom message: `throw new NotFoundError('Post 42 not found')`.

**Trade-off**: Inconsistent messages. We accept this for ergonomics.

## Decision 8: The wall is the last `app.use`

**Alternative**: Put the wall before some routes.

**Why last: The wall must catch everything. If a route is after the wall, errors in that route are not caught.

**Trade-off**: We must remember to add new routes *before* the wall. We do.

## Decision 9: 500 for unknown errors

**Alternative**: Include the original error message in the response.

**Why 500 with generic message: Don't leak internal errors. The original message could contain sensitive info (database table names, file paths). We log server-side; we return a clean message to the client.

**Trade-off**: Harder to debug. We accept this for security.

## Decision 10: No custom error pages

**Alternative**: Return HTML error pages.

**Why JSON: We're an API. The client is a program, not a human. JSON is the lingua franca. HTML would be wrong.

**Trade-off**: If a human hits the API in a browser, they see a JSON error. That's fine — it's an API.

---

## What We Did Not Decide

- **Sentry / error tracking** — out of scope (project 39, Observability)
- **i18n for error messages** — out of scope
- **Retry logic** — out of scope (project 26, Queue)
- **Rate limiting on errors** — out of scope (project 24, Rate Limiter)
- **Async error handling in Express 5** — we use the wrapper for compatibility
- **Custom error classes for specific databases** — out of scope
- **Stack traces in dev** — out of scope (could add later)
- **Error recovery / fallback responses** — out of scope

Each is a future decision.

---

## The Meta-Decision: Errors Are First-Class

For 14 projects, errors were an afterthought. The handler did its best. If something went wrong, the response was a 500 with a stack trace. The client had to parse the stack trace. The developer had to read it.

Now errors are *first-class*. They have classes. They have status codes. They have messages. The wall catches them. The response is clean. The developer logs them. The client gets a clear error.

This is the foundation of *robust APIs*. Every real API has an error wall. The patterns (custom errors, throw, catch, JSON response) are universal.

The next 25 projects will assume the error wall exists. The path diverges:

- **Logging** (project 16): structured logs
- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance
- **File upload** (project 20): accept files
- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse

The wall is built. The errors are caught. The path continues.

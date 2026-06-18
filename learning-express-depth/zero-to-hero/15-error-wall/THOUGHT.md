# The Thought

> *"Express's error handling is one middleware. Throw in a handler, catch in the wall. The wall is the last app.use. The wall is the safety net."*

## How Express Handles Errors

Express has a special signature for error-handling middleware:

```js
app.use((err, req, res, next) => {
  // err is the error passed by next(err) or thrown
  // ...
});
```

The 4-argument signature is the signal. When you call `next(err)` in any middleware or handler, Express skips to the next 4-argument middleware.

If you `throw` inside a synchronous handler, Express catches it and passes it to the error handler.

If you `throw` inside an **async** handler (project 13+), Express does *not* automatically catch it. The thrown error becomes an unhandled rejection. We need to either:
- Use `try/catch` in the async handler
- Wrap async handlers with a helper that catches and calls `next(err)`
- Use Express 5 (which catches async errors)

For this project, we'll use the wrapper approach (it's the standard).

### The Async Wrapper

```js
function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

app.post('/signup', asyncHandler(async (req, res) => {
  // ... if this throws, the error goes to errorHandler
}));
```

`asyncHandler` wraps an async function. If the function rejects, the rejection is caught and passed to `next(err)`. Express's error handler then catches it.

This is the standard pattern for async error handling in Express 4. Express 5 has it built-in.

## Custom Error Classes

We create a base `HttpError` class with `status` and `code` properties, then subclasses for specific errors:

```js
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
```

Each subclass has a default message and a status code. The `code` is a machine-readable string (e.g., `NOT_FOUND`, `CONFLICT`).

The `super(message)` call sets the `Error.message` property. We extend `Error` so these errors behave like regular errors (they have stack traces, they can be thrown, they can be caught).

## The Error Wall

```js
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

This is the *last* middleware. It catches everything.

The logic:

1. `console.error(err)` — log the error server-side. We'll improve this in project 16.
2. `if (err instanceof HttpError)` — known error. Use the status and code from the error.
3. If `err.issues` (from `ValidationError`), include them in the response.
4. Otherwise (unknown error), return a generic 500. **No stack trace leaked to the client.**

## How Handlers Use This

Instead of:

```js
app.post('/signup', async (req, res) => {
  if (existing) {
    return res.status(409).json({ error: 'username already taken' });
  }
  if (!user) {
    return res.status(404).json({ error: 'Not Found' });
  }
});
```

We write:

```js
app.post('/signup', async (req, res) => {
  if (existing) {
    throw new ConflictError('username already taken');
  }
  if (!user) {
    throw new NotFoundError('User not found');
  }
});
```

The handler throws. Express's async wrapper catches. The error wall maps to a status code. The response is sent.

This is *much* cleaner. The handler focuses on logic, not on response formatting. The response formatting is centralized.

## The Updated `validate` Middleware

```js
function validate(schema) {
  return (req, res, next) => {
    try {
      req.validated = schema.parse(req.body);
      next();
    } catch (err) {
      if (err.issues) {
        return next(new ValidationError(err.issues));
      }
      next(err);
    }
  };
}
```

We pass the `ValidationError` to `next(err)`. The error wall catches it. The response is a 400 with the issues.

## The Updated `authMiddleware`

```js
function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) {
    return next(new UnauthorizedError('missing or invalid authorization header'));
  }
  const token = auth.slice(7);
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (err) {
    return next(new UnauthorizedError('invalid or expired token'));
  }
}
```

Same pattern. We throw `UnauthorizedError` instead of returning 401 JSON.

## Common Confusions (read these)

**Confusion 1: "Why not just use try/catch in every handler?"**
You could. For 5 handlers, it's fine. For 50, it's repetitive. The error wall centralizes the logic.

**Confusion 2: "Why custom error classes and not just `{ status, message }` objects?"**
Objects don't have stack traces. They're harder to identify (`err.code === 'NOT_FOUND'` vs `err instanceof NotFoundError`). Classes give you `instanceof` and stack traces.

**Confusion 3: "What if I throw a non-HttpError?"**
The error wall returns a generic 500. The stack trace is logged server-side but not leaked to the client. Safe.

**Confusion 4: "Why not include the stack trace in dev?"**
We could. `if (process.env.NODE_ENV === 'development') body.stack = err.stack;`. For this project, we don't. In a real app, you might.

**Confusion 5: "Why is `errorHandler` last?"**
Express processes middleware in order. The error wall is the last `app.use`. It catches everything that came before. If you put a normal middleware after it, that middleware is unreachable for errors.

**Confusion 6: "What about Express 5?"**
Express 5 catches async errors automatically. You don't need `asyncHandler`. But Express 5 was released in late 2024 and adoption is still ramping up. For now, we use the wrapper.

**Confusion 7: "What if I want to return a specific message for a known error?"**
The error class constructor takes a message. `throw new NotFoundError('Post 42 not found')`. The error wall returns `{ error: 'Post 42 not found', code: 'NOT_FOUND' }`.

**Confusion 8: "What about database errors?"**
We could catch them and map to specific errors. For example, a unique constraint violation could be a `ConflictError`. We don't do this in the project; the wall treats them as 500s. In a real app, you'd map.

## What We Are About to Build

A ~150-line Express app that:

1. Has the same auth and post flow as project 14
2. Has a `HttpError` base class and 4 subclasses
3. Has an `errorHandler` middleware (the wall)
4. Uses an `asyncHandler` wrapper for async routes
5. Handlers throw errors instead of returning 4xx JSON
6. `validate` middleware throws `ValidationError`
7. `authMiddleware` throws `UnauthorizedError`

The handlers are cleaner. The error logic is centralized. The response shape is consistent.

In [BUILD.md](./BUILD.md) we will go line by line.

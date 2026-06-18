# The Build

> *"Throw at the source. Catch at the wall. The wall is the last line of defense."*

We are going to add an error wall. The change from project 14: introduce custom error classes, an `asyncHandler` wrapper, and an `errorHandler` middleware. The handlers throw instead of returning 4xx JSON.

## Setup

```bash
npm install knex better-sqlite3 zod
```

(If you've been following along, you already have these.)

## The File

Create `server.js`. Fill it in. The structure is the same as project 14, with the new error handling pieces.

---

## Lines 1-22: The Imports, App, and Database (Same as Project 14)

```js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const knex = require('knex');
const { z } = require('zod');

const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const app = express();
app.use(express.json());

const db = knex({...});

async function migrate() {...}

migrate().then(() => {
  app.listen(3000, () => console.log('Server listening on http://localhost:3000'));
});
```

Same as project 14.

---

## Lines 24-58: The Error Classes (NEW)

```js
class HttpError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

class ValidationError extends HttpError {
  constructor(issues) {
    super(400, 'VALIDATION', 'Validation failed');
    this.issues = issues;
  }
}

class UnauthorizedError extends HttpError {
  constructor(message = 'Unauthorized') {
    super(401, 'UNAUTHORIZED', message);
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

function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}
```

### `HttpError` (base)

The base class. Sets `status` and `code`. Subclasses extend it.

### Subclasses

Each subclass has a default message and a fixed status code. `ValidationError` adds `issues`. We don't expose the base `HttpError` — only the subclasses are thrown.

### `asyncHandler`

Wraps an async function. If the function rejects, the rejection is caught and passed to `next(err)`. Express's error handler then catches it.

This is necessary because Express 4 doesn't catch async errors automatically.

---

## Lines 60-72: The Error Wall (NEW)

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

### What it does

The 4-argument middleware. Catches every error.

1. `console.error(err)` — log the error server-side
2. If `err instanceof HttpError` — known error, use the status and code
3. If `err.issues` (from `ValidationError`) — include them
4. Otherwise — generic 500, no stack trace leaked

### Why `app.use(errorHandler)` last

Express processes middleware in order. The error wall is the last `app.use`. It catches everything that came before.

---

## Lines 74-95: The Schemas and `validate` Middleware (Updated)

```js
const signupSchema = z.object({...});
const loginSchema = z.object({...});
const postSchema = z.object({...});

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

The `validate` middleware now throws `ValidationError` (via `next(err)`) instead of returning 400 JSON directly. The error wall catches it.

---

## Lines 97-105: The `authMiddleware` (Updated)

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

Same as project 14, but uses `next(new UnauthorizedError(...))` instead of `return res.status(401)...`.

---

## Lines 107-160: The Handlers (Updated to Throw)

### Signup

```js
app.post('/signup', validate(signupSchema), asyncHandler(async (req, res) => {
  const { username, password, email } = req.validated;
  const existing = await db('users').where({ username }).first();
  if (existing) {
    throw new ConflictError('username already taken');
  }
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db('users').insert({ username, hash, email: email || null, created_at: Date.now() });
  res.status(201).json({ id, username, email: email || null });
}));
```

### What changed

- Wrapped in `asyncHandler(...)` for async error catching
- `if (existing) return res.status(409)...` → `if (existing) throw new ConflictError(...)`

The handler is cleaner. It throws; the wall catches.

### Login, /me, post routes

Same pattern. `asyncHandler(...)` wrapper. `throw new ...Error(...)` for known errors.

### Post fetch

```js
app.get('/posts/:id', asyncHandler(async (req, res) => {
  const post = await db('posts')
    .join('users', 'posts.user_id', 'users.id')
    .select('posts.*', 'users.username as author')
    .where('posts.id', req.params.id)
    .first();
  if (!post) {
    throw new NotFoundError('Post not found');
  }
  res.json(post);
}));
```

The handler throws `NotFoundError` instead of returning 404 JSON. The wall catches.

---

## The Full File

The full file is shown in the README. The new pieces are the error classes, the `asyncHandler`, the `errorHandler`, and the use of `throw` in handlers.

---

## Run It

```bash
node server.js

# Trigger a ValidationError
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"a"}'
# {"error":"Validation failed","code":"VALIDATION","issues":[{"path":"username","message":"String must contain at least 3 character(s)"}]}

# Trigger a ConflictError
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long"}'
# (after alice is signed up)
# {"error":"username already taken","code":"CONFLICT"}

# Trigger a NotFoundError
curl http://localhost:3000/posts/9999
# {"error":"Post not found","code":"NOT_FOUND"}

# Trigger an UnauthorizedError
curl http://localhost:3000/posts/1 -X POST \
  -H "Content-Type: application/json" \
  -d '{"title":"x","body":"y"}'
# {"error":"missing or invalid authorization header","code":"UNAUTHORIZED"}

# Trigger a 500 (e.g., kill the database mid-request, or trigger a bug)
# (returns 500 with no stack trace)
```

Every error returns the same shape: `{ error, code, issues? }`. The status code is correct. The error message is friendly.

---

## Experiments

### Experiment 1: Add a new error class

```js
class ForbiddenError extends HttpError {
  constructor(message = 'Forbidden') {
    super(403, 'FORBIDDEN', message);
  }
}
```

Use it: `throw new ForbiddenError('You cannot delete this post')`. The wall returns 403.

### Experiment 2: Throw a non-HttpError

```js
app.get('/boom', (req, res) => {
  throw new Error('boom');
});
```

The wall returns 500 with `{ error: 'Internal Server Error', code: 'INTERNAL' }`. The original error is logged to stderr.

### Experiment 3: Custom error in async handler

```js
app.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await db('users').where({ id: req.params.id }).first();
  if (!user) throw new NotFoundError('User not found');
  res.json({ id: user.id, username: user.username });
}));
```

Throws are caught by `asyncHandler`, passed to `next(err)`, caught by the wall. Status 404 with a clean response.

### Experiment 4: Log the stack trace

In the error wall:

```js
function errorHandler(err, req, res, next) {
  console.error(err.stack);
  // ...
}
```

Now we log the full stack trace. The client still gets a clean response.

### Experiment 5: Add metadata to errors

```js
class ValidationError extends HttpError {
  constructor(issues, metadata) {
    super(400, 'VALIDATION', 'Validation failed');
    this.issues = issues;
    this.metadata = metadata;
  }
}
```

Pass extra data with the error. The wall can include it in the response.

---

## Summary

You now have an error wall. Every error is caught, mapped to a status code, and returned as JSON. The handlers are cleaner. The response shape is consistent. No stack traces leak to clients.

This is the foundation of *error handling*. From here, every project assumes a single error wall. The handlers throw; the wall catches.

In project 16, we will add logging. We will replace `console.error(err)` with structured logging (pino). We will log every request with timing, status, and metadata.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

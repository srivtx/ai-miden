# The Build

> *"Logs are data. Data is JSON. JSON is queryable."*

We are going to add structured logging with pino. The change from project 15: replace `console.error(err)` with `req.log.error(...)`, add `pino-http` for request logging, and add log lines for important events in handlers.

## Setup

```bash
npm install knex better-sqlite3 zod pino pino-http pino-pretty
```

The new dependencies are `pino`, `pino-http`, and `pino-pretty`.

## The File

Create `server.js`. Fill it in. The structure is the same as project 15, with logging added.

---

## Lines 1-7: The Imports

```js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const knex = require('knex');
const { z } = require('zod');
const pino = require('pino');
const pinoHttp = require('pino-http');
```

`pino` and `pino-http` are new.

---

## Lines 9-14: The Logger

```js
const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'production' ? undefined : { target: 'pino-pretty' },
});
```

### What it does

Creates a pino logger instance. Configured with:

- `level` — minimum level to log. `'info'` is the default. Set to `'debug'` for verbose logs, `'warn'` for quiet.
- `transport` — `pino-pretty` formats JSON for humans. Used in dev. In production, we omit the transport (raw JSON).

`process.env.LOG_LEVEL` and `process.env.NODE_ENV` are environment variables. We don't have a `.env` setup yet; we'll add that in a later project.

---

## Lines 16-30: The App, Database, and Migration (Same as Project 15)

```js
const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const app = express();
app.use(express.json());
app.use(pinoHttp({ logger }));  // <-- NEW

const db = knex({...});

async function migrate() {...}

migrate().then(() => {
  app.listen(3000, () => logger.info('Server listening on http://localhost:3000'));  // <-- changed
});
```

### The new line: `app.use(pinoHttp({ logger }))`

This is the request logger middleware. It:

1. Generates a request ID (`req.id`)
2. Logs the request start (debug level)
3. Logs the request completion with status and duration (info level)
4. Logs the request error (error level)
5. Adds a child logger to `req.log` (with the request ID bound)

After this middleware, every handler can use `req.log.info(...)`.

We register it *before* the routes. So it logs every request.

### The changed line: `logger.info(...)`

We use `logger.info(...)` instead of `console.log(...)` for the startup message. The structured logger handles it.

---

## Lines 32-95: The Error Classes, Schemas, and Validation (Same as Project 15)

The error classes, schemas, `validate` middleware, and `authMiddleware` are unchanged. They don't log directly — the error wall does.

---

## Lines 97-115: The Error Wall (Updated)

```js
function errorHandler(err, req, res, next) {
  req.log.error({ err, code: err.code, status: err.status }, err.message);
  if (err instanceof HttpError) {
    const body = { error: err.message, code: err.code };
    if (err.issues) body.issues = err.issues;
    return res.status(err.status).json(body);
  }
  res.status(500).json({ error: 'Internal Server Error', code: 'INTERNAL' });
}
```

### What changed

`console.error(err)` → `req.log.error({ err, code, status }, msg)`

`req.log` is a child logger with the request ID bound. The error log line includes:

- `err` — the error object (serialized: message, stack, name)
- `code` — the error code (e.g., `NOT_FOUND`)
- `status` — the HTTP status
- `msg` — the error message (the second argument)

The log line is JSON:

```json
{"level":50,"reqId":"abc-123","err":{"type":"NotFoundError","message":"Post not found","stack":"..."},"code":"NOT_FOUND","status":404,"msg":"Post not found"}
```

In dev (with `pino-pretty`), this is rendered as:

```
[15:00:00.000] ERROR (abc-123): Post not found
    code: "NOT_FOUND"
    status: 404
    err: NotFoundError: Post not found
        at ...
```

---

## Lines 117-180: The Handlers (Updated to Use `req.log`)

### Signup

```js
app.post('/signup', validate(signupSchema), asyncHandler(async (req, res) => {
  const { username, password, email } = req.validated;
  const existing = await db('users').where({ username }).first();
  if (existing) {
    req.log.warn({ username }, 'signup conflict');
    throw new ConflictError('username already taken');
  }
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db('users').insert({ username, hash, email: email || null, created_at: Date.now() });
  req.log.info({ userId: id, username }, 'user created');
  res.status(201).json({ id, username, email: email || null });
}));
```

### What changed

- `req.log.warn({ username }, 'signup conflict')` — log a warning when a user tries to sign up with a taken username. The username is in the context.
- `req.log.info({ userId, username }, 'user created')` — log an info when a user is created. The user ID and username are in the context.

These log lines are queryable: "show me all signup conflicts" or "show me all signups by user X".

### Other handlers

Similar additions. `req.log.info(...)` for important events. `req.log.warn(...)` for recoverable issues.

---

## The Full File

The full file is shown in the README. The new pieces are the logger, the `pino-http` middleware, the updated error wall, and the log lines in handlers.

---

## Run It

```bash
npm install knex better-sqlite3 zod pino pino-http pino-pretty
NODE_ENV=development node server.js

# Make some requests
curl http://localhost:3000/
# (in dev, pino-pretty formats the log)
# [15:00:00.000] INFO (req-1): request completed
#     req: { method: "GET", url: "/" }
#     res: { statusCode: 200 }
#     responseTime: 2

# Trigger an error
curl http://localhost:3000/posts/9999
# [15:00:01.000] ERROR (req-2): Post not found
#     err: NotFoundError: Post not found
#         at ...
#     code: "NOT_FOUND"
#     status: 404

# Sign up
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long"}'
# [15:00:02.000] INFO (req-3): user created
#     userId: 1
#     username: "alice"
# [15:00:02.000] INFO (req-3): request completed
#     req: { method: "POST", url: "/signup" }
#     res: { statusCode: 201 }
#     responseTime: 50
```

Every request is logged. Every error is logged with context. The request ID ties them together.

---

## Experiments

### Experiment 1: Log level

```bash
LOG_LEVEL=debug node server.js
```

Now debug-level logs are also shown (including request start, before the response).

### Experiment 2: Production mode

```bash
NODE_ENV=production node server.js
```

Raw JSON to stdout. No pretty-printing. This is what production looks like.

### Experiment 3: Log a child context

```js
const childLog = req.log.child({ userId: req.user.userId });
childLog.info('doing something');
```

The child logger binds `userId` to every log line. Useful for handlers that perform multiple actions on behalf of a user.

### Experiment 4: Use `req.log` in middleware

```js
function myMiddleware(req, res, next) {
  req.log.info('middleware ran');
  next();
}
```

Every log line in this middleware includes the request ID (because `req.log` is a child logger).

### Experiment 5: Disable pino-pretty

Comment out the `transport` option. The logs are raw JSON. Useful for piping to `jq` or another tool.

```bash
node server.js | jq 'select(.level >= 50)'
# Only show errors
```

### Experiment 6: Ship logs to a file

```bash
node server.js > app.log 2>&1
```

Logs go to `app.log`. In production, a log shipper (Filebeat, Promtail) would tail this file and send to a log aggregator.

---

## Summary

You now have structured logging. Every request is logged. Every error is logged with context. The request ID ties everything together. The logs are JSON, queryable, and aggregatable.

This is the foundation of *observability*. From here, every project assumes structured logging. The patterns (`req.log.info(...)`, `pino-http` middleware) are universal.

In project 17, we will refactor the URLs to be REST-shaped. We will use resource-oriented patterns, consistent naming, and proper HTTP semantics.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

# The Thought

> *"Logs are data. Data is JSON. JSON is queryable. Queryable is debuggable."*

## What Structured Logging Is

Structured logging is a logging practice where each log line is a *machine-parseable data structure* (usually JSON), not a free-form string. The fields are consistent. The values are typed. The data can be queried.

Example structured log (JSONL):

```json
{"level":30,"time":1700000000000,"msg":"request completed","req":{"method":"GET","url":"/"},"res":{"statusCode":200},"responseTime":12,"reqId":"abc-123"}
```

Same information as a free-form log, but:

- `level` is a number (10=trace, 20=debug, 30=info, 40=warn, 50=error, 60=fatal)
- `time` is a Unix timestamp
- `msg` is a human-readable summary
- `req` is a nested object with method and URL
- `res` is a nested object with status code
- `responseTime` is in milliseconds
- `reqId` is a unique identifier

A log aggregator can:
- Filter: `level >= 50` (errors only)
- Filter: `req.url = "/users/42"`
- Aggregate: `count by statusCode per minute`
- Alert: `error rate > 5%`

## Pino: The Fastest JSON Logger

`pino` is the de-facto structured logger for Node. It is:

- **Fast** — 5x faster than winston, the main alternative
- **JSON by default** — every log line is JSON
- **Child loggers** — bind context (request ID, user ID) to a logger
- **Pretty printing** — `pino-pretty` formats for development

Pino is *low-level*. It writes JSON lines to a stream (default: stdout). It doesn't do file rotation, log shipping, or anything fancy. Those concerns are handled by infrastructure.

## pino-http: Request Logging

`pino-http` is Express middleware that logs every request. It:

1. Generates a unique request ID (`req.id`)
2. Logs the request start (debug level)
3. Logs the request completion with status and duration (info level)
4. Logs the request error (error level)
5. Adds the request ID to `req.log` (a child logger with the request ID bound)

After `pino-http`, every handler can do `req.log.info(...)` and the log line will include the request ID.

## Request IDs

A *request ID* (or correlation ID) is a unique identifier for a request. It's generated when the request arrives and propagated through the system. Every log line related to the request includes the ID.

If a customer reports an error, they can give you the request ID. You search the logs for that ID. You see everything that happened during that request.

`pino-http` uses `crypto.randomUUID()` by default. The ID is in `req.id`.

## The Code

```js
const pino = require('pino');
const pinoHttp = require('pino-http');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'production' ? undefined : { target: 'pino-pretty' },
});

const app = express();
app.use(pinoHttp({ logger }));
```

`pinoHttp({ logger })` is middleware. It wraps the request with a child logger (`req.log`). It logs the request on response.

`pino({ level, transport })` configures pino. In dev, we use `pino-pretty` for human-readable output. In production, we use raw JSON (no transport).

## Logging in Handlers

```js
app.post('/signup', validate(signupSchema), asyncHandler(async (req, res) => {
  const { username, password, email } = req.validated;
  const existing = await db('users').where({ username }).first();
  if (existing) {
    req.log.warn({ username }, 'signup conflict');
    throw new ConflictError('username already taken');
  }
  // ... insert ...
  req.log.info({ userId: id, username }, 'user created');
  res.status(201).json({ id, username, email: email || null });
}));
```

`req.log` is a child logger with the request ID bound. Every log line includes the request ID automatically.

We can log with context: `{ userId, username }`. The structured data is queryable.

## Logging in the Error Wall

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

`req.log.error({ err, ... }, msg)` logs the error with context. `err` is serialized to a stack trace and message. The structured data is queryable.

## Common Confusions (read these)

**Confusion 1: "Why pino and not winston?"**
Pino is faster (5x). Pino is JSON-only. Winston is more flexible (formats, transports) but slower. For most apps, pino is the right choice. Winston is for legacy or specific formatting needs.

**Confusion 2: "Why JSON and not pretty in production?"**
JSON is parseable. Pretty is for humans. In production, you don't read the logs — an aggregator does. The aggregator wants JSON.

**Confusion 3: "What about file logging?"**
We log to stdout. In production, a process manager (systemd, Docker, Kubernetes) captures stdout and writes to a file or ships to a log aggregator. We don't write to files directly — that's the process manager's job.

**Confusion 4: "How do I include the user ID in every log line?"**
Use a child logger: `req.log.child({ userId: req.user.userId })`. Every log line with this child includes the user ID.

**Confusion 5: "What about sensitive data?"**
Don't log passwords, tokens, or PII. We log `username` (not `password`) and `userId` (not `email`). Be careful.

**Confusion 6: "What is `pino-pretty`?"**
A separate package that formats pino's JSON output for humans. Used in development. In production, you use raw JSON.

**Confusion 7: "What if my log line is too long?"**
Pino doesn't limit line length by default. If a log line is too long (e.g., a giant stack trace), it can slow down the aggregator. Pino handles this by truncating if needed.

**Confusion 8: "What is `level: 30`?"**
Pino uses numeric levels. 10=trace, 20=debug, 30=info, 40=warn, 50=error, 60=fatal. The `level` config is the minimum level to log. `level: 'info'` logs info and above (info, warn, error, fatal).

## What We Are About to Build

A ~150-line Express app that:

1. Uses pino for structured logging
2. Uses pino-http for request logging
3. Logs every request with method, URL, status, duration, request ID
4. Logs every error with stack trace and request context
5. Pretty-prints logs in development
6. The error wall uses `req.log` instead of `console.error`

The handlers are slightly different (we use `req.log.info(...)` for important events). The error wall is updated to use `req.log.error(...)`.

In [BUILD.md](./BUILD.md) we will go line by line.

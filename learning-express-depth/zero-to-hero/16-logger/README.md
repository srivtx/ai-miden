# Project 16: The Logger

> *"Console.log is for debugging. Production needs structured logs."*

In project 15, our error wall calls `console.error(err)`. That's unstructured. We can't search, filter, or analyze. We don't log successful requests, response times, or request IDs.

This project introduces **structured logging** with **pino** — the fastest JSON logger for Node. We replace `console.log` and `console.error` with `logger.info(...)` and `logger.error(...)`. Every log line is a JSON object with consistent fields: `level`, `time`, `msg`, plus any context we add (request ID, user ID, status, duration, etc.).

We also add a **request logger middleware** that logs every incoming request and its response. The log includes the method, URL, status code, response time, and a unique request ID. In production, we'd ship these logs to a log aggregator (Datadog, ELK, CloudWatch).

By the end, every event in the server is logged in a structured, queryable format.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is console.log not enough? What is structured logging?
2. [The Thought](./THOUGHT.md) — How does pino work? What is a request ID?
3. [The Build](./BUILD.md) — Line-by-line construction of the logger
4. [The Decisions](./DECISIONS.md) — Why pino? Why not winston? Why JSON?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Structured logging means every log line is a JSON object (or similar machine-parseable format) with consistent fields. `pino` is the de-facto structured logger for Node. It writes JSON lines to stdout (or a file). A request logger middleware logs every request with method, URL, status, duration, and a request ID. The error wall logs errors with stack traces. Production ships these logs to a log aggregator.

---

## The Code

```js
// server.js
const pino = require('pino');
const pinoHttp = require('pino-http');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'production' ? undefined : { target: 'pino-pretty' },
});

const app = express();
app.use(express.json());
app.use(pinoHttp({ logger }));

// ... handlers throw HttpError; the wall logs and returns ...

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

Setup:

```bash
npm install knex better-sqlite3 zod pino pino-http pino-pretty
node server.js
```

Test it:

```bash
# Make some requests
curl http://localhost:3000/
# {"level":30,"time":...,"pid":...,"hostname":"...","req":{"method":"GET","url":"/","headers":{...}},"res":{"statusCode":200},"responseTime":2,"msg":"request completed"}

# Trigger an error
curl http://localhost:3000/posts/9999
# {"level":50,"time":...,"err":{"type":"NotFoundError","message":"Post not found",...},"req":{...},"res":{"statusCode":404},"msg":"request errored"}
```

The pain of "I have no visibility into production" is solved. Every request is logged. Every error is logged with context.

---

## What You Will Have Learned

- What structured logging is (JSON lines, consistent fields)
- How pino works (the fastest JSON logger for Node)
- How `pino-http` adds request logging
- What a request ID is (unique identifier per request)
- How to log errors with context (stack trace, request, user)
- Why structured logs are better than console.log

These are the foundations of *observability*. From here, every project assumes structured logging.

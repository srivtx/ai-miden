# The Decisions

> *"Every choice has an alternative. Here is why we chose what we chose."*

This document is short. The server is 30 lines. The decisions are few but they matter.

## Decision 1: `node:http` and not Express

**Alternative**: `npm install express`, then `const express = require('express'); const app = express(); app.get('/', (req, res) => res.send('Hello')); app.listen(3000);`

**Why we didn't choose it**: This is the foundation. Express is a *decoration* on top of `node:http`. If we start with Express, we never see the substrate. We never understand what `app.listen` actually does. We never appreciate what middleware is. We never feel the pain that motivated Express to exist.

**Trade-off**: Our code is uglier. There is no `app.get` shorthand. We have to manually set status and headers. The handler signature is `(req, res)` instead of Express's slightly-different `(req, res) =>` — wait, it's the same. OK, the trade-off is that we have to write more code. But we understand it.

**When this changes**: Project 07. By then, we will have written a router, a body parser, a cookie parser, a static file server, all by hand. We will be tired. Express will arrive as a *relief*, not a *mystery*. That is the right time to adopt a framework.

## Decision 2: Plain function handler, not class-based

**Alternative**: A `class Server { constructor() { ... } handle(req, res) { ... } }`.

**Why we didn't choose it**: JavaScript's class system is fine, but for a single-route server it is overkill. A function is the smallest unit that does the work. Project 02 (Router) will introduce a *map* of routes, which is a more useful abstraction than a class. We don't need OOP for this.

**Trade-off**: If we later need to manage server state (e.g., a counter, a connection pool), we'd reach for a class. But for now, a function is enough. YAGNI.

## Decision 3: Port 3000

**Alternatives**: 80, 8080, 8000, 5000, 4000.

**Why 3000**: Convention. Node communities use 3000. React dev servers use 3000. Rails uses 3000. It is the "I am a dev server" port. You can use 8000 (Python's convention), or 8080 (a common alternative), or anything above 1024. We pick 3000 because it is the most common in JavaScript tutorials.

**Trade-off**: None, really. It is arbitrary. But consistency across projects in this path makes life easier.

## Decision 4: No `package.json`

**Alternatives**: Create a `package.json` with `name`, `version`, `scripts.start = "node server.js"`, etc.

**Why we didn't**: This project has zero dependencies. There is nothing to install. Creating a `package.json` is busywork. We will create one in project 02 (when we add Express) and never look back.

**Trade-off**: To run the project, you must remember `node server.js`. We accept this because the alternative (`npm start` for a 30-line file) is more friction than it's worth.

## Decision 5: Synchronous startup, no graceful shutdown

**Alternatives**: Handle `SIGINT`, close the server gracefully, drain in-flight requests, then exit.

**Why we didn't**: The server has no state, no in-flight requests we care about, and one process. Pressing Ctrl+C in a dev environment is fine. Production graceful shutdown is project 38 (Pipeline).

**Trade-off**: If we were running this in production behind a load balancer, we'd want a SIGTERM handler that drains. But that is project 38. Not now.

## Decision 6: `res.end()` with the body, not `res.write()` + `res.end()`

**Alternative**: `res.write('Hello, world.\n'); res.end();`

**Why we didn't**: For a single-chunk body, `res.end(body)` is the same as `res.write(body); res.end()`. It is one line shorter. The behavior is identical. We'll use the longer form in project 20 (Uploader) when we stream a file in chunks.

**Trade-off**: None. Just style.

## Decision 7: No `Content-Length` header

**Alternative**: `res.setHeader('Content-Length', body.length);`

**Why we didn't**: Node computes `Content-Length` for you when you call `res.end(string)`. Setting it manually is redundant. The only time you need to set it manually is when you use `res.write()` for chunked transfer encoding, which is rare. We'll discuss this in project 05 (Body Parser) and project 20 (Uploader).

**Trade-off**: None for this project. We'll revisit in project 20.

## Decision 8: No HTTPS

**Alternative**: `const https = require('node:https'); const server = https.createServer(options, handler);`

**Why we didn't**: HTTPS requires a TLS certificate. Getting one for development is friction (`mkcert`, self-signed, etc.). For learning HTTP semantics, plain HTTP is enough. We will discuss TLS in a later project (probably project 38, Pipeline, or a bonus).

**Trade-off**: A real production server speaks HTTPS. But that's a project for later. For now, we are learning the *protocol*, not the *transport*.

---

## What We Did Not Decide (Because the Question Doesn't Arise Yet)

- **Logging framework** (pino, winston) — not needed for 1 route
- **Error handling** — we throw, Node catches, we move on (project 15)
- **Environment variables** (`.env`, `dotenv`) — port is hardcoded (project 14+)
- **Async middleware** — not needed yet
- **Routing library** — built in project 02
- **Body parser** — built in project 05
- **Static file serving** — built in project 03 or later

Each of these is a future decision. We will face them when their absence hurts.

---

## The Meta-Decision: This Project Is Boring On Purpose

This is the most boring project in the path. It does one thing, and that one thing is "respond with the same string every time." There is no database, no auth, no routing, no business logic.

That is the point. By the time you reach project 40, your server will have 50,000 lines of code, and you will not be able to hold it all in your head. The only way to manage that complexity is to understand the foundation so deeply that it is *invisible* to you. You don't think about `res.end()` anymore. You don't think about `Content-Type`. You just write.

This project is where that foundation is built. It is boring so that everything after it is interesting.

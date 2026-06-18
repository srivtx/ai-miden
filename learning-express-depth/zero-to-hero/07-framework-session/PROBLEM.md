# The Problem

> *"You have written a router. You have written a body parser. You have written a cookie parser. You have written a session store. You are now the maintainer of a micro-framework."*

## Why Adopt a Framework

For 6 projects, we have built our server from scratch. The dispatch is now ~30 lines:

```js
const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split('?');
  req.query = Object.fromEntries(new URLSearchParams(queryString || ''));
  req.cookies = parseCookies(req.headers.cookie);

  const chunks = [];
  req.on('data', (chunk) => chunks.push(chunk));
  req.on('end', () => {
    // parse body, dispatch
  });
});
```

This is a *framework*. It is small. It works. It is also *limited*.

Every new feature we want to add — validation, auth, logging, error handling, request IDs, rate limiting, CORS, compression — would require either:

1. Adding more code to the dispatch (which would grow to 100+ lines)
2. Adding a wrapper around the handler (which is what middleware is)

Express *is* the wrapper approach. It is the most popular Node framework, used by millions of apps. It has battle-tested middleware for everything we need. We don't need to write it.

## What Pain Is This Solving?

Imagine the alternative. We want to add logging. Now we add to the dispatch:

```js
console.log(`${req.method} ${req.url}`);
```

We want to add request IDs:

```js
req.id = crypto.randomUUID();
```

We want to add error handling:

```js
try { ... } catch (err) { ... }
```

We want to add auth checks:

```js
const session = SESSIONS.get(req.cookies.sessionId);
if (!session && req.url.startsWith('/api/')) { ... }
```

Each of these goes in the dispatch. After 5 features, the dispatch is 100 lines. After 10, it's unmaintainable.

**The pain**: Reinventing the framework. We need a real framework.

## The Deeper Problem: Separation of Mechanism and Policy

The dispatch is *mechanism*. It does:
- Parse the URL
- Parse cookies
- Parse the body
- Look up the route
- Dispatch

These are *general* concerns. They apply to every request. They don't change based on the URL or the user.

The handlers are *policy*. They do:
- Validate the input
- Check authentication
- Read/write the database
- Return the response

These are *specific* concerns. They vary by URL.

The dispatch should be *small* and *general*. The handlers should be *focused* on the business logic. When the dispatch grows to handle authentication, validation, and logging, it conflates mechanism and policy.

**Middleware** is the answer. The dispatch is a *chain* of small functions. Each function does one thing. Each can be added or removed. The chain composes.

This is the *middleware pattern*, and it is the heart of Express (and Koa, Fastify, Hono, etc.).

## What This Project Will Solve

This project will:

1. Replace our hand-rolled dispatch with Express
2. Replace our hand-rolled body parser with `express.json()`
3. Replace our hand-rolled cookie parser with `cookie-parser`
4. Replace our hand-rolled session store with `express-session`
5. Use the same handler interface: `(req, res) => { ... }`
6. Use the same patterns: `req.body`, `req.query`, `req.cookies`, `req.session`

By the end, our server is ~30 lines of Express, replacing ~90 lines of hand-rolled code. The behavior is the same. The code is simpler.

## What This Project Will *Not* Solve

- **Real auth with passwords** — we still have `username` only. Project 08 (Bcrypt).
- **Stateless tokens** — sessions are in memory. Project 09 (JWT).
- **Persistent storage** — sessions are in memory. Project 10 (SQLite).
- **Validation** — we accept any body. Project 14 (Validator).
- **Error handling for handler errors** — we still don't catch. Project 15 (Error Wall).
- **CORS** — we still don't have it. Project 57.

## The Question This Project Answers

> *"When should I stop building my own and adopt a framework?"*

The answer: when the framework's complexity is *less* than the complexity of reinventing it. By project 06, we have reinvented the framework. Now we adopt it. The framework is no longer mystery; it is the dispatch we built, with more features.

## Why Now, Not Earlier

We could have started with Express in project 01. We didn't, because we wanted to *understand* what Express does. Now we know. The mystery is gone. Express is just our dispatch, plus middleware, plus helpers.

If we had started with Express, we would have used `req.body` and `req.cookies` and `req.session` as *magic*. Now we know they are *conventions* — properties added to `req` by middleware. The same conventions we built by hand.

The path was: build the foundation by hand → understand the foundation → adopt the framework that *is* the foundation.

This is the order that produces understanding. The opposite order produces *users* of frameworks, not *builders* of systems.

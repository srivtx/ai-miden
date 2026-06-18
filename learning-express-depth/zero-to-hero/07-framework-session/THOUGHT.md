# The Thought

> *"Middleware is a chain of functions. Each one runs in order. Each can short-circuit. The chain ends with a handler. That is the whole pattern."*

## What Middleware Is

A middleware is a function with the signature `(req, res, next) => { ... }`. It runs *before* the route handler. It can:

1. **Read the request** (`req.headers`, `req.body`, etc.)
2. **Modify the request** (`req.user = ...`, `req.id = ...`)
3. **Send a response** (short-circuit the chain by calling `res.send()` or `res.json()`)
4. **Call `next()`** to pass to the next middleware
5. **Call `next(err)`** to skip to the error handler

The chain is:

```
Request → middleware1 → middleware2 → ... → handler → Response
```

Each middleware runs in order. If a middleware sends a response, the chain stops (no further middleware, no handler). If a middleware calls `next()`, the next one runs. If the handler sends a response, the chain ends.

This is *extremely* powerful. Each middleware does one thing. They compose.

## A Concrete Example: `express.json()`

The `express.json()` middleware reads the body, parses it as JSON, and puts it on `req.body`. Internally, it does exactly what our hand-rolled body parser did (projects 05). It is just packaged as a middleware.

When you register it:

```js
app.use(express.json());
```

…the chain becomes:

```
Request → express.json() → ... → handler
```

`express.json()` reads the body. If the body is JSON, it parses it and sets `req.body`. Then it calls `next()`. The next middleware runs. Eventually, the handler runs, and `req.body` is already a real object.

This is the same pattern as our hand-rolled body parser. Just packaged differently.

## The `app` Object

When you do `const app = express()`, you get an Express application object. It has methods for:

- `app.use(middleware)` — register a middleware (runs on every request)
- `app.get(path, handler)` — register a GET route
- `app.post(path, handler)` — register a POST route
- `app.put`, `app.delete`, `app.patch` — other methods
- `app.listen(port, callback)` — start the server

The handlers are the same `(req, res) => { ... }` shape we used in projects 02-06. The methods on `res` are enhanced:

- `res.json(body)` — send JSON (replaces our `json(res, status, body)` helper)
- `res.status(code)` — chainable status setter
- `res.send(body)` — send any body
- `res.end()` — same as before
- `res.cookie(name, value, options)` — set a cookie
- `res.redirect(url)` — send a redirect

Most of what we did by hand in projects 03 and 06 is now a method on `res`.

## `req` Is Enhanced

Express adds properties to `req`:

- `req.body` — parsed body (from `express.json()`)
- `req.query` — parsed query string
- `req.params` — path parameters (project 11+)
- `req.cookies` — parsed cookies (from `cookie-parser`)
- `req.session` — session data (from `express-session`)
- `req.ip` — client IP
- `req.method`, `req.url`, `req.headers` — same as before

These are the conventions we built by hand. Now they are provided by Express.

## `express-session`

`express-session` is a middleware that provides server-side sessions. The flow:

1. Client makes a request
2. `express-session` checks for a session cookie (`connect.sid`)
3. If present, looks up the session in the store (memory by default)
4. Sets `req.session` to the session data
5. Handler reads/writes `req.session.foo = ...`
6. On response, `express-session` saves the session and sets/updates the cookie

The session is just a JS object. You can put anything in it: `req.session.username`, `req.session.cart`, etc. The middleware handles the cookie, the storage, and the lifecycle.

`req.session.destroy()` ends the session (and clears the cookie).

## `cookie-parser`

`cookie-parser` parses the `Cookie` header into `req.cookies`. It does the same thing as our hand-rolled `parseCookies` from project 06. Just packaged.

## The `secret` Option

`express-session` requires a `secret` — a string used to sign the session ID cookie. The signing prevents the client from forging session IDs.

```js
app.use(session({
  secret: 'dev-secret-change-in-prod',
  resave: false,
  saveUninitialized: false,
}));
```

The secret should be a long random string in production. We use a placeholder.

`resave: false` — don't re-save the session if it wasn't modified.

`saveUninitialized: false` — don't save empty sessions (sessions that the handler didn't touch).

## What We Lose

We lose the *control*. Express is opinionated. Our hand-rolled version let us see every line. Now we trust Express's internals. This is a trade-off:

- **Gain**: Less code, more features, battle-tested, standard
- **Lose**: Less visibility into internals, must trust the framework

We accept this because we *built* the framework's core in projects 01-06. We know what's happening.

## What We Gain

We gain:
- **Middleware** for everything (logging, auth, CORS, validation, error handling)
- **Helper methods** (`res.json`, `res.cookie`, `res.status`)
- **Path parameters** (`/users/:id`) — built into the router
- **Standard conventions** (`req.body`, `req.cookies`, `req.session`) — easy for other developers
- **Community** — thousands of tutorials, StackOverflow answers, npm packages

The trade-off is worth it.

## Common Confusions (read these)

**Confusion 1: "Why Express and not Fastify, Hono, Koa, Nest, etc.?"**
Express is the most popular. It has the most middleware. It is the lowest-friction to learn. Fastify is faster; Hono is more modern; Koa is more minimal; Nest is more structured. We use Express because it is the standard. The concepts transfer to all the others.

**Confusion 2: "Why do I need `npm install` now?"**
Because `node:http` is built into Node. Express is not. We have to install it (and `cookie-parser` and `express-session`). This is the first project with a `package.json` and `node_modules`.

**Confusion 3: "What is `resave: false`?"**
It means "don't re-save the session on every request, only if the session was modified." This is a performance optimization. We always set it to `false` in modern apps.

**Confusion 4: "What is `saveUninitialized: false`?"**
It means "don't create a session for a request that didn't touch `req.session`." This prevents the creation of empty sessions for unauthenticated visitors. Saves memory.

**Confusion 5: "Where is the session data stored?"**
By default, in memory. In production, you'd use a session store like `connect-redis` (project 23) or a database-backed store.

**Confusion 6: "What if I forget to install a package?"**
`require('express')` will throw `Cannot find module 'express'`. Run `npm install express`.

**Confusion 7: "What if my middleware doesn't call `next()`?"**
The request hangs. The chain stops. The client never gets a response. Always call `next()` (or send a response).

**Confusion 8: "What's the difference between `app.use(middleware)` and `app.get(path, middleware)`?"**
`app.use(middleware)` runs on *every* request. `app.get(path, middleware)` runs only on `GET <path>`. Use `app.use` for cross-cutting concerns (logging, body parsing, cookies). Use `app.get/post` for specific routes.

## What We Are About to Build

A 30-line Express app that:

1. Has `express.json()` for body parsing
2. Has `cookie-parser` for cookies
3. Has `express-session` for sessions
4. Has 5 routes: `/`, `/health`, `/login`, `/me`, `/logout`
5. Replaces our 90-line hand-rolled version

The handlers are mostly identical to project 06. The dispatch is replaced by Express.

In [BUILD.md](./BUILD.md) we will go line by line.

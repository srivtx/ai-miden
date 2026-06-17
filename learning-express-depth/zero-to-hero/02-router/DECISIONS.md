# The Decisions

> *"A `Map` is the right data structure. Here's why we chose it, and what comes after."*

## Decision 1: `Map` instead of a plain object

**Alternative**: `const routes = {};` and `routes['GET /'] = handler;`

**Why we didn't**: A `Map` is a cleaner dictionary. It accepts any key type (we use strings, but it could be tuples or objects), has a `size` property, iterates in insertion order, and is slightly faster for many keys. Most importantly, *forming the habit of using `Map` for a dictionary* is correct. We use it.

**Trade-off**: None. A plain object would work; `Map` is just better.

## Decision 2: String key `METHOD PATH` instead of nested structure

**Alternative**: A two-level `Map`:

```js
const routes = new Map();
routes.set('GET', new Map([['/', handlerHome], ['/users', handlerUsers]]));
routes.set('POST', new Map([['/users', handlerCreateUser]]));
```

**Why we didn't**: It's more code for negligible benefit. The lookup is one string comparison either way. We can optimize when the *measured* performance matters, not before.

**Trade-off**: For thousands of routes, the nested structure is slightly faster (no string concatenation). For our scale, the difference is microseconds. YAGNI.

## Decision 3: Helper functions (`get`, `post`) instead of one `route` function

**Alternative**: `route('GET', '/', handler)` everywhere.

**Why we didn't**: `get('/users', handler)` reads like English. `route('GET', '/users', handler)` is more verbose. We match the convention of Express, Hono, Fastify, etc.

**Trade-off**: Two functions to maintain instead of one. We accept this for readability.

## Decision 4: No path parameters

**Alternative**: A `path-to-regexp`-style approach: `get('/users/:id', handler)` and the handler receives `req.params.id = '42'`.

**Why we didn't**: We don't need it yet. Project 11 (Foreign Key) will introduce the need (one user, fetch by id). When it hurts, we'll build it. For now, exact-string matching is enough.

**Trade-off**: For routes like `/users/42` and `/users/43`, we'd have to register each one. Painful, but we don't have this pain yet.

## Decision 5: No query string handling

**Alternative**: Strip the query string before lookup, store it separately, pass it to the handler.

**Why we didn't**: We don't need it yet. The lookup would be `routes.get(`${req.method} ${path}`)` where `path` is `req.url.split('?')[0]`. We'll do this in project 04 (Query-String Reader) when the pain of "I can't filter" is real.

**Trade-off**: Right now, `/users?role=admin` is a 404. That's a bug for any real API, but we have no API yet.

## Decision 6: No middleware

**Alternative**: A chain of functions that run before the handler:

```js
get('/users', logger, auth, (req, res) => { ... });
```

**Why we didn't**: We don't need it yet. Middleware is for cross-cutting concerns: auth, logging, rate limiting. We have none of these. Project 07 (Framework Pivot) will introduce middleware, and we'll feel the *need* for it then.

**Trade-off**: If we add logging now, we'd copy-paste `console.log(req.method, req.url)` into every handler. That's why middleware exists. But we don't have that pain yet.

## Decision 7: 404 for unmatched routes, not 405

**HTTP 405** is "Method Not Allowed" — used when the URL exists but the method doesn't (e.g., `GET /users` works, but `DELETE /users` doesn't).

**Why we use 404**: Simpler. We don't track which methods are valid for a URL. We could enhance the router to return 405 for known-URL-but-unknown-method, but it requires an extra lookup. We use 404 for now. Project 17 (REST Refactor) will revisit this.

**Trade-off**: A strict REST API should return 405 in this case. We don't, because we haven't been asked to.

## Decision 8: Content-Type set once in the dispatch

**Alternative**: Each handler sets its own Content-Type.

**Why we did it this way**: Every response in this project is plain text. Setting it once is DRY.

**Trade-off**: In project 03, we will need different Content-Types per response (text vs. JSON). We'll move it into the handlers then. This is a project 02 decision; not a permanent one.

## Decision 9: No async handlers

The handlers are synchronous. They call `res.end()` and return. No `await`, no callbacks.

**Why**: We have no I/O. No database calls, no network requests, nothing to wait for. Synchronous is fine.

**Trade-off**: Project 10 (SQLite Notebook) introduces a database. From that point on, handlers will be `async`. We'll handle that when we need to.

## Decision 10: Plain `function` for `get` and `post`, arrow function for handlers

**Why**: The helpers (`get`, `post`) might need to be called before their definition is read (in hoisting terms). `function` declarations are hoisted; `const x = () => ...` is not. So we use `function` for the helpers, and arrow functions for the handlers (which are called dynamically, not at definition time).

**Trade-off**: None. It's a JavaScript style point. Some teams use only arrows; some use only `function`. We use `function` for top-level definitions and arrows for callbacks. This is common.

---

## What We Did Not Decide

- **Trie-based routing** for thousands of routes — premature optimization
- **Regex matching** for complex patterns — YAGNI
- **Route grouping** like `/api/v1/users` and `/api/v2/users` — premature
- **Async middleware chains** — we have no async
- **Error pages** with HTML — we send plain text
- **Wildcard routes** like `/static/*` — premature

All of these are real concerns in real systems. We will face them when the scale demands it.

---

## The Meta-Decision: This Project Is Also Boring On Purpose

Just like project 01, project 02 is "boring" in that it doesn't do anything *useful*. It returns hardcoded strings. There's no database, no auth, no real logic.

But it is the *shape* of a router. Once you have this shape, every subsequent project (03 JSON, 04 query strings, 05 body parsing, 06 cookies, etc.) is a *one-line modification* to this code. The router is the *skeleton*. The next projects are the muscles and organs.

We build the boring skeleton first.

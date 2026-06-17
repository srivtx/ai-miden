# The Thought

> *"Routing is a lookup table. The table is a `Map`."*

## The Simplest Possible Router

A router answers one question: *given a request, which handler runs?* The simplest possible router is an `if/else` chain. The next step is a data structure. Let's walk through both.

### Version 1: The If-Chain

```js
const server = http.createServer((req, res) => {
  if (req.url === '/' && req.method === 'GET') {
    return handlerHome(req, res);
  } else if (req.url === '/users' && req.method === 'GET') {
    return handlerUsers(req, res);
  } else if (req.url === '/users' && req.method === 'POST') {
    return handlerCreateUser(req, res);
  } else {
    res.statusCode = 404;
    res.end('Not Found');
  }
});
```

This works. It's just *bad*. Five routes? OK. Fifty? Ouch. Five hundred? Impossible to maintain.

### Version 2: The Map

```js
const routes = new Map();
routes.set('GET /', handlerHome);
routes.set('GET /users', handlerUsers);
routes.set('POST /users', handlerCreateUser);

const server = http.createServer((req, res) => {
  const key = `${req.method} ${req.url}`;
  const handler = routes.get(key);
  if (!handler) {
    res.statusCode = 404;
    res.end('Not Found');
    return;
  }
  handler(req, res);
});
```

Same behavior. *Much* cleaner dispatch logic. Adding a route is a one-line change. Removing a route is a one-line change. Reading the code, the dispatch is *obvious*: look up the key, run the handler, fall back to 404.

This is the version we will build.

## Why a Map and Not an Object?

JavaScript objects are also key-value stores. Why use a `Map`?

**Reason 1: Keys can be any type.** An object coerces keys to strings (or symbols). A `Map` accepts any type, including objects, numbers, and our `METHOD PATH` strings. In our case, the strings work in both, but `Map` is more general.

**Reason 2: `Map` has a size.** `routes.size` gives you the count of routes. Useful for debugging ("how many routes are registered?").

**Reason 3: Iteration order is well-defined.** `Map` iterates in insertion order. Object iteration order is mostly well-defined in modern JS, but `Map` is unambiguous.

**Reason 4: Performance.** For small numbers of keys, the difference is negligible. For thousands, `Map` is consistently faster.

For our case, an object would also work. We use `Map` because it is the *correct* data structure for a dictionary, and forming the habit now is good.

## Why `METHOD PATH` as the Key?

A route is a *combination* of method and path. `GET /users` and `POST /users` are different routes. `GET /users` and `GET /posts` are different routes. We need to distinguish them.

The simplest key is the concatenation `METHOD PATH` with a separator. We use a space, but you could use `:` or `/`. The space is conventional and easy to read.

Some routers use a *two-level* structure: a `Map` of methods, each containing a `Map` of paths:

```js
const routes = new Map();
routes.set('GET', new Map([['/', handlerHome], ['/users', handlerUsers]]));
routes.set('POST', new Map([['/users', handlerCreateUser]]));
```

This is slightly more efficient (you only do one string comparison per request), but it is more code. We use the simpler concatenation. We can optimize later.

## Why a 404?

When no route matches, the standard HTTP response is `404 Not Found`. This is a *contract* between your server and the client. The client sees `404` and knows "this URL doesn't exist on this server." If you returned `200` with an error message, the client would be confused.

`404` is one of the famous "404 page not found" codes. Other common ones:

- `200 OK` — success
- `201 Created` — `POST` that created a resource
- `204 No Content` — `DELETE` that succeeded
- `301 Moved Permanently` — redirect
- `400 Bad Request` — client sent malformed input
- `401 Unauthorized` — needs auth
- `403 Forbidden` — authed but not allowed
- `404 Not Found` — URL doesn't exist
- `500 Internal Server Error` — your code crashed

The status code is part of the *protocol*. Clients use it to decide what to do.

## What the Map Looks Like at Runtime

After we register 4 routes, the `routes` Map contains:

```
'GET /'        → (req, res) => { res.end('Welcome...') }
'GET /users'   → (req, res) => { res.end('Alice, Bob...') }
'POST /users'  → (req, res) => { res.end('User created...') }
'GET /health'  → (req, res) => { res.end('OK') }
```

When a request comes in — say, `GET /users` — we compute the key `'GET /users'`, look it up, and find the second handler. We call it. Done.

When a request comes in for `GET /does-not-exist`, the key `'GET /does-not-exist'` is not in the map, so we return 404.

This is a *lookup table*. It is the simplest possible dispatcher.

## Common Confusions (read these — they will save you hours)

**Confusion 1: "What if I want `/users/42` and `/users/43` to both work?"**
You need *path parameters* — patterns like `/users/:id` that match any value in that position. Our current router matches *exact strings*. Path parameters are a future project. For now, `/users/42` is a 404. We will fix this when it hurts (project 11, Foreign Key, when we have one user and need to fetch by id).

**Confusion 2: "What if I want `/users` and `/Users` to be the same?"**
They are different. `req.url` is case-sensitive. The convention is to use lowercase paths. We don't do case-insensitive routing in this path; it is a footgun.

**Confusion 3: "What if I want to match `/users` *and* `/users/`?"**
Trailing slashes are a perennial source of pain. Some servers treat `/users` and `/users/` as the same. Some don't. We don't. We match exact strings. If you want both, you register both. Or you normalize. We will revisit in project 17 (REST Refactor).

**Confusion 4: "What about query strings? `/users?role=admin`?"**
`req.url` includes the query string. So `'GET /users?role=admin'` is a *different key* from `'GET /users'`. We will address this in project 04 (Query-String Reader). For now, the query string is part of the URL, and the routes are registered without it, so `?role=admin` would cause a 404.

**Confusion 5: "What about the `favicon.ico` request that browsers make automatically?"**
Browsers automatically request `/favicon.ico` for every site. If you don't register a route, it 404s. That's fine — most APIs ignore it. The browser will give up. We will not add a special case.

**Confusion 6: "Why `return;` after the 404?"**
After we call `res.end()`, the response is done. But the handler function continues to the next line. If we wrote more code after the if, it would run. The `return` exits the function early. We use it to make the control flow clear: if we got here, we sent a 404; we are done. Strictly speaking, in this case it's not needed (there's no more code), but it's a good habit for when handlers grow.

**Confusion 7: "What if my handler throws?"**
The server catches the throw (Node wraps handler calls in try/catch), and the client hangs because the response was never sent. This is the same pain as project 01. We will fix it in project 15 (Error Wall).

## What We Are About to Build

A 50-line file that has:

1. A `Map` to store routes
2. `get()` and `post()` helper functions to register routes
3. A request handler that looks up the route and dispatches
4. A `404` fallback for unmatched routes

That's it. In [BUILD.md](./BUILD.md) we will go line by line.

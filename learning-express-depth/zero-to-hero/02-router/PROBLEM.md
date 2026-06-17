# The Problem

> *"Two URLs is a problem. Ten URLs is a crisis. A hundred URLs is an architecture."*

## Why Routing Exists

In project 01, we had one URL: `/`. The handler didn't care what the URL was. The handler responded with `'Hello, world.\n'` to *anything* — `/users`, `/posts`, `/`. It worked because there was only one response to give.

But the moment you have a real API, you have many URLs:

- `GET /users` — list users
- `GET /users/:id` — get one user
- `POST /users` — create a user
- `PUT /users/:id` — update a user
- `DELETE /users/:id` — delete a user
- `GET /posts` — list posts
- `GET /posts/:id` — get one post
- ... and so on

For each URL, you have a *different* function. You need to *pick* the right one based on the request.

**The pain: dispatch.** Given a request, which function do I call?

## What Pain Is This Solving?

Imagine you wrote project 01 with the naive solution:

```js
const server = http.createServer((req, res) => {
  if (req.url === '/' && req.method === 'GET') {
    res.end('Welcome.\n');
  } else if (req.url === '/users' && req.method === 'GET') {
    res.end('Alice, Bob, Carol.\n');
  } else if (req.url === '/users' && req.method === 'POST') {
    res.end('User created.\n');
  } else if (req.url === '/health' && req.method === 'GET') {
    res.end('OK.\n');
  } else {
    res.statusCode = 404;
    res.end('Not Found.\n');
  }
});
```

This *works*. For 4 routes. But:

1. **It's ugly.** The if-chain gets longer with every route. By 20 routes, it's 200 lines of nested conditions.
2. **It's fragile.** Add a new route? You have to find the right place in the chain. Miss a case? You have a bug.
3. **It's hard to test.** The dispatch logic is tangled with the handlers. You can't unit-test "the router" because there is no router — there is just code.
4. **It doesn't scale.** Frameworks like Express have a router that handles thousands of routes in microseconds. An if-chain is O(n) per request.

**The pain is the same as project 01, just bigger.** Project 01 had one URL. Project 02 has many. The solution is the same: a data structure that maps keys (method+path) to values (handler).

## The Deeper Problem: Separating Mechanism from Policy

The if-chain mixes two things:

- **Mechanism**: "Look at the request, find the right handler, call it." (This is the *router*.)
- **Policy**: "What does `/users` return? What does `POST /users` do?" (This is your *business logic*.)

When mechanism and policy are tangled, you can't reason about either one. You can't add a new route without touching the dispatch logic. You can't change the dispatch logic without risking every route.

A router separates them. The router is *mechanism*: a generic dispatcher. Your handlers are *policy*: specific business logic. They evolve independently. This is one of the most important architectural ideas in all of software.

## What This Project Will Solve

This project will:

1. Introduce a `Map` as the routing data structure
2. Add `get()` and `post()` helper functions to register routes
3. Centralize the dispatch in the request handler
4. Return `404` when no route matches

By the end, adding a new route is a one-line change. Removing a route is a one-line change. The dispatch logic is in one place. The handlers are independent of each other.

## What This Project Will *Not* Solve

- **Path parameters** like `/users/:id` — project 11 (Foreign Key) introduces the need, and a later project (probably project 17, REST Refactor) builds the parameter extraction.
- **Query strings** like `/users?role=admin` — project 04 (Query-String Reader).
- **JSON bodies** — project 03 (JSON API).
- **Middleware** — a way to run code *before* the handler (auth, logging, etc.). Project 07 (Framework Pivot) will introduce this.
- **Nested routers** like `/api/v1/users` and `/api/v2/users` — project 17 (REST Refactor).
- **Wildcards** like `/static/*` — project 20 (Uploader) or project 22 (Cache).

Each is a future project. We will feel their absence when it hurts.

## The Question This Project Answers

> *"How do I dispatch a request to the right function?"*

If you can answer: "look up `METHOD path` in a `Map`, call the value, fall back to 404 if missing," you are ready for project 03.

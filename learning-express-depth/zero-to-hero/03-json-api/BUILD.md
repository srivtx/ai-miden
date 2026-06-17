# The Build

> *"Three lines of boilerplate become one. That's the helper."*

We are going to build the JSON API. Most of the code is the same as project 02. The change is:

1. Add a `json(res, status, body)` helper
2. Replace `res.end('text')` with `json(res, 200, { ... })` in every handler
3. Return JSON for the 404 fallback

That's the whole project. Let's go.

## The File

Create `server.js`. Fill it in.

---

## Lines 1-12: The Router (Unchanged)

```js
const http = require('node:http');

const routes = new Map();

function get(path, handler) {
  routes.set(`GET ${path}`, handler);
}

function post(path, handler) {
  routes.set(`POST ${path}`, handler);
}
```

This is identical to project 02. The router is unchanged. We are extending the *handlers*, not the dispatch logic.

---

## Lines 14-19: The JSON Helper

```js
function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(body));
}
```

### What it does

Three steps in one function call:

1. `res.statusCode = status` — set the status code
2. `res.setHeader('Content-Type', 'application/json')` — set the content type
3. `res.end(JSON.stringify(body))` — stringify the body and send it

### Why a helper?

Three lines per response × 6 responses = 18 lines of boilerplate. With the helper, it's 6 lines (one per response). The helper also ensures we never forget the `Content-Type` header.

### Why not a method on `res`?

Express adds `res.json(body)` as a method on the response object. We could do the same:

```js
function attachHelpers(res) {
  res.json = function(status, body) {
    res.statusCode = status;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(body));
  };
  return res;
}
```

Then call `attachHelpers(res).json(200, {...})` everywhere. This is more "framework-like" but more code. We use a free function for now. Project 07 (Framework Pivot) adopts Express, which has `res.json` as a method.

### Order of operations

The status code and header must be set *before* `res.end()`. Once `res.end()` is called, the response is sent. You can't change a header on a sent response (Node will throw).

This is why we use `res.statusCode = ...` and `res.setHeader(...)` (which set fields on the response object), and only call `res.end()` last.

---

## Lines 21-44: The Handlers

```js
get('/', (req, res) => {
  json(res, 200, { message: 'Welcome to the API.' });
});

get('/users', (req, res) => {
  json(res, 200, [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' },
    { id: 3, name: 'Carol' },
  ]);
});

get('/users/1', (req, res) => {
  json(res, 200, { id: 1, name: 'Alice', email: 'alice@example.com' });
});

post('/users', (req, res) => {
  json(res, 201, { id: 4, name: 'Dave', email: 'dave@example.com' });
});

get('/health', (req, res) => {
  json(res, 200, { status: 'ok' });
});
```

### The shape of the responses

- `GET /` — an object with a `message` field
- `GET /users` — an array of objects, each with `id` and `name`
- `GET /users/1` — a single user object with `id`, `name`, `email`
- `POST /users` — the created user (with `id: 4`, the new id), status 201
- `GET /health` — a status object

### Why `201` for `POST`?

The convention: `201 Created` means "I created a new resource, here it is." The response includes the new resource (so the client knows its id, etc.).

`200 OK` is generic success. For `POST` that creates, `201` is more specific.

### The hardcoded data

`/users/1` returns a hardcoded user. We don't have a database yet, so this is a fake. In project 10 (SQLite Notebook), we'll have a real database. For now, hardcoded is fine — the *shape* of the response is what matters.

---

## Lines 46-55: The Server and Dispatch

```js
const server = http.createServer((req, res) => {
  const handler = routes.get(`${req.method} ${req.url}`);
  if (!handler) {
    json(res, 404, { error: 'Not Found' });
    return;
  }
  handler(req, res);
});

server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

### What changed from project 02

- The `Content-Type: text/plain` is gone. Each handler sets its own content type via the `json()` helper.
- The 404 fallback now returns JSON: `json(res, 404, { error: 'Not Found' })`. Not `'Not Found\n'`.

### Why JSON for errors?

Because the client (a JS program) wants structured errors. `{ error: 'Not Found' }` can be programmatically handled: `if (response.error === 'Not Found') showNotFoundPage()`. A plain string is harder to handle robustly.

This is the convention for modern APIs. JSON in, JSON out — even for errors.

---

## The Full File

```js
const http = require('node:http');

const routes = new Map();

function get(path, handler) {
  routes.set(`GET ${path}`, handler);
}

function post(path, handler) {
  routes.set(`POST ${path}`, handler);
}

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(body));
}

get('/', (req, res) => {
  json(res, 200, { message: 'Welcome to the API.' });
});

get('/users', (req, res) => {
  json(res, 200, [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' },
    { id: 3, name: 'Carol' },
  ]);
});

get('/users/1', (req, res) => {
  json(res, 200, { id: 1, name: 'Alice', email: 'alice@example.com' });
});

post('/users', (req, res) => {
  json(res, 201, { id: 4, name: 'Dave', email: 'dave@example.com' });
});

get('/health', (req, res) => {
  json(res, 200, { status: 'ok' });
});

const server = http.createServer((req, res) => {
  const handler = routes.get(`${req.method} ${req.url}`);
  if (!handler) {
    json(res, 404, { error: 'Not Found' });
    return;
  }
  handler(req, res);
});

server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

---

## Run It

```bash
node server.js

# Welcome
curl http://localhost:3000/
# {"message":"Welcome to the API."}

# List users
curl http://localhost:3000/users
# [{"id":1,"name":"Alice"},{"id":2,"name":"Bob"},{"id":3,"name":"Carol"}]

# Get one user
curl http://localhost:3000/users/1
# {"id":1,"name":"Alice","email":"alice@example.com"}

# Create a user
curl -X POST http://localhost:3000/users
# {"id":4,"name":"Dave","email":"dave@example.com"}

# Health
curl http://localhost:3000/health
# {"status":"ok"}

# 404
curl -i http://localhost:3000/missing
# HTTP/1.1 404 Not Found
# Content-Type: application/json
#
# {"error":"Not Found"}
```

---

## Experiments

### Experiment 1: Return a nested object

```js
get('/profile', (req, res) => {
  json(res, 200, {
    user: { id: 1, name: 'Alice' },
    preferences: { theme: 'dark', lang: 'en' },
    friends: [2, 3, 4],
  });
});
```

```bash
curl http://localhost:3000/profile | python3 -m json.tool
```

`json.tool` (from Python) pretty-prints JSON. Useful for reading.

### Experiment 2: Return a circular structure

```js
const a = { name: 'A' };
const b = { name: 'B', friend: a };
a.friend = b;

get('/circular', (req, res) => {
  json(res, 200, a); // throws
});
```

`JSON.stringify` throws on circular references. The throw happens inside your handler, the response is never sent, and the client hangs. We will fix this in project 15 (Error Wall).

### Experiment 3: Forget Content-Type

Comment out the `setHeader` line in `json()`. Restart. `curl -i` will show no Content-Type. The body is still valid JSON, but the client doesn't know to parse it. A browser will display it as text. A fetch client might not parse it.

### Experiment 4: Use `res.end` directly with a string

```js
get('/text', (req, res) => {
  res.end('just a string');
});
```

The handler bypasses our `json()` helper. No Content-Type is set. The client gets a string. This works but breaks the JSON convention. Don't do this.

### Experiment 5: Return a status with no body

For `DELETE`, you often want to return 204 with no body. Try:

```js
function del(path, handler) {
  routes.set(`DELETE ${path}`, handler);
}

del('/users/1', (req, res) => {
  res.statusCode = 204;
  res.end();
});
```

`204 No Content` means "success, but no body to send." `res.end()` with no argument sends no body. The connection still closes.

### Experiment 6: Pretty-print

```js
function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(body, null, 2)); // 2-space indent
}
```

Now responses are pretty-printed. Useful for development. Don't do this in production — it adds bytes.

---

## Summary

You now have a JSON API. Sending and receiving structured data works. The router is unchanged. The handlers return JS objects, which are stringified and sent with the correct Content-Type.

In project 04, we will add query string support so we can do `GET /users?role=admin` and filter the list. The router needs a small change: strip the query string from `req.url` before the lookup.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

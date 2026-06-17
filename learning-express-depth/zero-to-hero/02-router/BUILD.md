# The Build

> *"Adding routes is data, not control flow."*

We are going to build the router, line by line, and along the way we will discuss what each piece does and why it exists.

## The File

Create `server.js`. We will fill it in.

```bash
touch server.js
```

---

## Lines 1-2: The Imports and the Map

```js
const http = require('node:http');

const routes = new Map();
```

### Line 1

We have seen this before. It loads the built-in HTTP module.

### Line 3

`new Map()` creates an empty dictionary. We will use it to store the routes.

Why a `Map` and not an object? Both are key-value stores. `Map` has slightly better semantics (any key type, well-defined iteration, `size` property) and is the standard choice for a dictionary in modern JS. We use it because it is the correct data structure.

At this point, `routes` is empty. We will add to it.

---

## Lines 5-11: The Helper Functions

```js
function get(path, handler) {
  routes.set(`GET ${path}`, handler);
}

function post(path, handler) {
  routes.set(`POST ${path}`, handler);
}
```

### What they do

`get(path, handler)` registers a handler for `GET <path>`. `post(path, handler)` does the same for `POST <path>`. The key is the string `METHOD path`; the value is the handler function.

### Why have helpers?

We *could* write `routes.set('GET /', handler)` directly. But the helpers:

1. **Enforce the key format.** We can't accidentally write `routes.set('/users', handler)` (which would match any method).
2. **Make the code readable.** `get('/users', handler)` reads like English. `routes.set('GET /users', handler)` is more verbose.
3. **Are extensible.** When we add `put`, `delete`, `patch`, etc., we just add more functions. The dispatch code doesn't change.

### Why two functions, not one?

We could have:

```js
function route(method, path, handler) {
  routes.set(`${method} ${path}`, handler);
}

route('GET', '/', handlerHome);
route('POST', '/users', handlerCreateUser);
```

This is one function that does both. It's slightly more compact. But the two-function form (`get`, `post`) reads better at the call site and matches what Express does. We use the two-function form.

### What's the trade-off?

Two functions means two pieces of code to maintain. One function means more verbose call sites. Both are fine. We pick the form that reads better.

---

## Lines 13-26: Registering Routes

```js
get('/', (req, res) => {
  res.end('Welcome to the API.\n');
});

get('/users', (req, res) => {
  res.end('Alice, Bob, Carol\n');
});

post('/users', (req, res) => {
  res.end('User created.\n');
});

get('/health', (req, res) => {
  res.end('OK\n');
});
```

### What they do

These register four routes:

- `GET /` → returns a welcome message
- `GET /users` → returns a list of users
- `POST /users` → returns a "user created" message
- `GET /health` → returns "OK" (a common endpoint for health checks)

### Why register before `createServer`?

Because if a request comes in before the route is registered, the router will return 404. In practice, this doesn't matter (the server doesn't start until `listen` is called, and no requests can come in until then). But registering routes first is a *readable* convention: "first I declare my routes, then I start the server."

### The handlers themselves

Each handler is an arrow function that takes `(req, res)` and writes a response. We don't need to set the status code (it defaults to 200) or `Content-Type` (we'll set it once in the dispatch, below).

Notice: **the handlers are not aware of the router.** They receive `req` and `res` and that's it. They don't know what method they handle, what path they handle, or what other handlers exist. This is the *separation of mechanism and policy* we discussed in PROBLEM.md.

---

## Lines 28-39: The Server and the Dispatch

```js
const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'text/plain');
  const handler = routes.get(`${req.method} ${req.url}`);
  if (!handler) {
    res.statusCode = 404;
    res.end('Not Found\n');
    return;
  }
  handler(req, res);
});
```

### Line 28

`http.createServer(handler)` creates the server, just like project 01. The handler is called for every request.

### Line 29

`res.setHeader('Content-Type', 'text/plain')` sets the content type for *all* responses. We're going to send plain text from every handler, so we set it once at the top of the dispatch.

This is fine for now. In project 03, we will move this into individual handlers (because JSON responses need `application/json`).

### Line 30

`const handler = routes.get(`${req.method} ${req.url}`);`

This is the *lookup*. We build the key from the request's method and URL, then look it up in the map.

- `req.method` is a string like `'GET'`, `'POST'`, etc.
- `req.url` is a string like `'/'` or `'/users?role=admin'`
- The template literal builds the key: `'GET /'`, `'GET /users'`, etc.

If the key exists in the map, `handler` is the function. If not, `handler` is `undefined`.

### Lines 31-35: The 404 Fallback

```js
if (!handler) {
  res.statusCode = 404;
  res.end('Not Found\n');
  return;
}
```

If no handler matched, we set the status to 404, send a "Not Found" body, and `return` to exit the handler.

The `return` is technically optional here (there's no code after it that would matter), but it's a good habit. If we add more logic later (e.g., logging, error handling), the `return` ensures we don't accidentally fall through.

### Line 36: The Dispatch

```js
handler(req, res);
```

If we got here, we have a handler. We call it with the original `req` and `res`. The handler writes its response. The connection eventually closes when `res.end()` is called inside the handler.

---

## Lines 41-43: The Listen

```js
server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

Same as project 01. Start the server, log a confirmation.

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

get('/', (req, res) => {
  res.end('Welcome to the API.\n');
});

get('/users', (req, res) => {
  res.end('Alice, Bob, Carol\n');
});

post('/users', (req, res) => {
  res.end('User created.\n');
});

get('/health', (req, res) => {
  res.end('OK\n');
});

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'text/plain');
  const handler = routes.get(`${req.method} ${req.url}`);
  if (!handler) {
    res.statusCode = 404;
    res.end('Not Found\n');
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

# In another terminal:

curl http://localhost:3000/
# Welcome to the API.

curl http://localhost:3000/users
# Alice, Bob, Carol

curl -X POST http://localhost:3000/users
# User created.

curl http://localhost:3000/health
# OK

curl http://localhost:3000/does-not-exist
# Not Found
```

---

## Experiments

### Experiment 1: Register the same route twice

Add:

```js
get('/users', (req, res) => res.end('Different response.\n'));
```

Run it. The new registration *overwrites* the old one. The Map's `set` is "last write wins." This is a feature: it lets you override routes. It's also a footgun: if you accidentally register the same route twice, the first is silently lost.

### Experiment 2: Use a method that isn't registered

```bash
curl -X PUT http://localhost:3000/users
# Not Found
```

The key `'PUT /users'` isn't in the map, so we 404. To handle PUT, we'd register a `put` helper and add a route.

### Experiment 3: Capitalize the path

```bash
curl http://localhost:3000/Users
# Not Found
```

The key `'GET /Users'` isn't in the map. We registered `'GET /users'` (lowercase). Case-sensitive. We don't do case-insensitive routing in this path.

### Experiment 4: Trailing slash

```bash
curl http://localhost:3000/users/
# Not Found
```

The key `'GET /users/'` isn't in the map. We registered `'GET /users'`. Trailing slashes matter.

### Experiment 5: Add a query string

```bash
curl 'http://localhost:3000/users?role=admin'
# Not Found
```

`req.url` is `'/users?role=admin'`, so the key is `'GET /users?role=admin'`, which isn't in the map. The query string is part of the URL. This is a *real pain* we will solve in project 04.

### Experiment 6: Throw inside a handler

```js
get('/boom', (req, res) => {
  throw new Error('kaboom');
});
```

```bash
curl http://localhost:3000/boom
# (hangs)
```

The handler throws, Node catches it at the framework level, but no response is sent. The client hangs. This is project 15's pain.

---

## Summary

You now have a router. Adding a route is one line. Removing a route is one line. The dispatch logic is in one place. The handlers are independent.

In project 03, we will move from plain text to JSON. The router stays the same. The handlers change.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

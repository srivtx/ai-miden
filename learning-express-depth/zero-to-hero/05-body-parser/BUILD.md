# The Build

> *"The body is a stream. Listen for chunks. Wait for the end. Then parse."*

We are going to add body parsing. The change is: the dispatch becomes async (it listens for `'data'` and `'end'` events). The handler is unchanged in shape — it just gets `req.body` for free.

## The File

Create `server.js`. Fill it in.

---

## Lines 1-22: The Router and Helper (Unchanged)

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
```

Identical to projects 02-04.

---

## Lines 24-27: The Users Data (with a Twist)

```js
const USERS = [
  { id: 1, name: 'Alice', role: 'admin' },
  { id: 2, name: 'Bob', role: 'user' },
];
```

We have a smaller list. This is so we can demonstrate *adding* a user via `POST`. The handler will push to this array.

---

## Lines 29-47: The Handlers

```js
get('/', (req, res) => {
  json(res, 200, { message: 'Welcome to the API.' });
});

get('/users', (req, res) => {
  json(res, 200, USERS);
});

post('/users', (req, res) => {
  const user = {
    id: USERS.length + 1,
    name: req.body.name,
    role: req.body.role || 'user',
  };
  USERS.push(user);
  json(res, 201, user);
});

get('/health', (req, res) => {
  json(res, 200, { status: 'ok' });
});
```

### The `POST /users` handler

This is where `req.body` shines:

1. `const user = { ... }` — build the new user object
2. `id: USERS.length + 1` — naive id assignment (1, 2, 3, ...). In project 10, the DB will assign ids.
3. `name: req.body.name` — read the name from the request body
4. `role: req.body.role || 'user'` — read the role, default to 'user' if not provided
5. `USERS.push(user)` — add to the in-memory array
6. `json(res, 201, user)` — return the new user with 201 Created

### Why `req.body.name` and not `req.query.name`?

Because `POST` is for *creating*. The data the client is sending is the *new* user. Convention says: use the body for `POST`, the query for `GET`.

Could we put the data in the query? `POST /users?name=Eve&role=admin`? Technically valid, but unusual. The convention is body for `POST`.

### What if the body is missing fields?

If the client sends `{"role": "admin"}` with no `name`, `req.body.name` is `undefined`, and we create a user with `name: undefined`. `JSON.stringify` will omit the field (we discussed this in project 03). The response is `{"id":3,"role":"admin"}`.

We don't validate. We don't reject. We just accept. Validation is project 14.

### What if the body is empty?

If the client sends `POST /users` with no body, `req.body` is `{}` (we set it in the dispatch). Then `req.body.name` is `undefined`. Same as above. The user is created with no name.

In a real API, we'd reject this with `400 Bad Request` because `name` is required. We don't yet.

---

## Lines 49-77: The Server and the New Async Dispatch

```js
const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split('?');
  req.query = Object.fromEntries(new URLSearchParams(queryString || ''));

  const chunks = [];
  req.on('data', (chunk) => chunks.push(chunk));
  req.on('end', () => {
    const raw = Buffer.concat(chunks).toString('utf8');
    if (raw) {
      try {
        req.body = JSON.parse(raw);
      } catch (err) {
        json(res, 400, { error: 'Invalid JSON' });
        return;
      }
    } else {
      req.body = {};
    }

    const handler = routes.get(`${req.method} ${path}`);
    if (!handler) {
      json(res, 404, { error: 'Not Found' });
      return;
    }
    handler(req, res);
  });
});

server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

### The new structure

The dispatch is now a function that:

1. Sets `req.query` (from project 04)
2. **Listens for `'data'` events** to collect body chunks
3. **Listens for the `'end'` event** to know the body is done
4. **Inside the `'end'` handler**: parse the body, dispatch to the route

The dispatch doesn't return immediately. It returns after setting up the listeners. The actual work (parsing, dispatching) happens later, when the body arrives.

This is what "asynchronous" means in Node. The framework (our dispatch) handles the I/O; the handler focuses on logic.

### Line by line

```js
const [path, queryString] = req.url.split('?');
req.query = Object.fromEntries(new URLSearchParams(queryString || ''));
```

Same as project 04. We set `req.query` synchronously, before listening for the body. This is fine because the query is in the URL (which is available immediately) while the body is in the payload (which isn't).

```js
const chunks = [];
req.on('data', (chunk) => chunks.push(chunk));
```

`chunks` is an array that will hold Buffer objects. We register a listener for `'data'` events: every time a chunk arrives, push it to the array. This runs 0 times (empty body), 1 time (small body in one chunk), or many times (large body in many chunks).

```js
req.on('end', () => {
```

Register a listener for the `'end'` event. This fires when the body is fully received. Inside the listener is where we parse and dispatch.

```js
  const raw = Buffer.concat(chunks).toString('utf8');
```

`Buffer.concat(chunks)` concatenates all the chunks into one Buffer. `.toString('utf8')` decodes the bytes as a UTF-8 string. Now we have the body as a string.

```js
  if (raw) {
    try {
      req.body = JSON.parse(raw);
    } catch (err) {
      json(res, 400, { error: 'Invalid JSON' });
      return;
    }
  } else {
    req.body = {};
  }
```

If the body is non-empty, try to parse as JSON. If parsing fails, send a 400 and return (don't dispatch).

If the body is empty (raw is `''`), set `req.body = {}` so handlers can safely do `req.body.name`.

```js
  const handler = routes.get(`${req.method} ${path}`);
  if (!handler) {
    json(res, 404, { error: 'Not Found' });
    return;
  }
  handler(req, res);
});
```

Same dispatch as before. Look up the route, 404 if not found, else run the handler. The handler now has access to `req.body`.

### Why is this inside a callback?

Because we can't dispatch until the body arrives. The `'end'` event is the signal "body is done, you can dispatch now." Putting the dispatch inside the `'end'` listener is the natural way to express this.

The handler is still called with `(req, res)`. It doesn't know about streams. It just sees `req.body` as a real object.

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

const USERS = [
  { id: 1, name: 'Alice', role: 'admin' },
  { id: 2, name: 'Bob', role: 'user' },
];

get('/', (req, res) => {
  json(res, 200, { message: 'Welcome to the API.' });
});

get('/users', (req, res) => {
  json(res, 200, USERS);
});

post('/users', (req, res) => {
  const user = {
    id: USERS.length + 1,
    name: req.body.name,
    role: req.body.role || 'user',
  };
  USERS.push(user);
  json(res, 201, user);
});

get('/health', (req, res) => {
  json(res, 200, { status: 'ok' });
});

const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split('?');
  req.query = Object.fromEntries(new URLSearchParams(queryString || ''));

  const chunks = [];
  req.on('data', (chunk) => chunks.push(chunk));
  req.on('end', () => {
    const raw = Buffer.concat(chunks).toString('utf8');
    if (raw) {
      try {
        req.body = JSON.parse(raw);
      } catch (err) {
        json(res, 400, { error: 'Invalid JSON' });
        return;
      }
    } else {
      req.body = {};
    }

    const handler = routes.get(`${req.method} ${path}`);
    if (!handler) {
      json(res, 404, { error: 'Not Found' });
      return;
    }
    handler(req, res);
  });
});

server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

---

## Run It

```bash
node server.js

# Create a user with full body
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Eve", "role": "admin"}'
# {"id":3,"name":"Eve","role":"admin"}

# Create a user with partial body
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Frank"}'
# {"id":4,"name":"Frank","role":"user"}

# Create a user with no body
curl -X POST http://localhost:3000/users
# {"id":5,"role":"user"} (name is undefined, omitted from JSON)

# Invalid JSON
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d 'not json'
# {"error":"Invalid JSON"}

# List
curl http://localhost:3000/users
# 5 users
```

---

## Experiments

### Experiment 1: Read a non-JSON body

```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: text/plain" \
  -d 'plain text body'
# {"error":"Invalid JSON"}
```

We try to parse plain text as JSON. It fails. We return 400. A more sophisticated body parser would check `Content-Type` and only parse if it's `application/json`. We don't, because we only expect JSON.

### Experiment 2: Send a huge body

```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d "$(python3 -c 'print("{\"name\": \"x\" * 100000}')")"
# (works, but uses lots of memory)
```

A huge body accumulates in `chunks`. We'd want a size limit. We'll add one in project 14 (Validator).

### Experiment 3: Disconnect mid-body

```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name":' &
sleep 0.1
kill %1
```

The client disconnects mid-body. The `'error'` event fires on `req` (we don't listen for it). The server's response is never sent. The connection is closed. We don't handle this gracefully. We will, in project 15 (Error Wall).

### Experiment 4: Send a body with a `GET`

```bash
curl -X GET http://localhost:3000/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Eve"}'
```

`GET` with a body is technically valid. We read the body, parse it, but the handler is `get('/', ...)` which doesn't use `req.body`. The body is silently ignored. Some servers reject this. We don't.

### Experiment 5: Forget to call `res.end`

```js
post('/hang', (req, res) => {
  // forgot res.end
});
```

```bash
curl -X POST http://localhost:3000/hang -d '{}'
# (hangs)
```

We don't call `res.end`. The response is never sent. The client hangs. We will fix this in project 15.

### Experiment 6: Log the body

```js
const server = http.createServer((req, res) => {
  // ...
  req.on('end', () => {
    console.log('body:', req.body); // <-- add this
    // dispatch
  });
});
```

Now every request's body is logged. The seed of project 16 (Logger).

### Experiment 7: Use `req.text` if you have Node 18+

```js
req.on('end', async () => {
  const raw = await req.text(); // simpler!
  // ...
});
```

Node 18+ added `req.text()` and `req.json()` methods to the request. We could use them instead of the stream-based approach. We don't, because we want to understand streams. The methods are syntactic sugar over the same pattern.

---

## Summary

You now have body parsing. The body is read, parsed, and put on `req.body`. Handlers can use it. The dispatch is async — it waits for the body before dispatching. Invalid JSON returns 400.

The pattern is: **parse once in the dispatch, use many times in handlers.** Same as `req.query`. The dispatch is becoming the *framework* — it does the I/O, the handler does the logic.

In project 06, we will add cookies — the ability to remember who the user is across requests. The body is *one request*; cookies span *many requests*. That's a different kind of state.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

# The Build

> *"One line of dispatch code unlocks a whole new dimension of API design."*

We are going to add query string support. The change is small: two lines in the dispatch. The handlers are also slightly more sophisticated (they read `req.query`). Let's go.

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

Identical to project 03. The router and helper are unchanged.

---

## Lines 24-31: The Users Data

```js
const USERS = [
  { id: 1, name: 'Alice', role: 'admin' },
  { id: 2, name: 'Bob', role: 'user' },
  { id: 3, name: 'Carol', role: 'admin' },
  { id: 4, name: 'Dave', role: 'user' },
];
```

We now have data with multiple roles. This is so we can demonstrate filtering. In project 10, this will move to a database.

---

## Lines 33-46: The Handlers

```js
get('/', (req, res) => {
  json(res, 200, { message: 'Welcome to the API.' });
});

get('/users', (req, res) => {
  let users = USERS;
  if (req.query.role) {
    users = users.filter((u) => u.role === req.query.role);
  }
  json(res, 200, users);
});

get('/health', (req, res) => {
  json(res, 200, { status: 'ok' });
});
```

### The `/users` handler

This is where query string parsing pays off:

1. `let users = USERS;` — start with all users
2. `if (req.query.role)` — if the client passed `?role=...`
3. `users = users.filter((u) => u.role === req.query.role);` — keep only matching users
4. `json(res, 200, users);` — return the filtered list

The handler is small. The *power* comes from `req.query.role` being a real string. If we hadn't parsed the query, we'd be doing string manipulation on `'/users?role=admin'`, which is awful.

### Why check `if (req.query.role)` first?

If the client calls `/users` with no query, `req.query` is `{}` and `req.query.role` is `undefined`. The `if` skips the filter and we return all users. This is the right behavior: no filter, no problem.

If we did `users.filter((u) => u.role === undefined)`, we'd get an empty list. Wrong.

### Why `===` and not `==`?

Strict equality. `req.query.role` is always a string (or `undefined`). `u.role` is always a string. `===` is the right tool. We always use `===` in this path.

### Other potential filters

We could add more filters:

```js
if (req.query.role) {
  users = users.filter((u) => u.role === req.query.role);
}
if (req.query.name) {
  users = users.filter((u) => u.name.includes(req.query.name));
}
```

Each filter is a few lines. The pattern is: read query, conditionally filter. We'll add more sophisticated filtering in project 19 (Searcher).

---

## Lines 48-58: The Server and the New Dispatch

```js
const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split('?');
  req.query = Object.fromEntries(new URLSearchParams(queryString || ''));
  const handler = routes.get(`${req.method} ${path}`);
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

### The new line: split the URL

```js
const [path, queryString] = req.url.split('?');
```

`String.prototype.split(separator)` returns an array. Destructuring assigns:

- `path` = the part before `?`
- `queryString` = the part after `?` (or `undefined` if no `?`)

For `req.url = '/users?role=admin'`, we get `['/users', 'role=admin']`. So `path = '/users'`, `queryString = 'role=admin'`.

For `req.url = '/users'`, we get `['/users']`. So `path = '/users'`, `queryString = undefined`.

### The next new line: parse the query

```js
req.query = Object.fromEntries(new URLSearchParams(queryString || ''));
```

Three things happen:

1. `queryString || ''` — handle the `undefined` case (no `?` in URL)
2. `new URLSearchParams(...)` — parse the query string into a `URLSearchParams` object
3. `Object.fromEntries(...)` — convert the iterator into a plain JS object

Result: `req.query` is a plain object like `{ role: 'admin', limit: '10' }`.

We *mutate* `req` by adding a `query` property. This is fine — `req` is an object we own, and adding properties to it is the convention for "enriching" the request.

### The route lookup is now by path, not full URL

```js
const handler = routes.get(`${req.method} ${path}`);  // path, not req.url
```

This is the key change. Before, we used `req.method} ${req.url}`. Now we use `${req.method} ${path}`. So `GET /users?role=admin` and `GET /users` both look up `GET /users` and find the same handler.

### The rest is unchanged

The 404 fallback and the handler call are the same as project 03.

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
  { id: 3, name: 'Carol', role: 'admin' },
  { id: 4, name: 'Dave', role: 'user' },
];

get('/', (req, res) => {
  json(res, 200, { message: 'Welcome to the API.' });
});

get('/users', (req, res) => {
  let users = USERS;
  if (req.query.role) {
    users = users.filter((u) => u.role === req.query.role);
  }
  json(res, 200, users);
});

get('/health', (req, res) => {
  json(res, 200, { status: 'ok' });
});

const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split('?');
  req.query = Object.fromEntries(new URLSearchParams(queryString || ''));
  const handler = routes.get(`${req.method} ${path}`);
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

# All users
curl http://localhost:3000/users
# 4 users

# Filter by role
curl 'http://localhost:3000/users?role=admin'
# 2 admins

curl 'http://localhost:3000/users?role=user'
# 2 users

# Unknown role
curl 'http://localhost:3000/users?role=foo'
# [] (empty array)

# No filter
curl http://localhost:3000/users
# 4 users

# Multiple params (limit is ignored for now)
curl 'http://localhost:3000/users?role=admin&limit=1'
# 2 admins (limit not enforced)
```

---

## Experiments

### Experiment 1: URL encoding

```bash
curl 'http://localhost:3000/users?name=Alice%20Smith'
# (returns whatever; the URL decoder handles the space)
```

Or with `+`:

```bash
curl 'http://localhost:3000/users?name=Alice+Smith'
# Same — `+` is a space in query strings
```

`URLSearchParams` decodes both. The handler sees `'Alice Smith'`.

### Experiment 2: Empty value

```bash
curl 'http://localhost:3000/users?role='
# (returns all users — empty string is falsy)
```

Our `if (req.query.role)` treats `''` as no filter. If we wanted to allow "filter for users with no role," we'd check `if ('role' in req.query)`. We don't, because the data doesn't have null roles.

### Experiment 3: Multi-value

```bash
curl 'http://localhost:3000/users?tag=a&tag=b'
# `tag` is 'b' (last value wins)
```

`Object.fromEntries` takes the last value. To keep all values, you'd iterate manually. We don't need this here.

### Experiment 4: Forget to update the lookup

If you accidentally leave `${req.method} ${req.url}` in the dispatch, the query string will break the lookup. `GET /users?role=admin` would look for `GET /users?role=admin` in the map and 404. Always use `path` for the lookup, not `req.url`.

### Experiment 5: Forget `req.query =`

If you compute the query but don't assign it to `req.query`, the handler can't access it. Always assign.

### Experiment 6: Hash fragment

```bash
curl 'http://localhost:3000/users#top'
# (curl strips the fragment; the server doesn't see it)
```

The fragment is a browser-only thing. Browsers strip it before sending. The server never sees `#top`. Good.

### Experiment 7: Log the request

```js
const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split('?');
  req.query = Object.fromEntries(new URLSearchParams(queryString || ''));
  console.log(`${req.method} ${path}`, req.query); // <-- add this
  // ...
});
```

Now every request is logged with its query. This is the seed of project 16 (Logger).

---

## Summary

You now have query string support. The router matches the path. The handler gets `req.query` as a clean object. Filtering is a one-line addition to the handler.

The pattern: **parse once in the dispatch, use many times in handlers.** This is the convention for *every* web framework. We do it the same way.

In project 05, we will add body parsing — the *opposite* of query strings. Query is in the URL; body is sent after the headers. We will read the body and put it on `req.body`, just like we did with `req.query`.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

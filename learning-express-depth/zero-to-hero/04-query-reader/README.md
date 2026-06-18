# Project 04: The Query-String Reader

> *"The URL is not just a path. It is a path and a question."*

So far, our router matches the *full* URL — including the query string. So `GET /users` works, but `GET /users?role=admin` is a 404, because the registered key is `'GET /users'` and the request key is `'GET /users?role=admin'`.

This project fixes that. We will:

1. Parse the query string into a real JS object: `{ role: 'admin' }`
2. Strip the query string from `req.url` before the route lookup
3. Pass the parsed query to the handler

By the end, `GET /users?role=admin` will dispatch to `GET /users`, and the handler will receive `req.query = { role: 'admin' }` so it can filter.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is the query string part of the URL? Why does it hurt?
2. [The Thought](./THOUGHT.md) — What is `URLSearchParams`? How do we split path from query?
3. [The Build](./BUILD.md) — Line-by-line construction of the query reader
4. [The Decisions](./DECISIONS.md) — Why `URLSearchParams` and not regex? Why not strip in handlers?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A URL is `<path>?<query>`. The path is the resource; the query is the question. To route by path only, we split the URL on `?` and look up the path. To answer the question, we parse the query with `URLSearchParams` and pass it to the handler. Two lines of code solve the pain. The standard library does the parsing — we just wire it in.

---

## The Code

```js
// server.js
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

Test it:

```bash
node server.js

curl http://localhost:3000/users
# [{"id":1,"name":"Alice","role":"admin"}, ...]

curl 'http://localhost:3000/users?role=admin'
# [{"id":1,"name":"Alice","role":"admin"},{"id":3,"name":"Carol","role":"admin"}]

curl 'http://localhost:3000/users?role=user'
# [{"id":2,"name":"Bob","role":"user"},{"id":4,"name":"Dave","role":"user"}]

curl 'http://localhost:3000/users?role=admin&limit=2'
# (returns the filtered list; `limit=2` is in req.query but not used)
```

The pain of "I cannot filter" is solved. The router matches the *path*; the query is a separate object on `req.query`.

---

## What You Will Have Learned

- The structure of a URL: `<scheme>://<host>:<port><path>?<query>#<fragment>`
- How to use `URLSearchParams` to parse a query string
- Why we split on `?` before the route lookup
- That the query string is the *filter*, the path is the *resource*
- A convention: `req.query` is the parsed query, `req.url` is still the raw URL (with the query)

These are the foundations of *every* API. Project 05 (Body Parser) will let us *send* data; this project lets us *filter*.

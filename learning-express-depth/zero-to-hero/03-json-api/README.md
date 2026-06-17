# Project 03: The JSON API

> *"Plain text is for humans. JSON is for programs."*

Projects 01 and 02 returned plain text: `'Alice, Bob, Carol\n'`. A human can read this, but a program can't. A program wants *structured* data — an array of strings, a list of objects, a nested tree. The standard format for that is JSON.

This project teaches JSON. By the end, our API will return and accept JSON, and you will understand the format so deeply that you'll never confuse JSON with JavaScript objects again.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why JSON? What's wrong with plain text?
2. [The Thought](./THOUGHT.md) — What is JSON? How does it differ from a JS object?
3. [The Build](./BUILD.md) — Line-by-line construction of the JSON API
4. [The Decisions](./DECISIONS.md) — Why JSON.stringify? Why application/json?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

JSON (JavaScript Object Notation) is a *string format* for representing structured data. It looks like JavaScript object syntax, but it is just text — it has to be *parsed* to become a JS object, and *stringified* to become JSON. The Content-Type for JSON is `application/json`. Three functions do all the work: `JSON.stringify(obj)` to send, `JSON.parse(string)` to receive, and a `res.json(obj)` helper to make it one line.

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

Test it:

```bash
node server.js

curl http://localhost:3000/
# {"message":"Welcome to the API."}

curl http://localhost:3000/users
# [{"id":1,"name":"Alice"},{"id":2,"name":"Bob"},{"id":3,"name":"Carol"}]

curl http://localhost:3000/users/1
# {"id":1,"name":"Alice","email":"alice@example.com"}

curl -X POST http://localhost:3000/users
# {"id":4,"name":"Dave","email":"dave@example.com"}

curl -i http://localhost:3000/missing
# HTTP/1.1 404 Not Found
# Content-Type: application/json
#
# {"error":"Not Found"}
```

The pain of "I can only return strings" is solved. We can return any structure: objects, arrays, nested data, numbers, booleans, null.

---

## What You Will Have Learned

- What JSON actually is (a string format, not a JS object)
- How to send JSON with `JSON.stringify`
- How to send the correct `Content-Type: application/json`
- Why `201 Created` is the right code for `POST` that creates
- A `json(res, status, body)` helper to avoid boilerplate

These are the foundations of every modern API. Project 04 (Query-String Reader) will add filtering, and project 05 (Body Parser) will let us accept JSON from clients.

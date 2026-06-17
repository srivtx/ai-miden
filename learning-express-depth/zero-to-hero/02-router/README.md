# Project 02: The Router

> *"One URL is a function. Many URLs is a router."*

Project 01 responded with the same string to every URL. That worked for a hello-world, but it is useless for anything else. The moment you have two endpoints — `/users` and `/posts` — you need to *decide* which one to run.

That decision is routing. This project builds a router from scratch: 50 lines of code that map a URL to a handler.

After this project, you will understand what every router in every framework does. You will be able to look at Express's `app.get('/users/:id', handler)` and know *exactly* what is happening under the hood.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why does routing exist? What is the pain?
2. [The Thought](./THOUGHT.md) — How do you map URLs to handlers? What are the trade-offs?
3. [The Build](./BUILD.md) — Line-by-line construction of the router
4. [The Decisions](./DECISIONS.md) — Why a `Map`? Why not `if/else` chains?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A router is a function that takes a request and asks: "which handler should I run for this URL and method?" It looks up the answer in a data structure — usually a `Map` or a tree — and calls the right handler. If no handler matches, it returns `404`. The whole job is dispatch.

The simplest router is an `if/else` chain. The next step is a `Map` of method+path → handler. The fancy step is a *prefix tree* (trie) for performance at thousands of routes. We build the middle one.

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

Test it:

```bash
node server.js

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

The pain of "one URL is one function" is solved. The pain of "many URLs is many ifs" is also solved — adding a new route is one line.

---

## What You Will Have Learned

- Why we use a `Map` (a data structure) and not an `if/else` chain
- The convention of `METHOD PATH` as a routing key
- What `404` means and when to use it
- How to think about routes as data, not as control flow
- The boundary between "the framework" and "your code"

These are the foundations of *every* web framework. Project 03 will extend this with JSON bodies, and project 04 with query strings.

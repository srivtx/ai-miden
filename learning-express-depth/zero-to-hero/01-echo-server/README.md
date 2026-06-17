# Project 01: The Echo Server

> *"Before you can build, you must understand what you are building on."*

This is the genesis. There is no framework. There is no Express. There is no "magic." There is only Node.js's `node:http` module, a 30-line file, and the raw mechanics of how a server actually works.

If you have never written a server from scratch, you have only ever used other people's abstractions. This project removes the abstraction. After it, you will understand what every framework does *for* you, and you will never be mystified by a 500 error again.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why start here? What pain is this solving?
2. [The Thought](./THOUGHT.md) — How does HTTP actually work? What is a request? A response?
3. [The Build](./BUILD.md) — Line-by-line construction of the server
4. [The Decisions](./DECISIONS.md) — Why `node:http` and not Express? Why port 3000?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A server is a *long-running program that listens for connections*. When a client (browser, curl, mobile app) opens a TCP connection to your server, Node calls a function you gave it. That function receives two objects: a *request* (what the client wants) and a *response* (what you send back). You write a status line, some headers, and a body. You end the response. The connection closes. That is the entire model. Everything else — frameworks, ORMs, WebSockets, microservices — is decoration on top of this 30-line dance.

---

## The Code

This is the entire project. Read it once. Then read [BUILD.md](./BUILD.md) for the line-by-line.

```js
// server.js
const http = require('node:http');

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello, world.\n');
});

server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

Run it:

```bash
node server.js
```

Test it:

```bash
curl http://localhost:3000
# Hello, world.
```

That is the whole project. Now we begin to *understand* it.

---

## What You Will Have Learned

By the end of this project, you will be able to:

- Explain what a TCP socket is, at a hand-wavy level
- Explain what an HTTP request looks like on the wire (method, URL, headers, body)
- Explain what an HTTP response looks like (status, headers, body)
- Explain why we need a `Content-Type` header
- Explain why we need to call `res.end()` exactly once
- Write a 30-line HTTP server from memory

These are not party tricks. They are the foundation. Project 02 (Router) will fail catastrophically if this foundation is shaky.

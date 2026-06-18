# Project 05: The Body Parser

> *"The query is in the URL. The body is in the payload. Both are input."*

Project 04 taught us to read filters from the URL. But `POST`/`PUT`/`PATCH` need more than filters — they need to receive *data*. A client creating a user sends `{"name": "Eve"}` in the request *body*, not in the URL.

This project teaches the body. By the end, our API will:

1. Read the request body as a stream of bytes
2. Decode it as UTF-8 text
3. Parse it as JSON (if `Content-Type: application/json`)
4. Put the parsed object on `req.body`

The pattern mirrors project 04: parse once in the dispatch, use many times in handlers.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why does the body exist? Why is it a stream?
2. [The Thought](./THOUGHT.md) — What is a stream? How do we read it?
3. [The Build](./BUILD.md) — Line-by-line construction of the body parser
4. [The Decisions](./DECISIONS.md) — Why `data`/`end` events? Why not synchronous?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

The HTTP body is sent *after* the headers, as a stream of bytes. To read it, you listen for `'data'` events (each chunk of bytes) and an `'end'` event (when the body is done). You concatenate the chunks, decode as UTF-8, parse as JSON, and put the result on `req.body`. The whole sequence is async — you can't read the body synchronously because the data hasn't arrived yet. Streams are how Node handles this without blocking.

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

Test it:

```bash
node server.js

# Create a user
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Eve", "role": "admin"}'
# {"id":3,"name":"Eve","role":"admin"}

# Now list
curl http://localhost:3000/users
# 3 users

# Invalid JSON
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d 'not json'
# {"error":"Invalid JSON"}
```

The pain of "I cannot accept input" is solved. The body is read, parsed, and put on `req.body`. The handler does what it wants with it.

---

## What You Will Have Learned

- What a stream is, at a conceptual level
- How to read a stream with `'data'` and `'end'` events
- Why we use `Buffer.concat` to assemble chunks
- How to parse the body as JSON
- Why the dispatch is *async* (we wait for the body before dispatching)
- How to handle invalid JSON with `try/catch` and a `400`

These are the foundations of *input* in every web framework. Project 06 will add cookies (state across requests), and project 07 will adopt a real framework to handle all this with less code.

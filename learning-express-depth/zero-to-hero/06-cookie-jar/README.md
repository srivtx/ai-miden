# Project 06: The Cookie Jar

> *"HTTP is stateless. Cookies are the duct tape that make it stateful."*

Every request so far has been independent. The server has no memory of past requests. There is no "you" — only "a stranger who happens to be making this request right now."

This project adds *state across requests*. We do it with **cookies**: small pieces of data the server sends to the client, the client stores, and sends back on every subsequent request.

By the end, our server will:

1. Set a cookie on the response (`Set-Cookie: sessionId=abc123`)
2. Read cookies from the request (`Cookie: sessionId=abc123`)
3. Parse the cookie header into a JS object
4. Use a cookie value to remember who the user is

This is the foundation of every authenticated web app. It is also the foundation of the *final artifact* — our collaborative workspace needs to know who is logged in.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is HTTP stateless? Why does that hurt?
2. [The Thought](./THOUGHT.md) — What is a cookie? How does the protocol work?
3. [The Build](./BUILD.md) — Line-by-line construction of the cookie jar
4. [The Decisions](./DECISIONS.md) — Why cookies and not localStorage? Why not sessions in URL?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A cookie is a `name=value` pair that the server sends in `Set-Cookie`, the browser stores, and sends back in `Cookie` on every subsequent request to the same domain. To support cookies, the server must (a) parse the `Cookie` header into an object on every request, and (b) be able to set `Set-Cookie` on the response. We add a `cookies` object to the request and a `setCookie(res, name, value)` helper. The handler can read `req.cookies.userId` to know who the user is, and call `setCookie(res, 'userId', '42')` to remember them.

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

function setCookie(res, name, value) {
  res.setHeader('Set-Cookie', `${name}=${value}; HttpOnly; Path=/`);
}

function parseCookies(header) {
  const cookies = {};
  if (!header) return cookies;
  for (const pair of header.split(';')) {
    const [name, ...rest] = pair.trim().split('=');
    cookies[name] = rest.join('=');
  }
  return cookies;
}

const SESSIONS = new Map();
let nextSessionId = 1;

get('/', (req, res) => {
  json(res, 200, { message: 'Welcome to the API.' });
});

get('/health', (req, res) => {
  json(res, 200, { status: 'ok' });
});

post('/login', (req, res) => {
  const sessionId = String(nextSessionId++);
  SESSIONS.set(sessionId, { username: req.body.username, createdAt: Date.now() });
  setCookie(res, 'sessionId', sessionId);
  json(res, 200, { sessionId, username: req.body.username });
});

get('/me', (req, res) => {
  const session = SESSIONS.get(req.cookies.sessionId);
  if (!session) {
    json(res, 401, { error: 'Not authenticated' });
    return;
  }
  json(res, 200, session);
});

const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split('?');
  req.query = Object.fromEntries(new URLSearchParams(queryString || ''));
  req.cookies = parseCookies(req.headers.cookie);

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

# Login (no cookies yet)
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice"}' \
  -c cookies.txt
# {"sessionId":"1","username":"alice"}

# Use the cookie
curl http://localhost:3000/me -b cookies.txt
# {"username":"alice","createdAt":1700000000000}

# Without cookies
curl http://localhost:3000/me
# {"error":"Not authenticated"}
```

The pain of "I cannot recognize returning users" is solved. The server sets a cookie on login, the client stores it, and sends it on subsequent requests.

---

## What You Will Have Learned

- What `Set-Cookie` and `Cookie` headers are
- Why HTTP is stateless and how cookies bridge to state
- How to parse the `Cookie` header into an object
- How to set a `Set-Cookie` header
- The `HttpOnly` and `Path` attributes
- Why we use cookies and not localStorage (security, server-side control)

These are the foundations of *state* in every web app. Project 07 will adopt Express, which has `cookie-parser` and session middleware to do this with less code.

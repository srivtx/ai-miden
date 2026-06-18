# Project 07: The Framework Pivot + Session

> *"Stop reinventing. Start composing. This is the inflection point."*

For 6 projects, we have built a web server from scratch. The dispatch is now ~30 lines. It does URL parsing, cookie parsing, body parsing, route lookup, and 404 fallback. It works. It is also a *maintenance burden* — every new feature (validation, auth checks, logging, error handling) would add more lines to the dispatch.

This is the moment to stop reinventing. We will adopt **Express**, the de-facto Node web framework. Express is the *same dispatch* we built, with the same patterns (`req.query`, `req.body`, `req.cookies`) but with **middleware** — small composable functions that run before the handler.

By the end of this project, our server will be:
- Half the lines
- More powerful (middleware, error handling, etc.)
- The industry standard
- A foundation for the rest of the path

We will also add **session middleware** (`express-session`), which stores session data in memory and ties it to a cookie. The pain of "I want server-side state that survives multiple requests" is solved properly.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why adopt a framework? What pain does it solve?
2. [The Thought](./THOUGHT.md) — What is middleware? How does Express compose?
3. [The Build](./BUILD.md) — Line-by-line construction of the Express app
4. [The Decisions](./DECISIONS.md) — Why Express? Why middleware? What do we lose?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Express is a thin wrapper around `node:http` that adds **middleware** — a chain of functions that run before the handler. Each middleware can read the request, modify it, send a response, or call `next()` to pass to the next middleware. The chain ends with a route handler. We will rewrite our server in ~40 lines using Express, replacing our 90-line hand-rolled version. We will use `express.json()` (body parsing), `cookie-parser` (cookie parsing), and `express-session` (server-side sessions).

---

## The Code

```js
// server.js
const express = require('express');
const cookieParser = require('cookie-parser');
const session = require('express-session');

const app = express();

app.use(express.json());
app.use(cookieParser());
app.use(session({
  secret: 'dev-secret-change-in-prod',
  resave: false,
  saveUninitialized: false,
}));

const SESSIONS = new Map();

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API.' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.post('/login', (req, res) => {
  if (!req.body.username) {
    return res.status(400).json({ error: 'username required' });
  }
  req.session.username = req.body.username;
  req.session.createdAt = Date.now();
  res.json({ username: req.session.username });
});

app.get('/me', (req, res) => {
  if (!req.session.username) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  res.json({ username: req.session.username, createdAt: req.session.createdAt });
});

app.post('/logout', (req, res) => {
  req.session.destroy(() => {
    res.json({ message: 'Logged out' });
  });
});

app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

Setup:

```bash
npm init -y
npm install express cookie-parser express-session
node server.js
```

Test it:

```bash
# Login
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice"}' \
  -c cookies.txt
# {"username":"alice"}

# Get session
curl http://localhost:3000/me -b cookies.txt
# {"username":"alice","createdAt":1700000000000}

# Logout
curl -X POST http://localhost:3000/logout -b cookies.txt -c cookies.txt
# {"message":"Logged out"}

# After logout
curl http://localhost:3000/me -b cookies.txt
# {"error":"Not authenticated"}
```

The pain of "I am rewriting the dispatch for every feature" is solved. The pain of "I want proper server-side sessions" is solved. Express does the boilerplate; we write the business logic.

---

## What You Will Have Learned

- What middleware is and how it composes
- How `app.use(middleware)` registers a middleware
- The `req, res, next` signature
- How `express.json()` replaces our hand-rolled body parser
- How `cookie-parser` replaces our hand-rolled cookie parser
- How `express-session` provides server-side sessions
- Why Express is the standard (and why we adopted it now, not earlier)

These are the foundations of every Node web app. From here, every project uses Express. The patterns (`req.body`, `req.cookies`, `req.session`) become the default.

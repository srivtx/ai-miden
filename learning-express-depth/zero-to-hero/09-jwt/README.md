# Project 09: The JWT

> *"Sessions are server-side. Tokens are stateless. Stateless scales."*

Projects 06-08 used server-side sessions. The session ID is in a cookie; the session *data* is in the server's memory. This works, but:

1. The server has to look up the session on every request (memory hit)
2. Sessions don't share across processes (each process has its own memory)
3. Restart the server, all sessions are gone

**JWT (JSON Web Token)** solves this. A JWT is a *stateless* token: it contains the session data, signed. The server doesn't need to store anything. Any server with the secret can verify the token.

This project replaces sessions with JWT. The flow:

1. User logs in
2. Server creates a JWT containing `{ userId, username }` and signs it
3. Server sends the JWT to the client
4. Client stores the JWT (in localStorage, or as a cookie)
5. Client sends the JWT on every request (in `Authorization: Bearer <token>` or in a cookie)
6. Server verifies the JWT and trusts the data inside

The server has *zero* state. Any number of servers can verify any token. Tokens can be issued by one server and verified by another.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is server-side state bad? Why is stateless better?
2. [The Thought](./THOUGHT.md) — How does JWT work? What is signing? What is the structure?
3. [The Build](./BUILD.md) — Line-by-line construction of the JWT auth
4. [The Decisions](./DECISIONS.md) — Why JWT? Why not opaque tokens? Why not session IDs?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A JWT is a string with three parts: a header (algorithm and type), a payload (the data), and a signature (HMAC of header+payload using a secret). The three parts are base64-encoded and joined with dots. The signature proves the token was issued by us and wasn't tampered with. We use `jsonwebtoken` to sign and verify. The client sends the token in `Authorization: Bearer <token>`. The server verifies the token on every request. No server-side storage needed.

---

## The Code

```js
// server.js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const app = express();
app.use(express.json());

const USERS = new Map();

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API.' });
});

app.post('/signup', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'username and password required' });
  }
  if (USERS.has(username)) {
    return res.status(409).json({ error: 'username already taken' });
  }
  const hash = await bcrypt.hash(password, 10);
  USERS.set(username, { username, hash, createdAt: Date.now() });
  res.status(201).json({ username });
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'username and password required' });
  }
  const user = USERS.get(username);
  if (!user) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  const ok = await bcrypt.compare(password, user.hash);
  if (!ok) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  const token = jwt.sign({ userId: user.username, username: user.username }, SECRET, { expiresIn: TOKEN_TTL });
  res.json({ token, username: user.username });
});

function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'missing or invalid authorization header' });
  }
  const token = auth.slice(7);
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: 'invalid or expired token' });
  }
}

app.get('/me', authMiddleware, (req, res) => {
  res.json({ user: req.user });
});

app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

Setup:

```bash
npm install jsonwebtoken
node server.js
```

Test it:

```bash
# Signup
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}'
# {"username":"alice"}

# Login
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}'
# {"token":"eyJhbGciOiJIUzI1NiIs...","username":"alice"}

# Get me (with token)
curl http://localhost:3000/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
# {"user":{"userId":"alice","username":"alice","iat":...,"exp":...}}

# Get me (no token)
curl http://localhost:3000/me
# {"error":"missing or invalid authorization header"}

# Get me (bad token)
curl http://localhost:3000/me \
  -H "Authorization: Bearer not.a.token"
# {"error":"invalid or expired token"}
```

The pain of "I need to scale to multiple servers" is solved. The token is stateless. Any server with the secret can verify it.

---

## What You Will Have Learned

- What a JWT is (header.payload.signature)
- What signing means (HMAC with a secret)
- Why stateless tokens scale (no server-side lookup)
- The `Authorization: Bearer` header
- How to issue a token on login
- How to verify a token on every request
- Why we use `expiresIn` (tokens shouldn't live forever)

These are the foundations of *stateless authentication*. From here, every protected endpoint uses the same middleware. The server has no state.

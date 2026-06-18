# The Build

> *"The session is gone. The token is the session. The server has no state."*

We are going to replace sessions with JWT. The change from project 08: `express-session` is removed, login issues a JWT, and protected routes use `authMiddleware` to verify the token.

## Setup

```bash
npm install jsonwebtoken
```

The `jsonwebtoken` package is the standard Node JWT library. It uses HMAC for signing and verifying.

## The File

Create `server.js`. Fill it in.

---

## Lines 1-4: The Imports

```js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
```

Three imports. `jsonwebtoken` is new. `cookie-parser` and `express-session` are gone.

---

## Lines 6-7: The Configuration

```js
const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';
```

`SECRET` is the signing key. It must be a long random string in production. We use a placeholder for development.

`TOKEN_TTL` is how long the token is valid. `'7d'` is 7 days. You can also use `'1h'`, `'30m'`, or a number of seconds.

---

## Lines 9-10: The App and Middleware

```js
const app = express();
app.use(express.json());
```

We have only one middleware now: `express.json()` for body parsing. No session middleware, no cookie parser.

---

## Line 12: The USERS Map

```js
const USERS = new Map();
```

Same as project 08. Users are in memory. We'll move to a database in project 10.

---

## Lines 14-16: The Welcome Route

```js
app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API.' });
});
```

Unchanged.

---

## Lines 18-29: The Signup Route

```js
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
```

Identical to project 08. The signup flow doesn't change.

---

## Lines 31-46: The Login Route (CHANGED)

```js
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
```

### What changed

The end of the handler is different. Instead of setting `req.session.username = ...`, we create a JWT:

```js
const token = jwt.sign(
  { userId: user.username, username: user.username },
  SECRET,
  { expiresIn: TOKEN_TTL }
);
```

### `jwt.sign(payload, secret, options)`

- `payload` — the data to put in the token. We use `{ userId, username }`.
- `secret` — the signing key.
- `options.expiresIn` — when the token expires. `'7d'` means 7 days.

Returns a string. The token looks like `eyJhbGciOiJIUzI1NiIs...`.

We send the token in the response body:

```js
res.json({ token, username: user.username });
```

The client receives the token and stores it (in localStorage, etc.). On subsequent requests, the client sends the token in the `Authorization: Bearer <token>` header.

### Why no session?

Sessions require server-side state. The server has to remember who is logged in. With JWT, the *token* is the proof. The server has nothing to remember.

---

## Lines 48-61: The authMiddleware (NEW)

```js
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
```

### What it does

This is a middleware that protects routes. It runs before the route handler. It:

1. Reads the `Authorization` header
2. Checks it starts with `'Bearer '`
3. Extracts the token (everything after `'Bearer '`)
4. Verifies the token with `jwt.verify(token, SECRET)`
5. If valid, puts the payload on `req.user` and calls `next()` (passes to the handler)
6. If invalid, returns 401 (and doesn't call `next()`, so the handler doesn't run)

### Why the `'Bearer '` prefix?

The `Authorization` header format is `Bearer <token>`. The `Bearer` keyword tells the server "this is a bearer token" (vs. other auth schemes like `Basic` or `Digest`). We check for it explicitly.

### Why `auth.slice(7)`?

`auth` is `'Bearer eyJhbGciOiJI...`. `slice(7)` removes the first 7 characters (`'Bearer '`) and returns just the token.

### `jwt.verify(token, secret)`

This verifies the token's signature. It:

1. Splits the token into header, payload, signature
2. Recomputes the signature with the secret
3. Compares with the provided signature
4. Checks the `exp` claim
5. If everything checks out, returns the payload

If the token is invalid (bad signature, expired, malformed), it throws an error. We catch the error and return 401.

### Why `req.user = ...`?

The convention. After auth middleware, the handler can read `req.user` to know who's authenticated. This is similar to `req.session.username` in project 08, but more general (`req.user` can be any object, not just `{ username }`).

### Why the `try/catch`?

`jwt.verify` throws on invalid tokens. We catch and return 401. Without the try/catch, the throw would propagate to Express's default error handler, which returns 500. We want 401 for invalid tokens.

---

## Lines 63-65: The Me Route (CHANGED)

```js
app.get('/me', authMiddleware, (req, res) => {
  res.json({ user: req.user });
});
```

The `authMiddleware` is registered as the *first* argument to `app.get`. Express runs middleware in order. So `authMiddleware` runs first, and only if it calls `next()` does the handler run.

If `authMiddleware` returns 401 (invalid token), the handler doesn't run. The client gets 401.

The handler reads `req.user` (set by the middleware) and returns it. Notice: we don't query `USERS` to look up the user. The token contains the data. We trust the token.

---

## Lines 67-69: Start the Server

```js
app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

Same as project 07/08.

---

## The Full File

```js
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

---

## Run It

```bash
npm install jsonwebtoken
node server.js

# Signup
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}'
# {"username":"alice"}

# Login
TOKEN=$(curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo $TOKEN
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJhbGljZSIsInVzZXJuYW1lIjoiYWxpY2UiLCJpYXQiOjE3MDAwMDAwMDAsImV4cCI6MTcwMDYwNDgwMH0.fHs8...

# Get me (with token)
curl http://localhost:3000/me -H "Authorization: Bearer $TOKEN"
# {"user":{"userId":"alice","username":"alice","iat":1700000000,"exp":1700604800}}

# Get me (no token)
curl http://localhost:3000/me
# {"error":"missing or invalid authorization header"}

# Get me (bad token)
curl http://localhost:3000/me -H "Authorization: Bearer not.a.token"
# {"error":"invalid or expired token"}
```

---

## Experiments

### Experiment 1: Decode the token

```bash
echo "eyJhbGciOiJIUzI1NiIs..." | cut -d. -f2 | base64 -d
# {"userId":"alice","username":"alice","iat":1700000000,"exp":1700604800}
```

The payload is just base64. Anyone with the token can see the data. Don't put secrets in the payload.

### Experiment 2: Tamper with the token

Change one character in the token:

```bash
curl http://localhost:3000/me -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." # last char changed
# {"error":"invalid or expired token"}
```

The signature no longer matches. The server rejects.

### Experiment 3: Use a different secret

Change `SECRET` to `'other-secret'`. Restart. Old tokens are now invalid (the signature was made with `'dev-secret-change-in-prod'`, but verification uses `'other-secret'`).

### Experiment 4: Set a short TTL

```js
const TOKEN_TTL = '10s';
```

The token expires in 10 seconds. Wait 10 seconds, try `/me`. You get 401 "invalid or expired token".

### Experiment 5: Refresh tokens

A 10-second token forces the user to re-login every 10 seconds. Bad UX. The fix is a *refresh token* — a longer-lived token that can be exchanged for a new short-lived JWT. Out of scope for this project, but worth knowing.

### Experiment 6: Add the username to the response

```js
app.get('/me', authMiddleware, (req, res) => {
  res.json({ userId: req.user.userId, username: req.user.username });
});
```

The handler reads `req.user` and returns specific fields. The token contains the data; we just expose it.

### Experiment 7: Multiple protected routes

```js
app.get('/profile', authMiddleware, (req, res) => {
  res.json({ user: req.user });
});

app.get('/settings', authMiddleware, (req, res) => {
  res.json({ user: req.user });
});
```

The same middleware works on any number of routes. Just register it as the first argument.

---

## Summary

You now have stateless authentication. Login issues a JWT. The JWT contains the user's identity, signed. Protected routes verify the JWT with `authMiddleware`. The server has *zero* state — it doesn't store sessions, doesn't look up anything. Any server with the `SECRET` can verify any token.

This is the foundation of *scalable* authentication. You can run 1000 servers. The token works on all of them. You can issue on one server, verify on another. You can survive restarts. You can survive multi-region.

The trade-offs: tokens can't be revoked (until they expire), can't be invalidated (if the user's password changes), and can't be "logged out" (the client just deletes them). For most apps, the trade-off is worth it. For high-security apps, you add a revocation list or use short-lived JWTs with refresh tokens.

In project 10, we will move users from in-memory to a database. The auth flow stays the same. The storage becomes durable.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

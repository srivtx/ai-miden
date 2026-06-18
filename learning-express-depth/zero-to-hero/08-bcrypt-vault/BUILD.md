# The Build

> *"Two handlers. One hash. One compare. That's the whole auth flow."*

We are going to add real authentication. The change from project 07: `/signup` (new), `/login` (rewritten with bcrypt), and a `USERS` Map.

## Setup

```bash
npm install bcrypt
```

The `bcrypt` package is the de-facto Node bcrypt library. It uses a native binding (C code) for speed.

## The File

Create `server.js`. Fill it in.

---

## Lines 1-4: The Imports

```js
const express = require('express');
const cookieParser = require('cookie-parser');
const session = require('express-session');
const bcrypt = require('bcrypt');
```

Four imports. `bcrypt` is new.

---

## Lines 6-15: The App and Middleware (Unchanged from Project 07)

```js
const app = express();

app.use(express.json());
app.use(cookieParser());
app.use(session({
  secret: 'dev-secret-change-in-prod',
  resave: false,
  saveUninitialized: false,
}));
```

Same as project 07. The foundation is the same.

---

## Line 17: The USERS Map

```js
const USERS = new Map();
```

In-memory user storage. Keys are usernames, values are `{ username, hash, createdAt }`. The password is *never* stored. The hash is stored.

This is in memory. Restart the server, users are gone. We'll move to a database in project 10.

---

## Lines 19-21: The Welcome Route

```js
app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API.' });
});
```

Unchanged.

---

## Lines 23-34: The Signup Route (NEW)

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

### Why `async`?

`bcrypt.hash` is async (returns a Promise). Hashing is slow (cost 10 = 1024 iterations), so we don't want to block the event loop. `async/await` makes this look synchronous.

### Why `if (!username || !password)`?

Reject empty inputs. `username` and `password` are required. If either is missing, return 400. This is basic validation. We'll add proper validation (length, format, etc.) in project 14.

### Why `if (USERS.has(username))`?

Reject duplicate usernames. If the username is taken, return 409 Conflict. The user should pick a different name.

In a real app, you'd also check email uniqueness, etc. We don't have email yet.

### Why `const hash = await bcrypt.hash(password, 10)`?

`bcrypt.hash(password, 10)`:
- `password` — the plaintext password
- `10` — the cost factor (2^10 = 1024 iterations)

Returns a Promise. We await it. The result is a string like `'$2b$10$N9qo8uLOickgx2ZMRZoMye...'`.

### Why `USERS.set(username, { username, hash, createdAt: Date.now() })`?

Store the user. We store the *hash*, not the password. The `createdAt` is a timestamp.

### Why `res.status(201).json({ username })`?

201 Created — we created a new user. Return just the username (not the hash, not anything else). The user is now in `USERS`.

---

## Lines 36-51: The Login Route (REWRITTEN)

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
  req.session.username = user.username;
  req.session.userId = user.username;
  res.json({ username: user.username });
});
```

### The flow

1. Validate input (same as signup)
2. Look up the user by username
3. If not found, return 401 with "invalid credentials"
4. Compare the input password with the stored hash
5. If they don't match, return 401 with "invalid credentials"
6. If they match, set the session and return success

### Why the same error for both?

"invalid credentials" for both "user not found" and "wrong password". This prevents username enumeration. An attacker can't tell which usernames exist.

### Why `await bcrypt.compare(password, user.hash)`?

`bcrypt.compare(plaintext, hash)`:
- `plaintext` — the password the user just sent
- `hash` — the stored hash from signup

It extracts the salt and cost from the stored hash, hashes the input with the same salt and cost, and compares. Returns a Promise that resolves to `true` or `false`.

We await it.

### Why `req.session.username = user.username`?

On successful login, we set the session. The session is now tied to the user. Subsequent requests with this session cookie are authenticated as this user.

`userId` is also stored for future use (project 33, RBAC).

---

## Lines 53-58: The Me Route (Unchanged)

```js
app.get('/me', (req, res) => {
  if (!req.session.username) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  res.json({ username: req.session.username });
});
```

Same as project 07. The session is the source of truth. We don't query `USERS`.

---

## Lines 60-64: The Logout Route (Unchanged)

```js
app.post('/logout', (req, res) => {
  req.session.destroy(() => {
    res.json({ message: 'Logged out' });
  });
});
```

Same as project 07.

---

## Lines 66-68: Start the Server

```js
app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

Same as project 07.

---

## The Full File

```js
const express = require('express');
const cookieParser = require('cookie-parser');
const session = require('express-session');
const bcrypt = require('bcrypt');

const app = express();

app.use(express.json());
app.use(cookieParser());
app.use(session({
  secret: 'dev-secret-change-in-prod',
  resave: false,
  saveUninitialized: false,
}));

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
  req.session.username = user.username;
  req.session.userId = user.username;
  res.json({ username: user.username });
});

app.get('/me', (req, res) => {
  if (!req.session.username) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  res.json({ username: req.session.username });
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

---

## Run It

```bash
npm install bcrypt
node server.js

# Signup
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "hunter2"}'
# {"username":"alice"}

# Signup duplicate
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "other"}'
# {"error":"username already taken"}

# Login correct
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "hunter2"}' \
  -c cookies.txt
# {"username":"alice"}

# Login wrong password
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "wrong"}'
# {"error":"invalid credentials"}

# Login unknown user
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "nobody", "password": "anything"}'
# {"error":"invalid credentials"} (same as wrong password!)

# Get session
curl http://localhost:3000/me -b cookies.txt
# {"username":"alice"}
```

---

## Experiments

### Experiment 1: Inspect the stored hash

Add a debug endpoint:

```js
app.get('/debug/users', (req, res) => {
  const users = Array.from(USERS.values()).map((u) => ({
    username: u.username,
    hash: u.hash,
  }));
  res.json(users);
});
```

```bash
curl http://localhost:3000/debug/users
# [{"username":"alice","hash":"$2b$10$N9qo8uLOickgx2ZMRZoMye..."}]
```

You can see the bcrypt hash format: `$2b$10$...`. The `2b` is the algorithm version, `10` is the cost, and the rest is salt + hash.

### Experiment 2: Signup with the same password twice

```bash
# Signup alice
curl -X POST http://localhost:3000/signup -d '{"username":"alice","password":"hunter2"}' -H "Content-Type: application/json"

# Signup bob with the same password
curl -X POST http://localhost:3000/signup -d '{"username":"bob","password":"hunter2"}' -H "Content-Type: application/json"

# Inspect the hashes
curl http://localhost:3000/debug/users
# Different hashes! (different salts)
```

Two users with the same password have different hashes. The salt is random.

### Experiment 3: Timing attack

Compare the response time for "user not found" vs "wrong password":

```bash
time curl -X POST http://localhost:3000/login -d '{"username":"nobody","password":"x"}' -H "Content-Type: application/json" -s -o /dev/null
time curl -X POST http://localhost:3000/login -d '{"username":"alice","password":"wrong"}' -H "Content-Type: application/json" -s -o /dev/null
```

The "user not found" response is *faster* (no bcrypt compare). The "wrong password" is slower (bcrypt compare runs). An attacker can measure this. We accept the small leak.

### Experiment 4: Increase bcrypt cost

```js
const hash = await bcrypt.hash(password, 12);
```

Cost 12 is 4x slower. More secure against brute-force. Slower login.

### Experiment 5: Forgot `await`

```js
const hash = bcrypt.hash(password, 10);  // forgot await
USERS.set(username, { username, hash, createdAt: Date.now() });
```

`hash` is now a *Promise*, not a string. `bcrypt.compare` will fail with a weird error. Always `await` bcrypt.

### Experiment 6: Use `req.body` after `await`

```js
app.post('/signup', async (req, res) => {
  // ... await bcrypt.hash ...
  console.log(req.body);  // still works!
});
```

`req.body` is not consumed by `await`. The body is already parsed. We can read it any time.

---

## Summary

You now have real authentication. Users sign up with a password. The password is hashed with bcrypt and stored. Users log in with a password. The password is compared with the stored hash. If they match, the user is authenticated.

The plaintext password is never stored. The hash is what we keep. Even if `USERS` is leaked, the attacker gets hashes, not passwords. They cannot reverse the hash to get the password (in theory).

In project 09, we will replace sessions with **JWT** (JSON Web Tokens). JWTs are stateless — the server doesn't need to store the session. The session data is *in* the token, signed.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

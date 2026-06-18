# Project 08: The Bcrypt Vault

> *"Plaintext passwords are criminal. Hash them. Salt them. Slow them down."*

Project 07's `/login` accepts any `username`. There is no password. Anyone can be anyone. This is not authentication; this is roleplay.

This project adds real auth. We will:

1. Add a `POST /signup` that creates a user with a hashed password
2. Add a `POST /login` that verifies a password
3. Use **bcrypt** to hash and verify passwords
4. Store users in a (still in-memory) `USERS` Map

By the end, only users with the correct password can log in. The server never sees the plaintext password after signup — only the hash.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is plaintext storage bad? What is hashing?
2. [The Thought](./THOUGHT.md) — How does bcrypt work? What is a salt?
3. [The Build](./BUILD.md) — Line-by-line construction of the auth flow
4. [The Decisions](./DECISIONS.md) — Why bcrypt? Why not MD5? Why not SHA-256?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Passwords must never be stored in plaintext. If the database is stolen, every user's password is exposed. Instead, we *hash* the password with bcrypt: a slow, salted hash function. The hash is what we store. When the user logs in, we hash their input with the same salt and compare. bcrypt is slow on purpose — it makes brute-force attacks expensive. We use `bcrypt.hash(password, 10)` to hash and `bcrypt.compare(password, hash)` to verify. The flow: signup hashes, login compares.

---

## The Code

```js
// server.js
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

Setup:

```bash
npm install bcrypt
node server.js
```

Test it:

```bash
# Signup
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "hunter2"}'
# {"username":"alice"}

# Login (correct password)
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "hunter2"}' \
  -c cookies.txt
# {"username":"alice"}

# Login (wrong password)
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "wrong"}'
# {"error":"invalid credentials"}

# Get session
curl http://localhost:3000/me -b cookies.txt
# {"username":"alice"}
```

The pain of "anyone can be anyone" is solved. Only users with the correct password can log in.

---

## What You Will Have Learned

- Why plaintext password storage is criminal
- What hashing is (one-way function)
- What a salt is (random data added to the input)
- Why bcrypt is slow on purpose (brute-force resistance)
- The signup → hash → store flow
- The login → fetch → compare flow
- Why we return the same error for "user not found" and "wrong password" (timing attacks)

These are the foundations of *authentication*. From here, every project assumes passwords are bcrypt-hashed. Project 09 (JWT) will replace sessions with tokens.

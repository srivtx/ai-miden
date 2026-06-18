# The Build

> *"Express is our dispatch, plus middleware, plus helpers. We didn't replace the foundation; we adopted it."*

We are going to rewrite our server in Express. The behavior is the same. The code is shorter. The patterns (`req.body`, `req.cookies`, `req.session`) are now provided by middleware.

## Setup

Before we write the code, we need a `package.json` and the Express dependencies.

```bash
mkdir server && cd server
npm init -y
npm install express cookie-parser express-session
```

`npm init -y` creates a `package.json` with default values. `npm install` adds the three packages we need. The `node_modules/` folder is created (this is where the packages live). `package-lock.json` is created (this is the lockfile that pins the exact versions).

## The File

Create `server.js`. Fill it in.

---

## Lines 1-3: The Imports

```js
const express = require('express');
const cookieParser = require('cookie-parser');
const session = require('express-session');
```

We import three npm modules:

- **`express`** — the framework itself
- **`cookie-parser`** — middleware that parses cookies into `req.cookies`
- **`express-session`** — middleware that provides server-side sessions

These are not built into Node. We installed them with `npm install`.

---

## Line 5: The App

```js
const app = express();
```

`express()` is a factory function. Calling it creates an Express application. The `app` object has methods for registering routes and middleware.

This is similar to `http.createServer(handler)`, but with more methods.

---

## Lines 7-15: The Middleware

```js
app.use(express.json());
app.use(cookieParser());
app.use(session({
  secret: 'dev-secret-change-in-prod',
  resave: false,
  saveUninitialized: false,
}));
```

`app.use(middleware)` registers a middleware. It runs on *every* request, in the order registered. The chain is:

1. **`express.json()`** — reads the body, parses as JSON, sets `req.body`. (Replaces project 05's hand-rolled parser.)
2. **`cookieParser()`** — parses the `Cookie` header, sets `req.cookies`. (Replaces project 06's hand-rolled parser.)
3. **`express-session({...})`** — provides `req.session`. Reads the session cookie, looks up the session, sets `req.session`. Saves the session on response.

The order matters. We put `express.json()` first because the body might be needed by other middleware. `cookieParser()` before `express-session` because the session ID is in a cookie.

`secret: 'dev-secret-change-in-prod'` — used to sign the session cookie. In production, use a long random string from an environment variable.

`resave: false` — don't re-save unmodified sessions (performance).

`saveUninitialized: false` — don't create sessions for requests that don't touch `req.session` (memory).

---

## Lines 17-19: The Welcome Route

```js
app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API.' });
});
```

`app.get(path, handler)` registers a GET route. The handler is `(req, res) => { ... }` — the same shape as project 02.

`res.json(body)` is Express's helper for sending JSON. It sets the `Content-Type: application/json` header, stringifies the body, and ends the response. (Replaces project 03's `json(res, 200, body)` helper.)

---

## Lines 21-23: The Health Route

```js
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});
```

Same as project 02-06. Unchanged.

---

## Lines 25-31: The Login Route

```js
app.post('/login', (req, res) => {
  if (!req.body.username) {
    return res.status(400).json({ error: 'username required' });
  }
  req.session.username = req.body.username;
  req.session.createdAt = Date.now();
  res.json({ username: req.session.username });
});
```

The handler is the same shape as project 06's `POST /login`. The differences:

1. `req.body` is provided by `express.json()` (was: hand-rolled body parser)
2. `req.session` is provided by `express-session` (was: in-memory `SESSIONS` Map)
3. `res.status(400).json({...})` is chainable: set status, send JSON (was: `json(res, 400, {...})`)

The flow:
1. Validate the body has a username (else 400)
2. Store the username in the session
3. Store the createdAt timestamp
4. Respond with the username

`express-session` handles the rest. It will:
- Set a `Set-Cookie: connect.sid=...` header on the response
- Save the session data to the store (in-memory by default)
- On subsequent requests, recognize the cookie and load the session

### Why `return res.status(...).json(...)`?

The `return` is important. Without it, the handler continues. The next line (`req.session.username = ...`) would run after the response. The middleware chain would be confused (you can't send a response twice). The `return` exits the handler early.

This is a common Express pattern: `return res.status(...).json(...)` for early returns.

---

## Lines 33-38: The Me Route

```js
app.get('/me', (req, res) => {
  if (!req.session.username) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  res.json({ username: req.session.username, createdAt: req.session.createdAt });
});
```

The same as project 06's `GET /me`. We read `req.session.username`. If not set, 401. Otherwise, return the session data.

`req.session` is a regular object. We can read or write any properties.

---

## Lines 40-44: The Logout Route

```js
app.post('/logout', (req, res) => {
  req.session.destroy(() => {
    res.json({ message: 'Logged out' });
  });
});
```

`req.session.destroy(callback)` ends the session. The callback is called after the session is removed from the store. Inside the callback, we send the response.

This is slightly awkward — why a callback? Because session destruction is async (it has to remove from the store). The callback runs when it's done.

A more modern approach is `async/await`:

```js
app.post('/logout', async (req, res) => {
  await req.session.destroy();
  res.json({ message: 'Logged out' });
});
```

`req.session.destroy()` returns a Promise in newer versions of `express-session`. We use the callback form to be explicit.

---

## Lines 46-48: Start the Server

```js
app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

`app.listen(port, callback)` starts the server. Internally, it calls `http.createServer(app).listen(port, callback)`. The callback runs when the server is ready.

Same as `server.listen()` from project 01, just on the `app` object instead of the raw server.

---

## The Full File

```js
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

About 40 lines. Compare to project 06's 90 lines. Half the code, same behavior, more features.

---

## Run It

```bash
npm install express cookie-parser express-session
node server.js

# Login
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice"}' \
  -c cookies.txt
# {"username":"alice"}

# Inspect cookies
cat cookies.txt
# connect.sid=... (signed session ID)

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

---

## Experiments

### Experiment 1: Forget `express.json()`

Comment out `app.use(express.json())`. Restart. Send a `POST /login` with a body. `req.body` is `undefined`. The handler crashes. The error handler returns a default 500.

The lesson: middleware is order-dependent and necessary. `req.body` is provided by `express.json()`.

### Experiment 2: Forget `cookieParser()`

Comment out `app.use(cookieParser())`. Restart. The session cookie is set, but `req.cookies` is `undefined`. `express-session` still works (it has its own cookie parsing internally), but we can't read other cookies. For this app, we don't read other cookies, so it works.

### Experiment 3: Use the session in middleware

```js
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url} - ${req.session.username || 'anonymous'}`);
  next();
});
```

This is a *custom middleware*. It runs on every request and logs the user. The seed of project 16 (Logger) and project 33 (RBAC).

### Experiment 4: Add an error handler

```js
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal Server Error' });
});
```

This is a *4-argument middleware*. Express recognizes the 4-arg signature as an error handler. It runs when a previous middleware calls `next(err)`. The seed of project 15 (Error Wall).

### Experiment 5: Add path parameters

```js
app.get('/users/:id', (req, res) => {
  res.json({ id: req.params.id });
});
```

```bash
curl http://localhost:3000/users/42
# {"id":"42"}
```

`req.params` is the path parameters object. We don't have this in our hand-rolled router. Express gives it for free. The seed of project 11 (Foreign Key).

### Experiment 6: Use `res.send` for non-JSON

```js
app.get('/text', (req, res) => {
  res.send('just a string');
});
```

`res.send(body)` sends any body. If the body is a string, it sets `Content-Type: text/html` by default. If it's an object, it stringifies as JSON. If it's a Buffer, it sends the bytes.

### Experiment 7: Add a 404 handler

```js
app.use((req, res) => {
  res.status(404).json({ error: 'Not Found' });
});
```

This is a *catch-all* middleware. It runs for any request that didn't match a route. The seed of project 15 (Error Wall).

---

## Summary

You now have an Express app. The dispatch is replaced. The handlers are similar. The patterns (`req.body`, `req.session`) are provided by middleware. The code is half the size of project 06.

This is the inflection point. From here, every project uses Express. The patterns are stable. The handlers stay the same shape. We add features by adding middleware and writing handlers.

The next project adds real auth: passwords, hashing, and storage.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

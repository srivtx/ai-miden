# The Build

> *"Cookies are tiny. The protocol is simple. The implications are deep."*

We are going to add cookie support. Two new helpers (`parseCookies`, `setCookie`), one new line in the dispatch (`req.cookies = parseCookies(...)`), and two new handlers (`POST /login`, `GET /me`).

## The File

Create `server.js`. Fill it in.

---

## Lines 1-22: The Router and Helper (Unchanged)

```js
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
```

Same as projects 02-05.

---

## Lines 24-28: The setCookie Helper

```js
function setCookie(res, name, value) {
  res.setHeader('Set-Cookie', `${name}=${value}; HttpOnly; Path=/`);
}
```

### What it does

Sets a `Set-Cookie` header on the response with the given name and value. The `HttpOnly; Path=/` are *attributes* that affect how the browser handles the cookie.

### Why `HttpOnly`?

Tells the browser: "this cookie is not accessible to JavaScript." `document.cookie` won't show it. This protects against XSS attacks that try to read the cookie.

### Why `Path=/`?

Tells the browser: "send this cookie for every URL on this domain." Without it, the cookie would only be sent for the path that set it. For an API, we want it everywhere.

### Why a helper?

If we set cookies in 5 places, we'd have 5 copies of `'name=value; HttpOnly; Path=/'`. A helper centralizes it. If we later want to add `SameSite=Strict` or `Secure`, we change one place.

---

## Lines 30-37: The parseCookies Helper

```js
function parseCookies(header) {
  const cookies = {};
  if (!header) return cookies;
  for (const pair of header.split(';')) {
    const [name, ...rest] = pair.trim().split('=');
    cookies[name] = rest.join('=');
  }
  return cookies;
}
```

### What it does

Takes a `Cookie` header string and returns an object.

### Why this parser?

The `Cookie` header looks like `name1=value1; name2=value2`. Split on `;` gives `['name1=value1', ' name2=value2']`. Trim each. Split each on `=`. The first part is the name; the rest is the value (in case the value has `=` in it, like a base64 string).

For `'sessionId=abc123; theme=dark'`:

- Split on `;` → `['sessionId=abc123', ' theme=dark']`
- Trim each → `['sessionId=abc123', 'theme=dark']`
- Split on `=` → `[['sessionId', 'abc123'], ['theme', 'dark']]`
- Build object → `{ sessionId: 'abc123', theme: 'dark' }`

### Why `if (!header) return cookies`?

If the client has never sent a cookie, `req.headers.cookie` is `undefined`. We return an empty object so handlers can safely do `req.cookies.sessionId` (which will be `undefined`).

### Why not use a library?

`cookie` is a popular npm package. It handles edge cases (escaping, etc.) better than our hand-rolled parser. We use the hand-rolled one because we want to understand the protocol. Project 07 (Express) will use `cookie-parser`.

---

## Lines 39-42: The SESSIONS Map

```js
const SESSIONS = new Map();
let nextSessionId = 1;
```

### What it does

In-memory session storage. Keys are session IDs, values are session data (e.g., `{ username, createdAt }`).

### Why a Map?

Same as the routes Map. Key-value lookup, fast.

### Why `nextSessionId`?

To generate unique session IDs. In a real system, you'd use `crypto.randomUUID()`. For development, incrementing numbers is fine.

### Why in memory?

For development. In production, you'd use Redis (project 23) or a database (project 10). Memory doesn't survive restarts, and doesn't share across processes.

---

## Lines 44-67: The Handlers

```js
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
```

### `POST /login`

1. `const sessionId = String(nextSessionId++);` — generate a new ID, as a string (cookies are strings)
2. `SESSIONS.set(sessionId, { username: req.body.username, createdAt: Date.now() });` — store the session
3. `setCookie(res, 'sessionId', sessionId);` — tell the browser to remember this
4. `json(res, 200, { sessionId, username: ... });` — respond with the ID and username (in the body, for clients that don't use cookies)

The user is now "logged in" — they have a session, and the browser has a cookie that points to it.

### `GET /me`

1. `const session = SESSIONS.get(req.cookies.sessionId);` — look up the session by the cookie
2. If no session, return 401
3. If found, return the session data

This is the *identity* endpoint. The server uses the cookie to recognize the user.

### Why `401` for unauthenticated?

`401 Unauthorized` is the right code. The request lacks valid authentication. The client should log in.

`403 Forbidden` is for "you're authenticated but not allowed." That's a different case (project 33, RBAC).

---

## Lines 69-95: The Server and Dispatch

```js
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

### The new line

```js
req.cookies = parseCookies(req.headers.cookie);
```

This is the only new line. It reads the `Cookie` header (if any) and parses it into an object on `req.cookies`. The handler can now do `req.cookies.sessionId`.

### Why here (and not inside the `'end'` listener)?

Because the `Cookie` header is in the request headers, which are available immediately (before the body). The body is sent after the headers, so we wait for `'end'` to read it. The `Cookie` header is *not* in the body — it's a regular header. So we can parse it synchronously, before the body.

The order is:

1. Parse URL (synchronous, available immediately)
2. Parse query (synchronous, available immediately)
3. **Parse cookies (synchronous, available immediately — NEW)**
4. Read body (async, wait for `'end'`)
5. Dispatch to handler (after body)

This is the right order. Cookies are part of the *request metadata*, not the *request payload*.

---

## The Full File

```js
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

---

## Run It

```bash
node server.js

# Login (save the cookie to a file)
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice"}' \
  -c cookies.txt
# {"sessionId":"1","username":"alice"}

# Inspect the cookie file
cat cookies.txt
# # Netscape HTTP Cookie File
# ...
# localhost FALSE / FALSE 0 sessionId 1

# Use the cookie
curl http://localhost:3000/me -b cookies.txt
# {"username":"alice","createdAt":1700000000000}

# Without cookies
curl http://localhost:3000/me
# {"error":"Not authenticated"}

# With a wrong session ID
curl http://localhost:3000/me -H "Cookie: sessionId=999"
# {"error":"Not authenticated"}
```

---

## Experiments

### Experiment 1: Set multiple cookies

```js
function setCookie(res, name, value) {
  const existing = res.getHeader('Set-Cookie') || [];
  const list = Array.isArray(existing) ? existing : [existing];
  list.push(`${name}=${value}; HttpOnly; Path=/`);
  res.setHeader('Set-Cookie', list);
}
```

Now `setCookie(res, 'a', '1'); setCookie(res, 'b', '2')` sets two cookies.

### Experiment 2: Forget HttpOnly

Comment out `; HttpOnly`. The cookie is now readable by JavaScript. Open a browser, log in, open DevTools, and `document.cookie` will show the session ID. Less secure, but useful for debugging.

### Experiment 3: Forged session ID

```bash
curl http://localhost:3000/me -H "Cookie: sessionId=99999"
# {"error":"Not authenticated"}
```

`sessionId=99999` is not in `SESSIONS`, so 401. We can't fake a session ID without knowing the format. (In a real system, you'd use `crypto.randomUUID()` to make them unguessable.)

### Experiment 4: Logout

Add a `POST /logout` handler:

```js
post('/logout', (req, res) => {
  SESSIONS.delete(req.cookies.sessionId);
  res.setHeader('Set-Cookie', 'sessionId=; Max-Age=0; Path=/');
  json(res, 200, { message: 'Logged out' });
});
```

`Max-Age=0` tells the browser to delete the cookie immediately. The session is also removed from `SESSIONS`.

### Experiment 5: Cookie without Path

Comment out `; Path=/`. The cookie is only sent for the path that set it. If you set it on `/login`, it's not sent on `/me`. Try it.

### Experiment 6: Inspect with the browser

Open a browser, go to `http://localhost:3000`. Then in DevTools → Application → Cookies, you can see the cookies the server set. Try logging in with `fetch` and watch the cookie appear.

### Experiment 7: Log the cookies

```js
req.cookies = parseCookies(req.headers.cookie);
console.log('cookies:', req.cookies); // <-- add this
```

Every request logs its cookies. The seed of project 16 (Logger).

---

## Summary

You now have cookies. The server sets them on login, the browser stores them, and sends them on every subsequent request. The server can recognize returning users.

The pattern: **parse headers in the dispatch, expose as `req.cookies` (or `req.query`, `req.body`)**. The handler doesn't need to know how parsing works. It just reads `req.cookies.sessionId`.

The dispatch is now a real *framework*. It does:

- URL parsing (path + query)
- Cookie parsing
- Body parsing (with error handling)
- Route lookup
- 404 fallback

This is ~50 lines. It's a real web framework's core. Project 07 will adopt Express, which is exactly this dispatch plus middleware plus helpers. You'll understand Express because you built its core.

In project 07, we will *not* add new features. We will *replace* our hand-rolled dispatch with Express, and use its middleware for the same things. The handler interface stays the same.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

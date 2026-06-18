# The Thought

> *"Cookies are tiny pieces of data the browser stores and sends back. The server can read them. The server can set them. That's the whole API."*

## What a Cookie Is

A cookie is a `name=value` pair. The server sends it in the `Set-Cookie` response header. The browser stores it. The browser sends it back in the `Cookie` request header on subsequent requests to the same domain.

Example:

```
HTTP/1.1 200 OK
Set-Cookie: sessionId=abc123; HttpOnly; Path=/
Content-Type: application/json

{"userId": 1}
```

The browser sees `Set-Cookie: sessionId=abc123` and stores `sessionId=abc123` for the domain `localhost`. On the next request to `localhost`, the browser sends:

```
GET /me HTTP/1.1
Cookie: sessionId=abc123
```

The server reads the `Cookie` header and knows who the user is.

## The Cookie Attributes

The `Set-Cookie` header can have attributes after the `name=value`:

- **`HttpOnly`** — the cookie is not accessible to JavaScript (`document.cookie` won't see it). This protects against XSS attacks that try to steal the cookie.
- **`Path=/`** — the cookie is sent for all paths on this domain. Default is the path of the URL that set it.
- **`Domain=example.com`** — the cookie is sent to this domain and subdomains. Default is the exact domain of the URL that set it.
- **`Secure`** — the cookie is only sent over HTTPS. We don't set this in development.
- **`SameSite=Strict|Lax|None`** — controls cross-origin cookie sending. `Strict` is safest; `Lax` is the modern default; `None` is required for cross-site (with `Secure`).
- **`Max-Age=3600`** — the cookie expires in 3600 seconds. Without this, the cookie is a *session cookie* — it dies when the browser closes.
- **`Expires=...`** — explicit expiration date.

We use `HttpOnly; Path=/`. We don't use `Secure` (we're on plain HTTP). We don't use `Max-Age` (session cookies are fine for development).

## How to Set a Cookie

In Node, set the `Set-Cookie` header before `res.end()`:

```js
res.setHeader('Set-Cookie', 'sessionId=abc123; HttpOnly; Path=/');
```

To set multiple cookies, use an array:

```js
res.setHeader('Set-Cookie', [
  'sessionId=abc123; HttpOnly; Path=/',
  'theme=dark; Path=/',
]);
```

We wrap this in a helper:

```js
function setCookie(res, name, value) {
  res.setHeader('Set-Cookie', `${name}=${value}; HttpOnly; Path=/`);
}
```

Note: this *overwrites* any previous `Set-Cookie` header for the same name. If you want multiple cookies, you'd need to handle that. We don't need that here.

## How to Read a Cookie

The `Cookie` request header is a single string with all cookies concatenated by `; `:

```
Cookie: sessionId=abc123; theme=dark
```

To parse it, split on `; `, then on `=`:

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

`header.split(';')` gives `['sessionId=abc123', ' theme=dark']` (note the leading space on the second). We trim each pair, then split on `=`. The first part is the name; the rest is the value (in case the value has `=` in it, like a base64 string).

`parseCookies('sessionId=abc123; theme=dark')` returns `{ sessionId: 'abc123', theme: 'dark' }`.

If there's no `Cookie` header (no cookies set yet), `req.headers.cookie` is `undefined`. We return `{}`.

## Why Cookies and Not localStorage

JavaScript in the browser has `localStorage` — a key-value store that persists across page reloads. Why not use that?

1. **localStorage is per-origin and per-browser.** It doesn't travel with the request. The server can't read it.
2. **The server has no control.** A user can edit localStorage. A user can clear it. The server can't enforce anything.
3. **Cross-tab consistency.** localStorage is shared across tabs of the same origin, but a user can open the app in two browsers and have different state. Cookies are tied to the browser, not the tab.

Cookies are the right tool when the *server* needs to recognize the user. localStorage is the right tool for client-only state (UI preferences, draft text).

## Why Cookies and Not Authorization Header

`Authorization: Bearer <token>` is the API convention. It's stateless, explicit, and standard. Why not use that?

1. **Browsers can't easily set headers.** A browser can send cookies automatically; setting a custom `Authorization` header requires JavaScript, which means CORS preflight, which is more friction.
2. **CSRF protection.** Cookies are vulnerable to CSRF (cross-site request forgery) — a malicious site can make a request that includes the user's cookies. Headers are not vulnerable to this.

The choice is contextual. For *browsers*, cookies are the path of least resistance. For *API clients* (mobile apps, server-to-server), `Authorization` is cleaner. We'll see both in this path.

## Sessions: The Other Half

A cookie is just a *token* — a string the server uses to look up *session data*. The session data is stored server-side. The cookie is the key; the data is the value.

In this project, the `SESSIONS` Map is the session store:

```js
const SESSIONS = new Map();
SESSIONS.set('abc123', { username: 'alice', createdAt: 1234567890 });
```

The cookie is `'sessionId=abc123'`. The handler reads `req.cookies.sessionId` and looks it up:

```js
const session = SESSIONS.get(req.cookies.sessionId);
```

This is *stateful* authentication. The server has the data. The cookie is just a pointer.

**Alternative (JWT)**: put the data *in* the cookie itself (signed). The server doesn't need to store anything. Stateless, but harder to revoke. We'll do that in project 09.

**Alternative (token in DB)**: store sessions in a database instead of memory. Survives restarts. We'll do that in project 10.

For now, in-memory is fine. We're learning the protocol, not the storage.

## Common Confusions (read these)

**Confusion 1: "Why does the cookie get sent automatically?"**
Because that's the spec. When a server sends `Set-Cookie`, the browser must store it. When the browser makes a request to the same domain, it must include the cookie in the `Cookie` header. This is a *contract*. Browsers that don't follow it aren't browsers.

**Confusion 2: "Can the client see the cookie?"**
With `HttpOnly`, no. JavaScript in the browser cannot read `document.cookie` for `HttpOnly` cookies. The cookie is sent with requests, but invisible to scripts. This protects against XSS.

**Confusion 3: "What if the user clears their cookies?"**
They get logged out. The session is still in `SESSIONS`, but the cookie is gone, so the user can't access it. This is a *soft* form of logout. The session data will eventually expire (or we can clean it up).

**Confusion 4: "What if someone steals the cookie?"**
They can impersonate the user. This is the cookie-stealing attack. Mitigations: `HttpOnly` (prevent XSS stealing), `Secure` (prevent sniffing on HTTP), `SameSite=Strict` (prevent CSRF). We use `HttpOnly`.

**Confusion 5: "What is CSRF?"**
Cross-Site Request Forgery. A malicious site tricks your browser into making a request to our server. Because the browser sends cookies automatically, the request is *authenticated* — the user didn't intend it, but the server thinks they did. Mitigations: `SameSite=Strict` (cookies aren't sent cross-site), CSRF tokens (a hidden form field that the attacker can't guess), and double-submit cookies. We don't have CSRF protection yet — we'll add `SameSite` in a later project.

**Confusion 6: "Why is the session data in a Map?"**
For development. In production, you'd use Redis (project 23) or a database (project 10). An in-memory Map works for a single process. If you have multiple processes or restarts, sessions are lost.

**Confusion 7: "What if two clients get the same sessionId?"**
Our `nextSessionId++` is process-local. In a real system, you'd use `crypto.randomUUID()` or a similar high-entropy generator. We'll switch to UUIDs in a later project.

## What We Are About to Build

A 90-line server that:

1. Parses the query (from project 04)
2. Parses the body (from project 05)
3. **NEW**: Parses the `Cookie` header into `req.cookies`
4. **NEW**: Has a `setCookie(res, name, value)` helper
5. **NEW**: Implements `POST /login` that creates a session
6. **NEW**: Implements `GET /me` that uses the cookie to identify the user

The dispatch is the same shape. Two new things in the dispatch (`req.cookies = ...`) and two new things in the handler set (`POST /login`, `GET /me`).

In [BUILD.md](./BUILD.md) we will go line by line.

# The Thought

> *"A JWT is three base64 strings joined by dots. The third one is the proof. The first two are the data. Trust the third, not the first two."*

## What a JWT Is

A JWT is a string with three parts, separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJhbGljZSIsInVzZXJuYW1lIjoiYWxpY2UifQ.fHs8...
│                                          │                                                                │
└── header (algorithm, type)                └── payload (data)                                               └── signature
```

Each part is a base64-encoded JSON object (or signature).

### Part 1: Header

The header describes the algorithm and token type:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

`HS256` means HMAC-SHA256 (symmetric — same secret for signing and verifying). Other options: `RS256` (RSA — different keys for signing and verifying), `ES256` (ECDSA), etc.

### Part 2: Payload

The payload is the *claims* — the data we want to send:

```json
{
  "userId": "alice",
  "username": "alice",
  "iat": 1700000000,
  "exp": 1700604800
}
```

`iat` is "issued at" (Unix timestamp). `exp` is "expiration" (Unix timestamp). Both are standard claims. We can add custom claims like `userId` and `username`.

### Part 3: Signature

The signature is the proof. It's computed as:

```
HMACSHA256(
  base64url(header) + "." + base64url(payload),
  secret
)
```

The server has the `secret`. Only the server can produce a valid signature. The signature proves the token was issued by us.

The client can read the header and payload (they're just base64). The client cannot create a valid signature without the secret.

## How the Server Verifies a Token

When a request comes in with `Authorization: Bearer <token>`:

1. Split the token on `.` to get header, payload, signature
2. Recompute the signature: `HMACSHA256(header + "." + payload, secret)`
3. Compare the recomputed signature with the provided signature
4. If they match, the token is valid (was signed by us, hasn't been tampered with)
5. Check `exp` — if the token is expired, reject

If everything checks out, the server trusts the payload. It uses `req.user.userId` and `req.user.username` as if they came from a session.

## Statelessness

Notice: the server has *zero* state. It doesn't look up anything. It just verifies the signature. This is the key property.

Any server with the secret can verify any token. You can run 1000 servers behind a load balancer. Each one can verify any token. No shared state.

You can also issue a token on one server and verify on another. The token is self-contained.

## The Trade-offs

Statelessness comes with trade-offs:

### 1. Cannot revoke

Once a token is issued, it's valid until `exp`. You can't revoke it without a *revocation list* (which is server-side state). For most apps, the short expiration (we use 7 days) is enough. If you need immediate revocation, you add a check: `if (revokedTokens.has(jti)) return 401`.

### 2. Cannot invalidate

If a user's password is changed, their existing tokens are still valid until `exp`. They could keep using the old token. The fix: include the password's hash version in the token. On every request, check the token's version against the current user's version. If they don't match, reject.

### 3. Cannot log out

`/logout` doesn't really work with stateless JWT. The server can't "destroy" the token. The client just deletes it. The token is still valid until `exp` — anyone who copied it can use it. For real logout, you need a revocation list (server-side state) or short expiration.

These trade-offs are why some apps use a hybrid: short-lived JWT (15 min) + long-lived refresh token (stored in DB, can be revoked).

For this project, we accept the trade-offs. The token is stateless. The user has to wait 7 days for it to expire (or just delete it from their client).

## The `Authorization: Bearer` Header

The standard way to send a JWT is in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

`Bearer` means "the bearer of this token is authenticated." The token is the credential.

The server reads the header, extracts the token (everything after `Bearer `), and verifies it.

This is *not* a cookie. The browser does not send `Authorization` headers automatically. The client (JavaScript) must add it to every request. This is why JWT is more common in API clients (mobile, server-to-server) than in browser apps (where cookies are easier).

For browser apps, you can also store the JWT in a cookie. But then you have CSRF. We use `Authorization: Bearer` for clarity.

## `jsonwebtoken` Library

`jsonwebtoken` is the standard Node JWT library. It has three functions we use:

### `jwt.sign(payload, secret, options)`

Creates a JWT. Returns a string.

```js
const token = jwt.sign(
  { userId: 'alice', username: 'alice' },
  SECRET,
  { expiresIn: '7d' }
);
```

- `payload` — the data to put in the token
- `secret` — the signing key
- `options.expiresIn` — when the token expires ('7d', '1h', 3600 seconds, etc.)

### `jwt.verify(token, secret)`

Verifies a JWT. Returns the payload if valid, throws if invalid.

```js
try {
  const payload = jwt.verify(token, SECRET);
  // payload.userId, payload.username, etc.
} catch (err) {
  // err.name: 'TokenExpiredError', 'JsonWebTokenError', 'NotBeforeError'
  // token is invalid
}
```

### `jwt.decode(token)`

Decodes a JWT *without* verifying. Returns the payload (or header). Useful for debugging.

```js
const payload = jwt.decode(token);
// payload is the data, but it's not verified
```

We use `sign` and `verify`. We don't use `decode` in production code (use `verify` instead).

## The Middleware

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

This is the auth middleware. It runs on protected routes. It:

1. Reads the `Authorization` header
2. Checks it starts with `Bearer `
3. Extracts the token (everything after `Bearer `)
4. Verifies the token with `jwt.verify`
5. If valid, puts the payload on `req.user` and calls `next()`
6. If invalid, returns 401

The handler can then use `req.user` to know who's authenticated.

## Common Confusions (read these)

**Confusion 1: "Can I read the data in the JWT?"**
Yes — it's just base64. The header and payload are *not encrypted*. They're just encoded. Anyone with the token can see the data. Don't put secrets in the payload (passwords, API keys, etc.).

**Confusion 2: "Is JWT encrypted?"**
No. JWT is *signed*, not *encrypted*. Signing proves the token is authentic. Encryption hides the data. JWT does the first, not the second. For encryption, use JWE (JSON Web Encryption) or just encrypt the payload manually.

**Confusion 3: "Where do I store the JWT on the client?"**
- **localStorage** — easy, but vulnerable to XSS (any script can read it)
- **sessionStorage** — same as localStorage but lost on tab close
- **Cookie (httpOnly)** — safer, but vulnerable to CSRF
- **In-memory (a variable)** — safest, but lost on page reload

The right answer depends on your threat model. For a typical web app, httpOnly cookie is the safest. For an API, `Authorization: Bearer` (where the client stores it) is fine.

**Confusion 4: "What if my secret leaks?"**
Anyone with the secret can forge tokens. They can become any user. Rotate the secret immediately. All existing tokens become invalid.

**Confusion 5: "HS256 vs RS256?"**
HS256 uses a *symmetric* key (the same secret for signing and verifying). RS256 uses an *asymmetric* key pair (private key signs, public key verifies). Use HS256 for single-service apps. Use RS256 when multiple services need to verify but only one should sign.

**Confusion 6: "What is `jti`?"**
JWT ID. A unique identifier for the token. Used for revocation lists. We don't use it.

**Confusion 7: "Why 7 days?"**
A balance between UX and security. Long enough that the user doesn't have to log in daily. Short enough that a leaked token is only useful for a week. For high-security apps, use 15 minutes + refresh tokens.

## What We Are About to Build

A ~50-line Express app that:

1. Has `POST /signup` and `POST /login` (unchanged from project 08)
2. Issues a JWT on successful login (instead of a session)
3. Sends the JWT in the response body
4. Has an `authMiddleware` that verifies the JWT
5. The `GET /me` route uses the middleware

The session middleware (`express-session`) is gone. The cookie-parser is gone. The handlers are slightly different — they read `req.user` instead of `req.session`.

In [BUILD.md](./BUILD.md) we will go line by line.

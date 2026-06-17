# 50 — JWT Auth

**New concept:** authentication with JSON Web Tokens.

When you log in to a website, the server gives you a "token" — a long string that proves who you are. You send this token with every request. The server checks it and knows it's you.

JWT is the most common format for these tokens. They're signed (the server can verify they're real) and can carry data (your user ID, email, etc.).

## Run it

```bash
npm install
node server.js
```

```bash
# Log in
RESP=$(curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "password123"}')
TOKEN=$(echo $RESP | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# Use the token
curl -H "Authorization: Bearer $TOKEN" http://localhost:3000/me
# { "user": { "sub": 1, "email": "alice@example.com", ... } }

# Try without a token
curl http://localhost:3000/me
# 401

# Try a bad password
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "wrong"}'
# 401
```

## How to think about it

When you go to a hotel, they give you a key card. The card is signed (only the hotel can issue it). It has your name and room number. Every time you open a door, you swipe the card. The door reader checks the signature and lets you in.

JWT is the same idea. The server signs the token. The client sends it. The server verifies the signature on every request.

## How to build it (line by line)

```js
const token = jwt.sign(
  { sub: user.id, email: user.email },
  SECRET,
  { expiresIn: '1h' }
);
```

**Lines 23-27.** Sign a token. Three parts:
- **Payload**: data to include (user ID, email)
- **Secret**: the key used to sign (kept on the server)
- **Options**: expiration, issuer, etc.

The result is a long string like `eyJhbGc...`. It's three base64-encoded parts separated by dots: header.payload.signature.

```js
function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing token' });
  }
  const token = auth.slice(7);  // Remove "Bearer "
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (e) {
    res.status(401).json({ error: 'Invalid token' });
  }
}
```

**Lines 35-47.** Middleware that verifies the token on every request.

**`Authorization: Bearer <token>`** is the standard format.

**`jwt.verify`** checks the signature and the expiration. If anything is wrong, it throws.

## What we learned

1. JWT is a signed token format
2. Login: verify credentials, return a token
3. Subsequent requests: send the token in the Authorization header
4. The server verifies the signature and the expiration
5. Tokens should have an expiration (1 hour is common)
6. Real systems: Auth0, Clerk, Firebase Auth, Supabase Auth

## What's next

You've now built apps with CRUD, real-time, file upload, search, rate limiting, scheduling, pub/sub, jobs, caching, analytics, and auth. These are the building blocks. From here, you can build anything.

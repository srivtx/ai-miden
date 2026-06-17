# JWT Demo — Issue, sign, verify, decode, refresh tokens

JWT (JSON Web Token) implementation from scratch using crypto. No external libraries. Shows: how JWTs work, what they contain, how to verify, why you need refresh tokens.

## Endpoints
```
POST /login          { email, password }  -> { accessToken, refreshToken, user }
POST /refresh        { refreshToken }     -> { accessToken }
GET  /me             (Authorization: Bearer ...)  -> user info
GET  /admin          (admin role required)       -> admin only
GET  /inspect?t=...  decode without verify
```

## Try
```bash
# Login
TOKEN=$(curl -X POST http://localhost:3000/login -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "x"}' | jq -r .accessToken)

# Use the token
curl -H "Authorization: Bearer $TOKEN" http://localhost:3000/me
# { user: { sub: 42, email: "alice@example.com", role: "user", iat: ..., exp: ... } }

# Decode without verify
curl 'http://localhost:3000/inspect?t='"$TOKEN"
```

## What this teaches
1. **JWT structure**: header.payload.signature (base64url encoded)
2. **HS256 signing**: HMAC-SHA256 with a shared secret
3. **Claims**: `sub` (subject/user id), `iat` (issued at), `exp` (expiration)
4. **Bearer token**: `Authorization: Bearer <token>`
5. **Access vs refresh tokens**: short-lived (1h) + long-lived (7d)
6. **Role-based access**: `requireRole('admin')` middleware
7. **Tamper detection**: signature doesn't match = 401

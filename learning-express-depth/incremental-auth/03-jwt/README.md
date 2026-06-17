# 03 — JWT (Auth)

Issue signed tokens on login. Verify them on every protected endpoint.

**What's new:**
- Login returns a JWT
- `auth` middleware verifies the token
- `/me` is a protected endpoint

**Why JWT?** Stateless. The server doesn't keep track of who's logged in. The token itself proves it. The server can verify the signature without looking anything up.

## Run
```bash
npm install && node server.js
```

```bash
# Signup
curl -X POST http://localhost:3000/auth/signup -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyPassword123"}'

# Login — returns a token
RESP=$(curl -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyPassword123"}')
TOKEN=$(echo $RESP | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# Use the token
curl -H "Authorization: Bearer $TOKEN" http://localhost:3000/me
# { user: { id: "u_...", email: "alice@example.com" } }

# Without token
curl http://localhost:3000/me
# 401 missing_token
```

## What this stage teaches
- JWT signing and verification
- Bearer token pattern
- Auth middleware
- Stateless authentication

## Next
**04-refresh** — short-lived access tokens, long-lived refresh tokens. Rotate them.

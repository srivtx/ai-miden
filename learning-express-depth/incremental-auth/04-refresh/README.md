# 04 — Refresh Tokens (Auth)

Short-lived access tokens (1h) + long-lived refresh tokens (7d). Refresh rotates both.

**What's new:**
- Login returns BOTH `access_token` and `refresh_token`
- Access token: 1 hour, used for every request
- Refresh token: 7 days, used only to get a new access token
- `/auth/refresh` rotates the refresh token (old one is revoked)
- `/auth/logout` revokes the refresh token
- The access token has `type: 'access'`, so it can't be used as a refresh token

**Why two tokens?** If you only have an access token, when it expires the user has to log in again. With a refresh token, the app can silently get a new access token without the user noticing.

**Why rotate the refresh token?** If a refresh token is stolen, the attacker can use it. By rotating (issuing a new one, revoking the old), the window is smaller.

**The flow:**
1. User logs in → gets access_token (1h) and refresh_token (7d)
2. App uses access_token for 1 hour
3. Access token expires → app sends refresh_token
4. Server rotates: revokes old refresh, issues new access AND new refresh
5. App continues for another 1h with new access
6. After 7 days, refresh expires, user must log in again

## Run
```bash
npm install && node server.js
```

```bash
# Login
RESP=$(curl -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyPassword123"}')
ACCESS=$(echo $RESP | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
REFRESH=$(echo $RESP | grep -o '"refresh_token":"[^"]*' | cut -d'"' -f4)

# Use access token
curl -H "Authorization: Bearer $ACCESS" http://localhost:3000/me

# Refresh
RESP2=$(curl -X POST http://localhost:3000/auth/refresh -H "Content-Type: application/json" -d "{\"refresh_token\": \"$REFRESH\"}")
# Get new access AND new refresh

# Try old refresh — revoked
curl -X POST http://localhost:3000/auth/refresh -H "Content-Type: application/json" -d "{\"refresh_token\": \"$REFRESH\"}"
# 401 revoked

# Logout
curl -X POST http://localhost:3000/auth/logout -H "Content-Type: application/json" -d "{\"refresh_token\": \"$REFRESH2\"}"
```

## What this stage teaches
- Access + refresh token pattern
- Token rotation
- Token type (`type: 'access'`)
- Revocation

## Next
**05-reset-password** — forgot password flow. Email a reset link, set a new password.

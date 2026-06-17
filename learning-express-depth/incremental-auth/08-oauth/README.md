# 08 — OAuth (Auth)

Login with third-party providers (Google, GitHub). The OAuth 2.0 flow.

**What's new:**
- `/auth/:provider/login` — generates the redirect URL
- `/auth/:provider/callback` — handles the provider's response
- Link an existing account to a provider
- Issue a JWT on successful OAuth login

**Why OAuth?** Users don't want another password. With OAuth, they log in with Google, GitHub, etc. You get their email and basic profile. You don't handle their password.

**The flow:**
1. User clicks "Login with Google"
2. Server redirects to Google's auth page
3. User logs in at Google
4. Google redirects back to your callback URL with a `code`
5. Server exchanges `code` for an access token at Google
6. Server uses the access token to get the user's profile
7. Server creates or finds a local user
8. Server issues its own JWT

**State parameter:** a random value sent in step 2, verified in step 4. Prevents CSRF attacks.

## Run
```bash
npm install && node server.js
```

```bash
# Step 1: get the redirect URL
curl http://localhost:3000/auth/google/login
# { redirect_url: "https://accounts.google.com/...", state: "..." }

# Step 2: simulate the callback (real one would have a real code from Google)
curl 'http://localhost:3000/auth/google/callback?code=valid_abc123'
# { user: { id, email }, token: "..." }

# Link an existing user
curl -X POST http://localhost:3000/auth/github/link -H "Content-Type: application/json" \
  -d '{"user_id": "u_xxx", "code": "valid_github_xyz"}'
```

## What this stage teaches
- OAuth 2.0 authorization code flow
- State parameter for CSRF protection
- Linking providers to existing accounts
- Why OAuth is preferred over passwords

## Next
**09-api-keys** — programmatic access. Long-lived tokens for scripts and integrations.

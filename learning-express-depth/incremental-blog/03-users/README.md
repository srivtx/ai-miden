# 03 — Users

User accounts. Signup, login, profile, JWT.

**What's new:**
- `users` table: email, password_hash, salt, display_name, bio, avatar_url
- Signup with email + password (8+ chars)
- Login returns JWT
- Profile is public, update requires auth
- PBKDF2 password hashing (we've seen this in the todo app)

**Why a separate profile?** The auth user (id, email, password) is for authentication. The profile (display_name, bio, avatar) is for display. Different concerns, different fields.

## Run
```bash
npm install && node server.js
```

```bash
# Signup
RESP=$(curl -X POST http://localhost:3000/auth/signup -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "password123", "display_name": "Alice"}')
TOKEN=$(echo $RESP | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# See your profile
curl -H "Authorization: Bearer $TOKEN" http://localhost:3000/me

# Update profile
curl -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  http://localhost:3000/users/me -d '{"bio": "I write about code"}'
```

## What this stage teaches
- Auth user vs profile user
- Public vs private fields
- Self-update via /me
- Same JWT pattern from the todo app

## Next
**04-roles** — admins, editors, authors. Different permissions.

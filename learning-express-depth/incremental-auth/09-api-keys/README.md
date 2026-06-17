# 09 — API Keys (Auth)

Programmatic access. Long-lived keys for scripts, integrations, CI.

**What's new:**
- Create keys: `POST /api-keys` returns the full key (only chance to see it)
- List keys: `GET /api-keys` returns prefixes only (not secrets)
- Revoke: `DELETE /api-keys/:id`
- Verify: `Authorization: Bearer ak_<prefix>_<secret>` middleware
- Track `last_used_at`
- Optional expiration

**Key format:** `ak_<8 hex chars>_<24 base64 chars>`. The prefix is shown in listings. The secret is hashed in the DB. The full key is shown only once at creation.

**Why?** If your DB leaks, the attacker gets hashes, not the actual keys. They can't use them. The user can see "ah, my key was ak_abc12345_..." in their listing — that's safe to share for support.

## Run
```bash
npm install && node server.js
```

```bash
# Create a key
KEY=$(curl -X POST http://localhost:3000/api-keys -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "name": "My script", "scopes": ["read", "write"]}' | grep -o '"key":"[^"]*' | cut -d'"' -f4)

# List (no secrets shown)
curl 'http://localhost:3000/api-keys?user_id=u_alice'
# [{ name: "My script", key_prefix: "abc12345", ... }]

# Use the key
curl -H "Authorization: Bearer $KEY" http://localhost:3000/api/data

# Revoke
curl -X DELETE "http://localhost:3000/api-keys/k_xxx?user_id=u_alice"
```

## What this stage teaches
- API key generation and storage
- Hashing secrets (so DB leak doesn't compromise them)
- Prefix-based identification
- Last-used tracking
- Show-once pattern

## Next
**10-audit** — the final stage. Log every auth event for security.

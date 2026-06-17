# 10 — Audit (Auth, final stage)

Log every auth event. Login, logout, password change, 2FA enable, suspicious activity.

**What's new:**
- `audit_log` table: every event recorded
- Middleware captures IP and user-agent
- `logEvent()` helper for consistent logging
- Query endpoints: by user, by event, by time, by success
- Suspicious IP detection (3+ failed logins in an hour)

**Why audit?** Compliance (SOC 2, GDPR, HIPAA). Forensics ("was the account hacked?"). Monitoring ("are we under attack?"). User trust ("show me my recent activity").

**What to log:**
- Successful logins
- Failed logins
- Logouts
- Password changes
- 2FA enable/disable
- API key creation/revocation
- Suspicious activity

**What NOT to log:** passwords, tokens, secrets. The log itself is sensitive.

## Run
```bash
npm install && node server.js
```

```bash
# Login (success or fail both logged)
curl -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" -H "X-Forwarded-For: 1.2.3.4" \
  -H "User-Agent: Mozilla/5.0" \
  -d '{"email": "alice@example.com", "password": "password123"}'

# Failed logins (3 from same IP → suspicious)
for i in {1..3}; do
  curl -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" \
    -H "X-Forwarded-For: 5.6.7.8" \
    -d '{"email": "alice@example.com", "password": "wrong"}'
done

# Query the log
curl http://localhost:3000/admin/audit

# Find suspicious IPs
curl http://localhost:3000/admin/suspicious-ips
# [{ ip: "5.6.7.8", failed_count: 3 }]
```

## What this stage teaches
- Audit log pattern
- IP and user-agent capture
- Event types and naming
- Suspicious pattern detection
- What to log (and not log)

## 🎉 10 stages complete!

The full auth service has:
- Signup ✓
- Login (with lockout) ✓
- JWT (signed tokens) ✓
- Refresh (rotation) ✓
- Reset password (email link) ✓
- Email verify ✓
- 2FA (TOTP) ✓
- OAuth (Google/GitHub) ✓
- API keys (programmatic) ✓
- Audit (every event) ✓

This is how Auth0, Clerk, Supabase Auth, Firebase Auth all work. Same 10 patterns, different code.

## The 10 patterns
1. **Signup** — email regex, password rules, hashing
2. **Login** — constant-time, lockout, no enumeration
3. **JWT** — signed, stateless, verifiable
4. **Refresh** — short-lived + long-lived, rotate
5. **Reset password** — token, TTL, single-use
6. **Email verify** — confirm email ownership
7. **2FA** — TOTP, second factor
8. **OAuth** — third-party auth, no password
9. **API keys** — programmatic access
10. **Audit** — log every event

These 10 patterns are the building blocks of every auth system.

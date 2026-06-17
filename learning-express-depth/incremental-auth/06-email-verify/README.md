# 06 — Email Verify (Auth)

After signup, the email is unverified. Send a verification link. The user must click it to verify.

**What's new:**
- `email_verified` flag on users (default 0)
- Verification token in DB, expires in 24h
- `/auth/verify-email?token=X` — click the link
- `/auth/resend-verification` — get a new link
- `/auth/verification-status` — check if verified

**Why verify?** Without it, anyone can sign up with your email. Then you get password reset emails you didn't ask for. Or worse, an attacker signs up with someone else's email and uses the account for abuse.

**Why does it matter for the user?** Some features only work for verified emails (sending, receiving, recovery).

## Run
```bash
npm install && node server.js
```

```bash
# Signup (returns a verify link)
RESP=$(curl -X POST http://localhost:3000/auth/signup -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyPassword123"}')
VERIFY_URL=$(echo $RESP | grep -o '"dev_verify_url":"[^"]*' | cut -d'"' -f4)

# Check status (not verified)
curl 'http://localhost:3000/auth/verification-status?email=alice@example.com'
# { verified: false }

# Click the link
curl "http://localhost:3000$VERIFY_URL"
# { verified: true }

# Check again
curl 'http://localhost:3000/auth/verification-status?email=alice@example.com'
# { verified: true }
```

## What this stage teaches
- Email verification flow
- Tokens with longer TTL (24h vs 1h for password reset)
- Resend pattern
- Verification status check

## Next
**07-2fa** — two-factor auth. TOTP codes from an authenticator app.

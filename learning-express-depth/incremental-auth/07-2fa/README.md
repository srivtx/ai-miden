# 07 — 2FA / TOTP (Auth)

Two-factor auth with TOTP (Time-based One-Time Password). Set up, get a secret, verify codes on login.

**What's new:**
- `totp_secret` and `totp_enabled` on users
- `/2fa/setup` — generate a secret, return otpauth:// URL
- `/2fa/enable` — verify user can produce a valid code, then enable
- `/2fa/disable` — require a code to disable (prevent stolen accounts)
- `/2fa/current-code` — for testing, get the current TOTP code

**Why TOTP?** A second factor. Even if your password is stolen, the attacker needs the 6-digit code from your phone. The code changes every 30 seconds.

**The flow:**
1. User enables 2FA in settings
2. Server generates a random secret, stores it
3. User scans a QR code (the otpauth:// URL) with Google Authenticator
4. Google Authenticator now generates a new 6-digit code every 30 seconds
5. User enters the code to confirm
6. Server enables 2FA

**The algorithm:** HMAC-SHA1 of (secret, time/30s) → truncate to 6 digits. The secret is shared between the server and the app. They both know the time. They both produce the same code.

## Run
```bash
npm install && node server.js
```

```bash
# Setup
RESP=$(curl -X POST http://localhost:3000/2fa/setup -H "Content-Type: application/json" -d '{"user_id": "u_xxx"}')
SECRET=$(echo $RESP | grep -o '"secret":"[^"]*' | cut -d'"' -f4)

# Get the current code
curl "http://localhost:3000/2fa/current-code?secret=$SECRET"
# { code: "123456", ms_until_next: 25000 }

# Enable with that code
curl -X POST http://localhost:3000/2fa/enable -H "Content-Type: application/json" \
  -d "{\"user_id\": \"u_xxx\", \"code\": \"$CODE\"}"

# Disable (requires a code)
curl -X POST http://localhost:3000/2fa/disable -H "Content-Type: application/json" \
  -d "{\"user_id\": \"u_xxx\", \"code\": \"$CODE\"}"
```

## What this stage teaches
- TOTP algorithm (RFC 6238)
- Base32 encoding (for the secret)
- Clock skew tolerance (±1 window)
- Setup-then-verify flow
- otpauth:// URLs for QR codes

## Next
**08-oauth** — login with Google, GitHub, etc. Third-party auth.

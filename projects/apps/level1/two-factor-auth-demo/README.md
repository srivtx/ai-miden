# 2FA Demo — TOTP (Time-based One-Time Password)

TOTP is the standard for 2FA: Google Authenticator, Authy, 1Password all use it. The server shares a secret with the user's authenticator app. The app generates a 6-digit code every 30 seconds based on (secret, time). The server verifies the user knows the code.

## Endpoints
```
POST /2fa/setup              { userId }            -> { secret, otpauth_url }
POST /2fa/enable             { userId, secret, code }   -> { enabled }
POST /login                  { email, password, code? }  -> { user }
GET  /2fa/current-code?secret=...                    -> { code, msLeft }
```

## Try
```bash
# 1. Setup — get a secret
SECRET=$(curl -X POST http://localhost:3000/2fa/setup \
  -H "Content-Type: application/json" -d '{"userId": "u_alice"}' | jq -r .secret)
# Scan the otpauth_url with Google Authenticator, or just use the secret directly

# 2. Get current code
curl "http://localhost:3000/2fa/current-code?secret=$SECRET"
# { code: "123456", msLeft: 25000 }

# 3. Enable 2FA with the code
curl -X POST http://localhost:3000/2fa/enable \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"u_alice\", \"secret\": \"$SECRET\", \"code\": \"123456\"}"

# 4. Login requires the code
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"alice@example.com\", \"password\": \"password-123\", \"code\": \"123456\"}"
```

## What this teaches
1. **TOTP (RFC 6238)**: HMAC-SHA1 of (secret, time/30s counter), truncated to 6 digits
2. **Base32 encoding**: the secret is base32 (not hex) for authenticator app compatibility
3. **Clock skew tolerance**: accept codes from current ± 1 window
4. **Replay prevention**: store used codes, reject duplicates
5. **Setup flow**: generate secret → user verifies → enable
6. **The code is computed locally**: no SMS, no email — the app does it offline

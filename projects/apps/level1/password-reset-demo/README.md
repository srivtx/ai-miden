# Password Reset Demo — Forgot password, email link, verify, set new password

The standard 3-step flow:
1. User clicks "forgot password," enters email
2. Server generates a token, emails a link with the token
3. User clicks link, enters new password
4. Server verifies the token, hashes the new password, invalidates the token

## Endpoints
```
POST /auth/forgot-password        { email }              -> { message, dev_only: { resetLink } }
GET  /auth/reset-password?token=  -> { valid, userId }    # verify token
POST /auth/reset-password         { token, newPassword } -> { message }
POST /auth/login                  { email, password }    -> { user }
```

## Try
```bash
# 1. Request reset
RESP=$(curl -X POST http://localhost:3000/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com"}')
TOKEN=$(echo $RESP | jq -r '.dev_only.token')

# 2. Verify token
curl "http://localhost:3000/auth/reset-password?token=$TOKEN"

# 3. Set new password
curl -X POST http://localhost:3000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$TOKEN\", \"newPassword\": \"my-new-password-123\"}"

# 4. Login with new password
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "my-new-password-123"}'
```

## What this teaches
1. **Email enumeration prevention**: always return same message whether email exists or not
2. **Cryptographically random tokens**: 32 bytes of randomness
3. **TTL**: tokens expire (1 hour here)
4. **Single-use**: mark token as used after reset
5. **Invalidate other tokens**: when one is used, invalidate all for that user
6. **Strong password validation**: minimum length, etc.
7. **Constant-time comparison**: timing-safe hash comparison

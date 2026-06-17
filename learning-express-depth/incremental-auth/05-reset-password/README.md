# 05 — Reset Password (Auth)

Forgot password. Request a reset, get a token, set a new password.

**What's new:**
- `/auth/forgot-password` — request a reset, returns a token
- `/auth/reset-password?token=X` — verify the token (user clicks the link)
- `/auth/reset-password` (POST) — set new password with the token
- Tokens expire after 1 hour
- Tokens are single-use (marked `used` after consumption)
- Other reset tokens for the same user are invalidated
- Always return same response (prevents email enumeration)

**The flow:**
1. User clicks "forgot password," enters email
2. We generate a token, store it, send via email
3. User clicks the link, the page calls GET to verify the token
4. User enters new password, POST to set it
5. We update the password hash, mark the token as used
6. Other reset tokens for that user are invalidated (defense in depth)

**Why single-use?** If someone gets the link, they use it once. The user (if they're real) has already used it. The attacker is locked out.

**Why invalidate other tokens?** If the user requested 5 resets, only the most recent should work.

## Run
```bash
npm install && node server.js
```

```bash
# Request reset
RESP=$(curl -X POST http://localhost:3000/auth/forgot-password -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com"}')
TOKEN=$(echo $RESP | grep -o '"dev_token":"[^"]*' | cut -d'"' -f4)

# Set new password
curl -X POST http://localhost:3000/auth/reset-password -H "Content-Type: application/json" \
  -d "{\"token\": \"$TOKEN\", \"new_password\": \"NewPassword123\"}"

# Try to use the token again
curl -X POST http://localhost:3000/auth/reset-password -H "Content-Type: application/json" \
  -d "{\"token\": \"$TOKEN\", \"new_password\": \"AnotherOne\"}"
# 400 invalid_token
```

## What this stage teaches
- Token-based password reset
- Email enumeration prevention
- Single-use tokens
- Token invalidation
- TTL on sensitive operations

## Next
**06-email-verify** — verify the email on signup. Send a confirmation link.

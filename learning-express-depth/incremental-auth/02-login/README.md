# 02 — Login (Auth)

Verify password. Same error for invalid email and wrong password. Account lockout.

**What's new:**
- Login endpoint with `verifyPassword`
- Constant-time response (always run the hash, even for missing users)
- Failed attempt tracking
- Account lockout: 5 failed attempts = 15-minute lock
- Same error message for invalid email and wrong password (prevents email enumeration)

**Why same error for both?** If you say "email not found" vs "wrong password," an attacker can enumerate which emails are registered. "Invalid credentials" reveals nothing.

**Why constant time?** If verify is faster for missing users (no hash to check), an attacker can measure response time. By always running the hash, the timing is the same.

**Why account lockout?** Brute force protection. 5 wrong attempts = 15 minutes wait. The user can still try after the lockout expires.

## Run
```bash
npm install && node server.js
```

```bash
# Signup
curl -X POST http://localhost:3000/auth/signup -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyPassword123"}'

# Login success
curl -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyPassword123"}'
# 200

# Wrong password — same error as wrong email
curl -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "wrong"}'
# 401 invalid_credentials

# 5 wrong attempts — locked
for i in {1..5}; do
  curl -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" \
    -d '{"email": "alice@example.com", "password": "wrong"}'
done
# Last one: 423 account_locked
```

## What this stage teaches
- Constant-time comparison
- Account lockout pattern
- Email enumeration prevention
- Failed attempt tracking

## Next
**03-jwt** — return a signed token on login. The token proves identity on future requests.

# 01 — Signup (Auth)

Create a user. Email + password (hashed). Validation.

**What's here:**
- Email validation (regex)
- Password validation: 8+ chars, upper, lower, digit, max 128
- Email uniqueness check
- PBKDF2 password hashing (100k iterations, SHA-512)
- Random salt per user

**Why strong password rules?** A short, simple password is brute-forceable. The rules (upper, lower, digit) force entropy. 8 chars minimum, 128 max (so a user can't lock you out with a 10MB password).

**Why PBKDF2?** Built into Node. 100k iterations = ~100ms per hash = expensive for attackers, fine for users.

## Run
```bash
npm install && node server.js
```

```bash
# Valid
curl -X POST http://localhost:3000/auth/signup -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyPassword123"}'
# 201

# Invalid email
curl -X POST http://localhost:3000/auth/signup -H "Content-Type: application/json" \
  -d '{"email": "not-an-email", "password": "MyPassword123"}'
# 422 invalid_email

# Weak password
curl -X POST http://localhost:3000/auth/signup -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "weak"}'
# 422 weak_password, errors: ["password must be at least 8 characters", ...]

# Duplicate
curl -X POST http://localhost:3000/auth/signup -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyPassword123"}'
# 409 email_taken
```

## What this stage teaches
- Email regex validation
- Password complexity rules
- Constant-time-safe hashing
- Uniqueness check

## Next
**02-login** — verify password, return user info. Same error for invalid email and password.

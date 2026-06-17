# Validation Demo — Schema-based validation without external libraries

A 50-line validator that handles: required, type, length, range, pattern, enum, custom.

## Endpoints
```
POST /users       # email, password, age, role
POST /products    # name, price_cents, category, description
POST /validate-test  # arbitrary schema for testing
```

## Try
```bash
# Valid user
curl -X POST http://localhost:3000/users -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "longpassword", "age": 25, "role": "user"}'
# 201

# Missing email
curl -X POST http://localhost:3000/users -H "Content-Type: application/json" \
  -d '{"password": "longpassword"}'
# 422 { error: "validation_failed", errors: [{ field: "email", code: "required" }] }

# Bad email format
curl -X POST http://localhost:3000/users -H "Content-Type: application/json" \
  -d '{"email": "not-an-email", "password": "longpassword"}'
# 422 { field: "email", code: "pattern_mismatch" }

# Wrong role
curl -X POST http://localhost:3000/users -H "Content-Type: application/json" \
  -d '{"email": "a@b.com", "password": "longpassword", "role": "wizard"}'
# 422 { field: "role", code: "not_in_enum", allowed: ["user", "admin", "moderator"] }
```

## What this teaches
1. **Schema as a contract**: declare the shape of valid input once
2. **Multiple error types**: required, type, length, range, pattern, enum, custom
3. **All errors at once**: validator collects all errors, not just the first
4. **422 Unprocessable Entity**: for validation failures (vs 400 for malformed)
5. **Custom validators**: function that returns null if valid, error message if not

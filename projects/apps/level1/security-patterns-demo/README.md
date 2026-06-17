# Security Patterns Demo — Parameterized queries, XSS, path traversal, password hashing

Five common attack vectors, five defenses. All in one Express app.

## Endpoints
```
POST /register              # PBKDF2 password hashing (100k iterations, SHA-512)
POST /login                 # parameterized query + timing-safe comparison
GET  /users/:id             # ID validation + parameterized query
GET  /search?q=...          # XSS escape in HTML output
GET  /file/:name            # path traversal prevention
```

## Try
```bash
# Register
curl -X POST http://localhost:3000/register \
  -H "Content-Type: application/json" \
  -d '{"email": "bob@example.com", "password": "mypassword123"}'
# 201 if valid, 422 if password < 8 chars

# Login (alice@example.com / correct horse battery staple)
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "correct horse battery staple"}'
# 200 if correct, 401 if wrong

# SQL injection attempt (FAILS, parameterized)
curl http://localhost:3000/users/1%20OR%201%3D1
# 400 invalid_id (not 200 with all users)

# XSS attempt (rendered as text, not executed)
curl 'http://localhost:3000/search?q=%3Cscript%3Ealert(1)%3C/script%3E'
# HTML output: <h1>Search results for: &lt;script&gt;alert(1)&lt;/script&gt;</h1>

# Path traversal attempt (FAILS)
curl http://localhost:3000/file/..%2F..%2Fetc%2Fpasswd
# 400: "Path traversal detected"

# Security headers in every response
curl -I http://localhost:3000/anything
# X-Content-Type-Options, X-Frame-Options, CSP, HSTS, X-XSS-Protection
```

## What this teaches
1. **PBKDF2 password hashing**: 100k iterations, SHA-512, salt per user, timing-safe compare
2. **Parameterized queries**: every DB call uses `?` placeholder, NEVER string interpolation
3. **XSS escape**: HTML entities for `<`, `>`, `&`, `"`, `'`
4. **Path traversal**: `path.resolve()` + check it starts with the base directory
5. **Security headers**: 5 headers that block common attacks
6. **Input validation**: type checks, length checks, format checks

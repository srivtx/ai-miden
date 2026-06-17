# Error Handling Demo — Typed errors, global handler, request IDs

A complete error handling pattern. Every error has: status code, machine-readable code, human message, request ID.

## Endpoints
```
GET  /users/:id        # 400 invalid_id, 404 not found, 403 forbidden
POST /login            # 422 missing email/password, 422 weak password
GET  /admin            # 500 unhandled (simulated)
```

## Try
```bash
# 400 Bad Request
curl http://localhost:3000/users/abc
# {"error": {"code": "invalid_id", "message": "ID must be a number", "details": {"received": "abc"}, "request_id": "req_..."}}

# 404 Not Found
curl http://localhost:3000/users/0
# {"error": {"code": "user_not_found", "message": "User 0 does not exist", ...}}

# 422 Validation
curl -X POST http://localhost:3000/login -H "Content-Type: application/json" -d '{"email": "a@b.com"}'
# {"error": {"code": "missing_password", ...}}

# 500 Internal Error
curl http://localhost:3000/admin
# {"error": {"code": "internal_error", "message": "An unexpected error occurred", "request_id": "req_..."}}
# (Stack trace in server logs, NOT in response)
```

## What this teaches
1. **Typed errors** (`AppError`) with status code, code, message, details
2. **Request ID propagation**: every error has a request_id, in both response and header
3. **Global error handler**: catches all errors, formats response
4. **No stack traces in production**: server logs the stack, client gets generic message
5. **RFC 7807-style response shape**: machine-readable, linkable docs

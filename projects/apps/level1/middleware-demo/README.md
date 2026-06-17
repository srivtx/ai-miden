# Middleware Demo — Custom middleware: timing, counter, blocklist, validation, transform

Five middleware functions showing the power of the middleware pattern. Each is a function that takes `(req, res, next)` and either responds or calls `next()`.

## Endpoints
```
GET  /health
POST /users              # uses requireFields('email', 'username') and normalizeEmail
GET  /admin/stats        # request counts by path
```

## What this teaches
1. **Order matters**: timing (outermost) → blocklist → counter → route-specific validation
2. **res.on('finish')** runs after the response is sent (for timing)
3. **req.body transformation**: normalizeEmail mutates req.body before the handler sees it
4. **Modular middleware**: `requireFields('email', 'username')` is a factory that returns middleware
5. **res.set** to add custom headers (`X-Response-Time`)

## Try
```bash
curl http://localhost:3000/health
# Header: X-Response-Time: 0.41ms

curl -X POST http://localhost:3000/users -H "Content-Type: application/json" -d '{"email": "  ALICE@X.COM  ", "username": "  Alice  "}'
# Normalized: email = "alice@x.com", username = "alice"

curl -X POST http://localhost:3000/users -H "Content-Type: application/json" -d '{}'
# 422 missing_fields: ["email", "username"]

curl http://localhost:3000/admin/stats
# requestCount and countsByPath
```

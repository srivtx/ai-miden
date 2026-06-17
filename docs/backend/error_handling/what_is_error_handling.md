## Why it exists (THE PROBLEM)

Something goes wrong. The user sees... what? Without a plan, you get: "Internal Server Error" with no info, or the entire stack trace dumped to the browser, or "Oops! Something went wrong" with no error code, or a half-rendered page mixed with a JSON error.

Three problems:
1. **The user can't act on the error.** "Something went wrong" tells them nothing. They retry, get the same error, give up.
2. **You can't debug.** If the error is just a 500 with no info, you have no idea what happened.
3. **The error leaks internals.** Stack trace with file paths, database names, internal IPs. Attackers LOVE this. It tells them what tech you use, what versions, what paths.

A good error response has: HTTP status code, machine-readable error code, human-readable message, request ID for support, sometimes a URL to docs.

## Definition (very simple)

**HTTP status code** = a number that classifies the error. `4xx` = client error (the request was bad). `5xx` = server error (the server broke). Common:
- 400 Bad Request — malformed JSON, missing fields
- 401 Unauthorized — no auth
- 403 Forbidden — auth but no permission
- 404 Not Found — resource doesn't exist
- 409 Conflict — duplicate, version conflict
- 422 Unprocessable Entity — well-formed but semantically wrong
- 429 Too Many Requests — rate limited
- 500 Internal Server Error — unhandled exception
- 502 Bad Gateway — upstream service failed
- 503 Service Unavailable — server overloaded, try again

**Error code** = a string identifier. `"invalid_card"`, `"user_not_found"`, `"rate_limit_exceeded"`. The client code can match on this to take action.

**Error message** = human-readable text. "Your card was declined." "The user with ID 42 does not exist." Localized in the user's language.

**Request ID / Trace ID** = a unique string for this specific request. The user reports "I got an error, my request ID is `req_abc123`." You search your logs. Find the exact failure. Fix it.

**Error class hierarchy** = your code has typed errors. `ValidationError`, `NotFoundError`, `AuthError`, `RateLimitError`. Each has a status code, an error code, a message. The error handler converts to HTTP responses.

## Real-life analogy

**Bad error handling = a store that just says "we can't help you."** No reason. No escalation. No idea who to ask. You leave.

**Good error handling = a store that says "I'm sorry, that item is out of stock. We expect more next Tuesday. Would you like me to notify you, or would you like a similar item?"** Clear. Actionable. Helpful.

**Request ID = the receipt.** "I want a refund for order 12345." The store can look it up. Without the receipt, the store has to ask "when? what did you buy? how much?" Endless questions.

## Tiny numeric example

Bad error (no info):
```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/html

<html><body><h1>Internal Server Error</h1></body></html>
```

Good error (helpful, secure):
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
X-Request-Id: req_abc123def456

{
  "error": {
    "code": "invalid_card",
    "message": "Your card was declined. Please use a different card.",
    "details": {
      "decline_code": "insufficient_funds",
      "card_brand": "visa"
    },
    "docs_url": "https://api.example.com/docs/errors#invalid_card",
    "request_id": "req_abc123def456"
  }
}
```

Now the client can: display "Your card was declined" to the user, check the decline code, link to docs, give the user the request ID for support.

## Common confusion (5+ bullet points)

1. **"I'll return 200 with the error in the body."** NO. The HTTP status code IS the error indicator. Scrapers, monitoring, libraries all check it first. 200 + error body = "it worked" to infrastructure, but the client has to parse the body. Use 4xx/5xx.

2. **"I'll expose the stack trace in production."** No. Attackers use it. Reveals your tech, your file structure, your database tables (sometimes), your internal IPs. Show: a generic message, a request ID. Log the stack trace server-side.

3. **"500 is fine for all errors."** No. 500 means "the server broke, try again." If the user sends invalid input, that's 400, not 500. 500 for client errors is a code smell — you didn't handle the case.

4. **"I'll just use try/catch in every handler."** Tedious, easy to miss. Use a global error middleware. Express: `app.use((err, req, res, next) => { ... })`. The middleware reads `err.statusCode` or `err.code` and formats the response.

5. **"Errors should be in English only."** Localization matters. Some APIs return errors in the user's `Accept-Language`. `"Accept-Language: es"` → error in Spanish. The error CODE is universal (`invalid_card`), the MESSAGE is localized.

6. **"I'll log errors to console."** `console.log` is OK in dev, useless in prod. Use a logging library (Winston, Pino, Bunyan). Structured logs: `logger.error({ err, requestId, userId, path }, "validation failed")`. Searchable. Alertable.

7. **"Validation errors should be 400."** Yes if it's "the JSON is malformed." If it's "the email is invalid" (well-formed but semantically wrong), it's 422 Unprocessable Entity. The line is fuzzy; pick a convention and stick to it.

## Key properties

| Status | Meaning | When to use |
|---|---|---|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful but no body to return |
| 400 | Bad Request | Malformed JSON, missing required fields |
| 401 | Unauthorized | No auth or invalid auth |
| 403 | Forbidden | Auth but no permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate, version mismatch |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limited |
| 500 | Server Error | Unhandled exception |
| 502/503/504 | Upstream/downstream | Service is up but something it depends on is down |

## Error response shape (RFC 7807 Problem Details)

```json
{
  "type": "https://example.com/probs/invalid-card",
  "title": "Invalid card",
  "status": 422,
  "detail": "Your card was declined.",
  "instance": "/charges/ch_42",
  "request_id": "req_abc123"
}
```

This is the IETF standard. Some companies follow it (GitHub, Stripe close). Some have their own shape. Pick one and be consistent.

## Global error handler (Express pattern)

```js
class AppError extends Error {
  constructor(statusCode, code, message, details) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
  }
}

// Routes throw these
app.post('/users', (req, res) => {
  if (!req.body.email) throw new AppError(400, 'missing_email', 'Email is required');
});

// Global handler
app.use((err, req, res, next) => {
  const requestId = req.headers['x-request-id'] || generateRequestId();
  if (err instanceof AppError) {
    logger.warn({ err, requestId, path: req.path }, 'client error');
    return res.status(err.statusCode).json({
      error: { code: err.code, message: err.message, details: err.details, request_id: requestId }
    });
  }
  // Unknown error: log fully, return generic
  logger.error({ err, requestId, path: req.path }, 'unhandled error');
  res.status(500).json({ error: { code: 'internal_error', message: 'Something went wrong', request_id: requestId } });
});
```

## Connection to our projects

For our 73 apps, add:
1. An `AppError` class in `lib/errors.js`
2. A global error handler in `app.js`
3. Use proper status codes (400, 401, 403, 404, 409, 422, 429, 500)
4. Include `request_id` in every error response
5. Never expose stack traces in production responses

The `error-handling-demo/` project shows the full pattern. Copy that to any project.

For CortexCode and logogen: same. The API can fail (model OOM, timeout, rate limit). Return a proper 500 with a request_id. The user can report it. You can look it up in your observability dashboard.

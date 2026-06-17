# 56 — CSRF Protection

**New concept:** cross-site request forgery (CSRF) protection.

Imagine you're logged in to your bank. You visit a malicious site. The site has a hidden form that submits a transfer request to your bank. Your browser sends your bank's cookie with the request. The bank thinks it's you. Money is transferred.

CSRF protection stops this. The malicious site can't make a request that has the right CSRF token.

## Run it

```bash
npm install
node server.js
```

```bash
# Get a CSRF token (and cookie)
RESP=$(curl -c cookies.txt http://localhost:3000/csrf-token)
TOKEN=$(echo $RESP | grep -o '"csrfToken":"[^"]*' | cut -d'"' -f4)

# Make a request WITH the token
curl -b cookies.txt \
  -H "X-CSRF-Token: $TOKEN" \
  -X POST http://localhost:3000/transfer \
  -H "Content-Type: application/json" \
  -d '{"to": "alice", "amount": 100}'
# { "message": "Transferred $100 to alice" }

# Try WITHOUT the token
curl -b cookies.txt \
  -X POST http://localhost:3000/transfer \
  -H "Content-Type: application/json" \
  -d '{"to": "attacker", "amount": 1000}'
# 403 { "error": "Invalid CSRF token" }
```

## How to think about it

CSRF protection is like a secret handshake. The server gives the user a token. The user has to send the token with every state-changing request. A malicious site doesn't know the token, so its requests get rejected.

## How to build it (line by line)

```js
const token = generateCsrfToken();
res.cookie('csrf_token', token, { sameSite: 'strict' });
res.json({ csrfToken: token });
```

**Lines 18-22.** Set a CSRF cookie and return the token. The client gets it.

**`sameSite: 'strict'`** — the cookie is only sent to your site, not to malicious sites.

```js
function verifyCsrf(req, res, next) {
  if (req.method === 'GET') return next();
  const provided = req.headers['x-csrf-token'] || req.body._csrf;
  if (!provided || provided !== req.cookies.csrf_token) {
    return res.status(403).json({ error: 'Invalid CSRF token' });
  }
  next();
}
```

**Lines 25-33.** Middleware that checks the CSRF token on every state-changing request.

**`GET` is safe** — reading doesn't change state, no CSRF risk.

**The token must match the cookie.** If they don't match, reject.

## What we learned

1. CSRF = cross-site request forgery
2. Without protection, malicious sites can submit forms as the user
3. CSRF token = secret handshake
4. `sameSite: 'strict'` cookies help
5. Modern frameworks (Next.js, Rails, Django) have CSRF protection built in

## What's next

In **57-cors** we configure CORS so browsers can call our API from other domains.

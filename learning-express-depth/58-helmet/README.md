# 58 — Helmet

**New concept:** security headers in one line.

There are many HTTP headers that protect against common web attacks: XSS, clickjacking, MIME sniffing, etc. Setting them all by hand is tedious. Helmet does it for you.

## Run it

```bash
npm install
node server.js
```

```bash
curl -i http://localhost:3000/
# HTTP/1.1 200 OK
# Content-Security-Policy: default-src 'self'; ...
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-DNS-Prefetch-Control: off
# X-Download-Options: noopen
# X-Permitted-Cross-Domain-Policies: none
# Referrer-Policy: no-referrer
# Cross-Origin-Opener-Policy: same-origin
# Cross-Origin-Resource-Policy: same-origin
# Origin-Agent-Cluster: ?1
# ...
```

## How to think about it

Helmet is a checklist. Each header prevents a specific attack. Setting them all is tedious. Helmet does it in one line.

## How to build it (line by line)

```js
const helmet = require('helmet');
app.use(helmet());
```

**Lines 4-7.** That's it. One line. Many headers.

**`app.use(helmet())`** — applies Helmet's middleware to every request.

## What we learned

1. Helmet sets 15+ security headers in one line
2. Each header prevents a specific attack
3. `Content-Security-Policy` — controls what JS/CSS can load
4. `X-Frame-Options: DENY` — prevents clickjacking
5. `Strict-Transport-Security` — forces HTTPS
6. Always use Helmet in production

## What's next

In **59-i18n** we make our API support multiple languages.

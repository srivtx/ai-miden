## Why it exists (THE PROBLEM)

A junior dev writes `app.get('/users/:id', (req, res) => db.query('SELECT * FROM users WHERE id = ' + req.params.id))`. The user passes `?id=1 OR 1=1` as the id. The query becomes `SELECT * FROM users WHERE id = 1 OR 1=1`. Every user is returned. Including passwords (if they're in the table). The attacker has all your users.

**SQL injection** is the #1 web vulnerability. It's been known for 20 years. It's still the #1 breach. Because someone forgot to use parameterized queries.

The second problem: a user uploads a profile picture. The server saves it as `public/uploads/<filename>`. The filename is the user's input. The user names the file `../../etc/passwd`. The server writes to `/etc/passwd`. Now the server is broken.

**Path traversal** lets attackers read or write files outside the intended directory.

The third problem: a user signs up with email `a@b.com`. The server sends a welcome email. The user reports the welcome email contains the email of another user. How? The server had a query bug: `SELECT email FROM users WHERE name = '${name}'` — name came from URL, attacker injected SQL.

**Don't trust input.** EVER. Every input is malicious until proven otherwise.

## Definition (very simple)

**SQL injection** = putting SQL code in user input that gets executed. The fix: parameterized queries (also called prepared statements). The DB driver sends the SQL and the data separately. The data can't be SQL.

**XSS (Cross-Site Scripting)** = putting JavaScript in user input that gets executed in another user's browser. The fix: escape user input when rendering HTML. Or: render text, not HTML.

**CSRF (Cross-Site Request Forgery)** = a user is logged in to your site, visits a malicious site, the malicious site makes a request to your site. The browser sends the auth cookie. The server thinks it's a real request. The fix: CSRF tokens, SameSite cookies.

**Path traversal** = putting `../` in a file path to read/write outside the intended directory. The fix: validate the resolved path is inside the intended directory.

**Authentication** = proving who you are. "I am Alice." Usually with a password, a token, a biometric.

**Authorization** = proving you're allowed to do this. "I am Alice, and Alice can read this resource." Different from auth.

**Secrets management** = storing API keys, DB passwords, etc. in a place that doesn't leak. Env vars, secret managers (AWS Secrets Manager, HashiCorp Vault). NOT in code, NOT in git.

**OWASP Top 10** = the 10 most common web security risks. Updated every few years. The current top: broken access control, cryptographic failures, injection, insecure design, security misconfiguration, vulnerable components, auth failures, software/data integrity failures, logging failures, SSRF.

## Real-life analogy

**Bad security = a bank vault with the door unlocked.** "We have a vault!" Yes, but the door is open. The vault doesn't help.

**Good security = the vault, the door, the lock, the guard, the alarm, the camera.** Layered. Each layer catches what the others miss.

**Auth = showing your ID at the door.** "I'm Alice." The guard checks the ID. If the ID matches Alice's photo, you enter.

**Authz = having the right key for the right room.** Alice is in the building, but the vault room needs a different key. She has the building key, not the vault key. So she can't enter the vault.

**Parameterized queries = a coffee order on a card.** You write "large latte, oat milk" on a card. The barista reads the card, makes the drink. You can't change the order by writing "DROP TABLE users" on the card. The barista reads the card as a coffee order, not as instructions.

**XSS = a note on a billboard that says "Read this aloud."** The billboard says "Hello, friend. <script>steal_cookies()</script>." Anyone who reads it aloud has their cookies stolen. The fix: don't write `<script>` in notes; write "Read this aloud" as plain text.

## Tiny numeric example

**SQL injection vulnerable:**
```js
// BAD
app.get('/users/:id', (req, res) => {
  db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);
  // If id = "1 OR 1=1", returns all users
  // If id = "1; DROP TABLE users;--", deletes the table
});
```

**Parameterized (safe):**
```js
// GOOD
app.get('/users/:id', (req, res) => {
  db.query('SELECT * FROM users WHERE id = ?', [req.params.id]);
  // id is treated as data, not SQL
  // Safe
});
```

**XSS vulnerable:**
```js
// BAD
app.get('/search', (req, res) => {
  res.send(`<h1>Results for ${req.query.q}</h1>`);
  // If q = "<script>alert('xss')</script>", executes the script
});
```

**XSS safe:**
```js
// GOOD
app.get('/search', (req, res) => {
  const escaped = escapeHtml(req.query.q);
  res.send(`<h1>Results for ${escaped}</h1>`);
});
// Or use a templating engine that escapes by default
```

**Path traversal vulnerable:**
```js
// BAD
app.get('/file/:name', (req, res) => {
  res.sendFile(`/uploads/${req.params.name}`);
  // If name = "../../etc/passwd", sends /etc/passwd
});
```

**Path traversal safe:**
```js
// GOOD
const path = require('path');
app.get('/file/:name', (req, res) => {
  const safe = path.resolve('/uploads', req.params.name);
  if (!safe.startsWith('/uploads/')) return res.status(400).send('Invalid path');
  res.sendFile(safe);
});
```

## Common confusion (5+ bullet points)

1. **"I'm using an ORM, so I'm safe from SQL injection."** Mostly, yes. But raw queries (`db.raw()`, `$$ ... $$`) bypass the ORM. Any string interpolation in a query is a potential injection. The ORM helps; it doesn't absolve you.

2. **"I escape output, so I'm safe from XSS."** You escape the OUTPUT, not the input. Different escaping for HTML, JS, URL, attribute. Use a templating engine (Handlebars, Mustache, JSX with default escaping) that does it for you.

3. **"I have HTTPS, so I'm secure."** HTTPS protects data in transit. It does nothing for SQL injection, XSS, CSRF, broken auth, etc. You still need to handle those.

4. **"My password is hashed, so it's safe."** With what algorithm? MD5 = unsafe. SHA-1 = unsafe. SHA-256 = maybe (fast hash, brute-forceable). bcrypt, scrypt, argon2 = safe (slow, with salt). Use bcrypt or argon2.

5. **"I'll roll my own auth."** Don't. Use a library (Passport, Auth.js, NextAuth, Clerk, Auth0) or a service. Auth has so many edge cases (password reset, session expiry, refresh tokens, MFA, account lockout) that you will get it wrong. Use a library.

6. **"Secrets in env vars are safe."** Yes, until someone dumps the env (`printenv`, `env`, `/proc/1/environ`). In a container, env vars are visible to anyone with shell access. In a CI log, env vars in the script are visible. Use a secret manager (AWS Secrets Manager, Vault). For dev, `.env` files (in `.gitignore`).

7. **"I'll add security later."** No. Security is not a feature. It's a foundation. Adding it later means re-architecting. Bake it in from the start: parameterized queries, input validation, output escaping, auth on every endpoint, secrets in env vars.

8. **"I checked OWASP once. I'm done."** OWASP updates every few years. New vulnerabilities appear (e.g., prototype pollution, supply chain attacks). Stay current.

## Key properties

| Attack | Vector | Defense |
|---|---|---|
| SQL injection | User input in SQL | Parameterized queries |
| XSS | User input in HTML | Escape output, CSP headers |
| CSRF | Cookie sent cross-origin | CSRF tokens, SameSite cookies |
| Path traversal | `../` in file paths | Validate resolved path |
| Auth bypass | Missing auth check | Middleware on every protected route |
| Brute force | Many login attempts | Rate limit, account lockout |
| Data leak | Verbose errors, stack traces | Generic errors, log details server-side |
| Insecure direct object reference (IDOR) | Guessable IDs (e.g., /users/1, /users/2) | Authz check, random IDs |

## Defense in depth (layers)

1. **Network**: HTTPS, rate limiting, WAF (Web Application Firewall)
2. **Auth**: strong password hashing (bcrypt/argon2), MFA, session expiry
3. **Authz**: role-based, check on every endpoint
4. **Input validation**: validate types, lengths, formats
5. **Output encoding**: escape HTML, JS, URLs
6. **Database**: parameterized queries, principle of least privilege
7. **Logging**: log auth events, log access, don't log secrets
8. **Monitoring**: alert on suspicious patterns (1000 logins in 1 min)
9. **Updates**: keep deps updated, watch for CVEs

## Connection to our projects

For our 73 apps, before going to production:
1. Use parameterized queries (always, no exceptions)
2. Escape output in HTML (use a templating engine)
3. Hash passwords with bcrypt
4. Validate input (length, format, type)
5. Use HTTPS (Caddy, nginx, Let's Encrypt)
6. Add rate limiting (token bucket)
7. Set security headers (`X-Content-Type-Options`, `X-Frame-Options`, `CSP`)
8. Store secrets in env vars (`.env` in `.gitignore`)
9. Add CSRF protection for cookie-based auth

The `security-basics/` and `auth-demo/` projects in apps/level1 show patterns. The `security_patterns/` curriculum doc covers more.

For CortexCode and logogen: if the API is public, add rate limiting, input validation, and don't expose internal errors. The auth-basics project shows the pattern.

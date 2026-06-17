# 20 — URL Shortener

The last project. You give it a long URL, it gives you a short code. When someone visits the short code, they get redirected to the long URL.

## Run it

```bash
npm install
node server.js
```

```bash
# Shorten a URL
curl -X POST http://localhost:3000/urls \
  -H "Content-Type: application/json" \
  -d '{"longUrl": "https://www.example.com/very/long/path/to/something"}'
# { "code": "a3b4c5", "longUrl": "...", "shortUrl": "http://localhost:3000/a3b4c5" }

# Visit the short URL — get redirected
curl -i http://localhost:3000/a3b4c5
# HTTP/1.1 302 Found
# Location: https://www.example.com/very/long/path/to/something

# List all short URLs
curl http://localhost:3000/urls
# Each one has a "clicks" count that goes up each time it's visited
```

## How to think about it

This is the first app where we use **redirect**. The user visits a short URL, and we tell the browser "go to this other URL." This is how bit.ly, tinyurl, and similar services work.

The new thing: a "lookup by code" pattern. The code is in the URL, not the id. We generate a random short code (like `a3b4c5`) instead of a number.

## How to build it (line by line)

```js
function makeCode() {
  return crypto.randomBytes(4).toString('hex').slice(0, 6);
}
```

**Lines 11-13.** Make a random 6-character code.

**`crypto.randomBytes(4)`** — 4 random bytes (32 bits).
**`.toString('hex')`** — convert to hex (so it's readable, like `"a3b4c5d6..."`).
**`.slice(0, 6)`** — take the first 6 characters.

With 6 hex chars, we have 16 million possible codes. Collisions are rare but possible, so we check for them.

```js
let code;
do {
  code = makeCode();
} while (urls.some(u => u.code === code));
```

**Lines 21-24.** Keep generating codes until we find one that's not used. `do...while` runs the body first, then checks the condition. So we generate at least one code, then check.

```js
app.get('/:code', (req, res) => {
  const entry = urls.find(u => u.code === req.params.code);
  if (!entry) return res.status(404).json({ error: 'Code not found' });
  entry.clicks += 1;
  res.redirect(entry.longUrl);
});
```

**Lines 39-44.** The redirect endpoint.

**`/:code`** — capture whatever the user types. This means `/urls` and `/anything-else` all hit this. But Express matches `/urls` first (it's registered earlier), so the redirect only happens for codes that aren't `/urls`.

**`res.redirect(longUrl)`** — send a 302 response with a `Location` header. The browser sees the 302 and goes to the long URL.

**`entry.clicks += 1`** — count this visit. Useful for analytics.

## What we learned

1. `res.redirect(url)` sends a 302 response
2. We can generate short random codes
3. Lookup by code is the same as lookup by id, just a different field
4. We can count clicks for analytics
5. We've now built 20 apps

## Where to go next

You've built 20 small apps. Each one taught a slightly different shape. The patterns you've seen:
- CRUD (every app)
- Filtering (products, contacts)
- Range queries (calendar)
- Uniqueness checks (bookmarks, contacts)
- Hashing (password vault)
- Aggregation (expenses)
- Voting (polls, quizzes)
- Nested data (recipes, chat)
- Date math (habits, calendar)
- Redirects (URL shortener)

Pick any of these apps and add to it:
- Add a database (so data survives restarts)
- Add user accounts (so each user has their own todos)
- Add tests (so you can change the code without breaking things)
- Add rate limiting (so people can't hammer the API)

Or, build a new app from scratch. You have the structure now.

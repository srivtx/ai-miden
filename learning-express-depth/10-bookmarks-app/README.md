# 10 — Bookmarks App

Same CRUD. New things:
- Bookmarks have a `url` (and `title`, `description`)
- We **reject duplicates** — same URL can't be saved twice

## Run it

```bash
npm install
node server.js
```

```bash
# Add a bookmark
curl -X POST http://localhost:3000/bookmarks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://nodejs.org", "title": "Node.js", "description": "JS runtime"}'

# Try to add the same URL again
curl -X POST http://localhost:3000/bookmarks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://nodejs.org", "title": "Node.js again"}'
# 409 { "error": "Bookmark with this URL already exists" }
```

## How to think about it

Most apps have at least one uniqueness rule: "no two of these can have the same X." For users it's email. For bookmarks it's URL. For products it's SKU. The pattern is the same: check if it exists, reject if it does, otherwise create.

## How to build it (line by line)

```js
if (bookmarks.some(b => b.url === url)) {
  return res.status(409).json({ error: 'Bookmark with this URL already exists' });
}
```

**Lines 13-15.** Check for duplicates before creating.

**`bookmarks.some(b => b.url === url)`** — does any bookmark in the list have this URL? `some` returns true if at least one item matches.

**`res.status(409)`** — 409 Conflict. The standard code for "this conflicts with something that already exists."

**Why return early?** If we don't, we'd create a duplicate and return 201.

## What we learned

1. Uniqueness checks prevent duplicates
2. `array.some(condition)` returns true if any item matches
3. 409 Conflict is the right code for "this already exists"
4. Always return early on validation failure
5. We've now seen validation in a real context

## What's next

In **11-weather-app** we build something with no storage. The "data" comes from a hardcoded list. We just look up the city and return the weather. This shows that not every app needs a database.

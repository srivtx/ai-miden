# 07 — Blog App

A blog post is like a note, but with an author. Same CRUD pattern, one new field.

## Run it

```bash
npm install
node server.js
```

```bash
# Create a post with an author
curl -X POST http://localhost:3000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello world", "body": "First post", "author": "Alice"}'
# { "id": 1, "title": "Hello world", "body": "First post", "author": "Alice", "createdAt": "..." }

# Create a post without an author (default to "Anonymous")
curl -X POST http://localhost:3000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Quick thought"}'
# { "id": 2, ..., "author": "Anonymous" }
```

## How to think about it

Notice how similar this is to the notes app. We just added one field (`author`) and gave it a default value. The whole structure — routes, status codes, error handling — is the same.

This is the most important insight: **most apps have the same shape**. Different data, same code.

## How to build it (line by line)

```js
const post = {
  id: posts.length + 1,
  title,
  body: body || '',
  author: author || 'Anonymous',
  createdAt: new Date().toISOString(),
};
```

**Lines 14-20.** Same as notes, plus one new field:

```js
author: author || 'Anonymous',
```

**Line 18.** If the client sent an author, use it. If not, use `'Anonymous'`.

**The `||` pattern again.** It means "or, if the left is falsy." Empty string, `null`, `undefined` are all falsy.

## What we learned

1. The CRUD pattern is the same for todos, notes, and posts
2. Adding a field is just adding a line to the object
3. `value || 'default'` gives a default when the value is missing
4. Most apps are 80% the same code, 20% different data

## What's next

In **08-products-app** we build a product catalog. Same CRUD pattern, but products have a `price` (a number, not a string) and a `category`. This is where we start seeing the data shapes get more interesting.

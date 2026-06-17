# 26 — Reading List

A list of books. Each book has a status: `to_read`, `reading`, or `done`. New thing: **PATCH** for partial updates.

## Run it

```bash
npm install
node server.js
```

```bash
# Add a book
curl -X POST http://localhost:3000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "The Pragmatic Programmer", "author": "Hunt & Thomas"}'

# Filter by status
curl 'http://localhost:3000/books?status=to_read'

# Update the status (PATCH — partial update)
curl -X PATCH http://localhost:3000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "reading"}'

# Mark as done and rate
curl -X PATCH http://localhost:3000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done", "rating": 5}'
```

## How to think about it

We saw POST (create) and DELETE. Now we see PATCH (update). PATCH is for partial updates: send only the fields you want to change. PUT is for full replacement (send the whole object).

## How to build it (line by line)

```js
app.patch('/books/:id', (req, res) => {
  const book = books.find(b => b.id === parseInt(req.params.id));
  if (!book) return res.status(404).json({ error: 'Book not found' });
  if (req.body.status) book.status = req.body.status;
  if (req.body.rating) book.rating = req.body.rating;
  res.json(book);
});
```

**Lines 22-29.** Update one or more fields.

**`if (req.body.status)`** — only update if the client sent it. This is the "partial" in partial update.

## What we learned

1. PATCH = partial update
2. PUT = full replacement (we'll see this later)
3. We can update multiple fields in one call
4. We've now seen POST, PATCH, DELETE — the full CRUD

## What's next

In **27-movie-watchlist** we build a movie watchlist. Same shape, different data.

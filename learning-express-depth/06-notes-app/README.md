# 06 — Notes App

Same structure as the todo app, but for notes. Notes have more fields than todos (a body, a createdAt timestamp). We also add a GET `/notes/:id` to fetch a single note.

## Run it

```bash
npm install
node server.js
```

```bash
# Create a note (title and body)
curl -X POST http://localhost:3000/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Meeting notes", "body": "Discussed Q1 plans"}'
# { "id": 1, "title": "Meeting notes", "body": "Discussed Q1 plans", "createdAt": "2024-..." }

# Create a note with only a title (body is optional)
curl -X POST http://localhost:3000/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Quick thought"}'
# { "id": 2, "title": "Quick thought", "body": "", "createdAt": "..." }

# Get all notes
curl http://localhost:3000/notes
# { "count": 2, "notes": [...] }

# Get a specific note
curl http://localhost:3000/notes/1
# { "id": 1, "title": "Meeting notes", "body": "...", "createdAt": "..." }

# Delete a note
curl -X DELETE http://localhost:3000/notes/1 -i
# HTTP/1.1 204 No Content
```

## How to think about it

Every CRUD app has the same shape:
- GET `/things` — list all
- GET `/things/:id` — get one
- POST `/things` — create one
- DELETE `/things/:id` — delete one
- (later) PATCH `/things/:id` — update one

The data is different (todos have a `done` flag, notes have a `body`), but the structure is the same. Once you've built three or four of these, you can build any of them.

## How to build it (line by line)

```js
const notes = [];
```

**Line 6.** Same as the todo app — an array in memory. The data is different (notes have a `body` and a `createdAt`), but the storage is the same.

```js
app.post('/notes', (req, res) => {
  const { title, body } = req.body;
  const note = {
    id: notes.length + 1,
    title,
    body: body || '',
    createdAt: new Date().toISOString(),
  };
```

**Lines 14-22.** The new todo, but with three new things:

1. **Destructuring two fields**: `const { title, body } = req.body` pulls both at once.
2. **`body: body || ''`**: If the client didn't send a body, use an empty string. The `||` means "or, if the left is falsy." Empty string is falsy.
3. **`new Date().toISOString()`**: The current time as a string. The ISO format is "YYYY-MM-DDTHH:MM:SS.sssZ" — sort of. It's a standard that computers understand.

```js
app.get('/notes/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const note = notes.find(n => n.id === id);
  if (!note) return res.status(404).json({ error: 'Note not found' });
  res.json(note);
});
```

**Lines 28-33.** New endpoint: get one note by id.

- `notes.find(n => n.id === id)` — find the first note where the id matches. If not found, returns `undefined`.
- `if (!note)` — if the note is undefined (not found), return 404.
- Otherwise, send the note.

**Why `find` instead of `findIndex`?** Here we want the note itself, not its position. `find` returns the item, `findIndex` returns the position.

## What we learned

1. The same CRUD pattern works for any kind of data
2. `body || ''` provides a default value
3. `new Date().toISOString()` gives a standard timestamp
4. `find` returns the item, `findIndex` returns the position
5. We've now built two apps with the same structure

## What's next

In **07-blog-app** we build a blog. A blog post is similar to a note (title, body) but with one new thing: an author. The structure stays the same — we just add a field and use it in the response.

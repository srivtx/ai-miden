# 37 — Kanban Board

A Kanban board. Cards have a column (todo / in_progress / done). We can move them between columns. New thing: **enum validation** (the column must be one of three values).

## Run it

```bash
npm install
node server.js
```

```bash
# Add cards
curl -X POST http://localhost:3000/cards -H "Content-Type: application/json" -d '{"title": "Build feature"}'
curl -X POST http://localhost:3000/cards -H "Content-Type: application/json" -d '{"title": "Fix bug"}'

# See the board (grouped by column)
curl http://localhost:3000/cards
# { "todo": [...], "in_progress": [], "done": [] }

# Move a card
curl -X PATCH http://localhost:3000/cards/1/move \
  -H "Content-Type: application/json" \
  -d '{"column": "in_progress"}'

# Try a bad column
curl -X PATCH http://localhost:3000/cards/1/move \
  -H "Content-Type: application/json" \
  -d '{"column": "frozen"}'
# 422 { "error": "column must be todo, in_progress, or done" }
```

## How to think about it

The shape is the same. The new thing: a "move" endpoint (action endpoint) and enum validation. Enums are everywhere: status, priority, role, type. We always check the value is in the allowed list.

## How to build it (line by line)

```js
if (!['todo', 'in_progress', 'done'].includes(column)) {
  return res.status(422).json({ error: '...' });
}
```

**Lines 25-27.** Check the value is in the allowed list. `includes` returns true if the value is in the array.

**Why this check?** Without it, a client could send `column: "frozen"` and our data would be inconsistent. We protect the shape.

## What we learned

1. Enums: only certain values are valid for a field
2. `Array.includes` checks if a value is in the list
3. Action endpoints (`/move`) are different from CRUD endpoints
4. We've now seen 3 action endpoints: vote, submit, move

## What's next

In **38-inventory** we build an inventory tracker. Items have a quantity. We can add and remove stock.

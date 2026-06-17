# 03 — Todo List (empty list)

The first "real" API endpoint. It returns the list of todos. Right now the list is empty — we just send `[]` back.

## Run it

```bash
npm install
node server.js
```

```bash
curl http://localhost:3000/todos
# { "count": 0, "todos": [] }
```

## How to think about it

Before we can add or delete todos, we need an endpoint to see them. We start with an empty list. We need somewhere to store the list — for now, just an array in memory.

## How to build it (line by line)

```js
const todos = [];
```

**Line 5.** We declare a variable `todos` and set it to an empty array. This array will hold all our todos. For now, it's empty.

**Why an array?** Lists are the most common data structure. You can add to them, remove from them, loop over them, and get their count.

**Why in memory?** Simplest thing that works. When we restart the server, the array is empty again. That's fine for now — we'll add a database later.

```js
app.get('/todos', (req, res) => {
  res.json({ count: todos.length, todos });
});
```

**Lines 7-9.** When someone does GET `/todos`, we send back a JSON object with two fields:
- `count` — how many todos we have (`todos.length`)
- `todos` — the actual list (the array)

**Why both count and the array?** The client can show "5 todos" without counting the array themselves. It's a small convenience.

**Why `res.json` instead of `res.send`?** `res.json` sets the right Content-Type header (`application/json`) and serializes the object. `res.send` would also work, but it doesn't always set the JSON header.

## What we learned

1. We can store data in a variable in memory
2. `app.get('/path', ...)` returns data
3. `res.json({...})` sends JSON
4. `array.length` gives us the count

## What's next

In **04-todo-add** we add a way to put new todos into the list. We'll need to read JSON from the request body.

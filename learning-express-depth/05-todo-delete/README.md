# 05 — Todo Delete

Now we can remove todos. The client sends `DELETE /todos/1` and we remove the one with id 1.

## Run it

```bash
npm install
node server.js
```

```bash
# See the list (we pre-seeded 2 todos)
curl http://localhost:3000/todos
# { "count": 2, "todos": [...] }

# Delete todo #1
curl -X DELETE http://localhost:3000/todos/1 -i
# HTTP/1.1 204 No Content

# See the list — only 1 left
curl http://localhost:3000/todos
# { "count": 1, "todos": [{ "id": 2, "title": "Walk dog", "done": false }] }

# Try to delete a todo that doesn't exist
curl -X DELETE http://localhost:3000/todos/99 -i
# HTTP/1.1 404 Not Found
# { "error": "Todo not found" }
```

## How to think about it

Now the list can grow AND shrink. We have all four CRUD operations except Update. Adding "update" would be a natural next step, but we want to keep the steps small.

The interesting new thing here is the URL parameter: `/todos/:id`. The colon makes `id` a placeholder for whatever the client puts in the URL.

## How to build it (line by line)

```js
app.delete('/todos/:id', (req, res) => {
```

**Line 25.** Register a handler for DELETE requests to `/todos/:id`. The `:id` is a URL parameter.

**What is a URL parameter?** It's a placeholder in the URL. If the client sends `DELETE /todos/1`, then `id` is `1`. If they send `DELETE /todos/42`, then `id` is `42`.

**The colon** tells Express: "this is a parameter, not a literal character." Without the colon, Express would look for the literal text ":id" in the URL.

```js
  const id = parseInt(req.params.id);
```

**Line 27.** Get the id from the URL and convert to a number.

**`req.params.id`** is the value the client put in the URL. It's always a string — even if it looks like a number. So `"1"` is a string, not the number 1. We use `parseInt` to convert.

```js
  const index = todos.findIndex(t => t.id === id);
```

**Line 30.** Find where the todo is in the array.

**`findIndex`** loops through the array and returns the index of the first item that matches. If nothing matches, it returns `-1`.

**The arrow function** `t => t.id === id` is the condition. For each todo `t`, check if its id matches.

```js
  if (index === -1) {
    return res.status(404).json({ error: 'Todo not found' });
  }
```

**Lines 33-35.** If `findIndex` returned `-1`, the todo doesn't exist. Return 404.

**Why 404?** It's the standard status code for "not found." The client knows the URL is wrong or the resource was deleted.

**Why return early?** `return res.status(...).json(...)` sends the response and stops the function. If we didn't return, the function would keep going and try to delete from index `-1`.

```js
  todos.splice(index, 1);
```

**Line 38.** Remove the todo at that index. `splice(index, 1)` removes 1 item starting at `index`.

**Why splice?** It modifies the array in place. After this, the array is shorter by one.

```js
  res.status(204).end();
```

**Line 41.** Send a response with status 204 (No Content) and no body.

**Why 204?** It's the standard status code for "I did the thing, but there's nothing to send back." Different from 200 (which usually has a body).

**Why `.end()` instead of `.json()`?** `.end()` sends an empty response. We don't have anything to put in the body.

## What we learned

1. URL parameters with `:name` capture parts of the URL
2. `req.params.name` gets the value (as a string)
3. `findIndex` finds the position of an item in an array
4. `splice(index, 1)` removes an item from an array
5. 404 means "not found"
6. 204 means "success, no body"

## What's next

In **06-notes-app** we start a new app. Instead of building on the todo app, we start fresh with notes. The pattern is similar (list, add, delete) but the data is different — notes have a body, not just a title. This is how we build many apps: same structure, different data.

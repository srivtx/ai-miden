# 04 — Todo Add

Now we can add todos. The client sends a POST request with a title, and we add it to the list.

## Run it

```bash
npm install
node server.js
```

```bash
# Add a todo
curl -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
# { "id": 1, "title": "Buy milk", "done": false }

# Add another
curl -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Walk dog"}'
# { "id": 2, "title": "Walk dog", "done": false }

# See them all
curl http://localhost:3000/todos
# { "count": 2, "todos": [{...}, {...}] }
```

## How to think about it

Now the list isn't always empty — we can add to it. The client sends data to the server. The server reads it, makes a new todo, and saves it. Then it sends the new todo back.

## How to build it (line by line)

```js
app.use(express.json());
```

**Line 8.** This is middleware — a function that runs before our routes. It tells Express: "If the request has a JSON body, parse it and put it on `req.body`."

**Without this line:** `req.body` would be `undefined`. Express doesn't read request bodies by default — you have to opt in.

**Why JSON?** Because that's what we send from the client. `-H "Content-Type: application/json"` tells the server: "the body is JSON."

```js
app.post('/todos', (req, res) => {
```

**Line 16.** `app.post` is for POST requests. POST means "create something new." We register a handler for POST `/todos`.

```js
  const { title } = req.body;
```

**Line 18.** Destructure `title` from the body. If the client sent `{"title": "Buy milk"}`, then `title` is `"Buy milk"`.

**What is destructuring?** `const { title } = req.body` is the same as `const title = req.body.title`. Shorter.

```js
  const todo = { id: todos.length + 1, title, done: false };
```

**Line 21.** Make a new todo object with three fields:
- `id` — a unique number. We use `todos.length + 1` for now.
- `title` — what the client sent
- `done` — starts as `false`

**Why an object?** A todo has more than just a title. It has an id, a status, maybe a date. An object holds all of those.

```js
  todos.push(todo);
```

**Line 24.** Add the new todo to the end of the array. `push` is an array method that adds to the end.

```js
  res.status(201).json(todo);
```

**Line 27.** Send back the new todo. `status(201)` sets the HTTP status to 201 (Created — different from 200 OK). `json(todo)` sends the todo as JSON.

**Why 201?** It's the standard status code for "I created something." 200 means "OK, here's what you asked for." 201 means "OK, I made something new."

## What we learned

1. `app.use(express.json())` reads JSON bodies
2. `app.post('/path', ...)` handles POST requests
3. `req.body` has the data the client sent
4. `res.status(201).json(...)` returns the new thing with 201
5. Arrays in memory are fine for simple things

## What's next

In **05-todo-delete** we add a way to remove todos by their id. The client will send `DELETE /todos/1` and we'll remove the one with id 1.

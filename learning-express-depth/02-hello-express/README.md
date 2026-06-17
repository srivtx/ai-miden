# 02 — Hello Express

Same as project 01, but using Express. We get cleaner code and easier routing.

## Setup

```bash
npm install
node server.js
```

In another terminal:
```bash
curl http://localhost:3000
# Hello
```

## How to think about it

`01-hello-server` worked, but every request hit the same handler. We had to check `req.url` to know what the user wanted. With Express, we say: "for this URL, do this. For that URL, do that."

## How to build it (line by line)

```js
const express = require('express');
```

**Line 1.** Loads Express. We installed it with `npm install`. The `package.json` lists it as a dependency.

```js
const app = express();
```

**Line 3.** `express()` creates an app. The `app` is what we register routes on.

```js
app.get('/', (req, res) => {
  res.send('Hello');
});
```

**Line 5-7.** `app.get('/', handler)` says: "When someone does a GET request to `/`, run this handler."

- `app.get` = register a handler for GET requests
- `'/'` = the URL path
- `handler` = the function that runs

Inside the handler:
- `req` = the request
- `res` = the response
- `res.send('Hello')` = send "Hello" as the body

```js
app.listen(3000, () => console.log('Server on http://localhost:3000'));
```

**Line 10.** Start the server on port 3000.

## What changed from project 01

| Project 01 | Project 02 |
|---|---|
| `http.createServer` | `express()` |
| One handler for all URLs | `app.get('/path', ...)` per URL |
| `res.end('Hello')` | `res.send('Hello')` |
| Manual URL parsing | Express handles it |

## What we learned

1. Express is a layer on top of Node's `http` that makes routing easier
2. `app.get(path, handler)` registers a route
3. `res.send(string)` sends a response
4. `app.listen(port)` starts the server

## What's next

In **03-todo-list** we add a list endpoint. The list will be empty at first — we just return an empty array. After that, we add ways to add and remove items.

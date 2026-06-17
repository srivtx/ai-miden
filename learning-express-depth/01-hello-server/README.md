# 01 — Hello Server

The smallest possible server. No Express, no libraries — just Node's built-in `http`.

## Run it

```bash
node server.js
```

In another terminal:
```bash
curl http://localhost:3000
# Hello
```

## How to think about it

A server is just a program that:
1. Waits for someone to connect
2. Reads what they sent
3. Sends something back

That's it. Everything else — Express, databases, auth — is built on top of these three things.

## How to build it (line by line)

```js
const http = require('http');
```

**Line 1.** `require('http')` loads Node's built-in HTTP module. Node ships with this — you don't install anything. The module has functions for creating servers and making requests.

```js
http.createServer((req, res) => {
```

**Line 3.** `createServer` takes a function. That function runs every time someone connects. It receives two things:
- `req` — the incoming request (what the client sent)
- `res` — the response (what we'll send back)

```js
  res.end('Hello');
```

**Line 4.** `res.end(...)` sends a response and closes the connection. The string `'Hello'` becomes the body of the response.

```js
}).listen(3000, () => console.log('Server on http://localhost:3000'));
```

**Line 6.** `.listen(3000, callback)` makes the server wait for connections on port 3000. The callback runs once when the server is ready.

## What we learned

1. A server is `createServer` + a function that handles requests
2. The function gets `req` (what came in) and `res` (what we send back)
3. `res.end(string)` sends a response
4. `.listen(port)` makes it wait for connections

## What's next

In **02-hello-express** we replace this with Express. Same idea, but easier to write routes.

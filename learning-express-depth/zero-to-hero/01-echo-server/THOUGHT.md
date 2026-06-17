# The Thought

> *"HTTP is just a string format. Servers are just string parsers."*

## The 30,000-Foot View

When you open a browser and type `http://example.com`, three things happen:

1. Your browser opens a **TCP connection** to `example.com` on **port 80**.
2. Your browser writes a **string** to that connection that looks like this:

```
GET / HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 ...
Accept: text/html

```

3. The server reads that string, decides what to do, and writes back **another string**:

```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1234

<html>...</html>
```

That is the entire model. HTTP is a string format. Servers are string parsers. The internet is billions of machines doing this dance.

Node's `node:http` module hides the TCP layer (so you don't have to write socket code) and gives you the parsed request and a writable response object. That's it. Express is a thin layer on top. Fastify is a thin layer on top. Hono is a thin layer on top. They all, ultimately, do exactly what we are about to do.

## The Request, Line by Line

What does a request actually look like? Let's look at what your browser sends when you visit `http://localhost:3000/hello?name=alice`:

```
GET /hello?name=alice HTTP/1.1\r\n
Host: localhost:3000\r\n
User-Agent: Mozilla/5.0 (Macintosh; ...)\r\n
Accept: text/html,application/xhtml+xml\r\n
Accept-Language: en-US,en;q=0.9\r\n
Connection: keep-alive\r\n
\r\n
```

Three parts:

1. **Request line**: `METHOD PATH HTTP/VERSION`
   - Method: `GET` (we want to read), `POST` (we want to write), `PUT`, `DELETE`, `PATCH`, etc.
   - Path: `/hello?name=alice` (the URL the user wants, including the query string)
   - Version: `HTTP/1.1` (almost always 1.1 today; HTTP/2 and HTTP/3 exist but are layered)
2. **Headers**: `Key: Value` pairs, one per line
   - `Host: localhost:3000` — which server (important when one IP hosts many sites)
   - `User-Agent: ...` — what browser
   - `Accept: ...` — what formats the client can understand
   - Many more
3. **Empty line** (`\r\n\r\n`): the separator between headers and body
4. **Body**: optional, present for `POST` / `PUT` / `PATCH`, absent for `GET` / `DELETE`

When the empty line is sent, the client is done writing the request. The server is now free to read it and respond.

## The Response, Line by Line

The server writes back:

```
HTTP/1.1 200 OK\r\n
Content-Type: text/plain\r\n
Content-Length: 14\r\n
\r\n
Hello, world.\n
```

Three parts:

1. **Status line**: `HTTP/VERSION STATUS-CODE REASON-PHRASE`
   - `200 OK` — success
   - `201 Created` — for `POST` that creates a resource
   - `204 No Content` — for `DELETE` that succeeded
   - `301 Moved Permanently` — redirect
   - `400 Bad Request` — client sent garbage
   - `401 Unauthorized` — needs auth
   - `403 Forbidden` — authed but not allowed
   - `404 Not Found` — URL doesn't exist
   - `500 Internal Server Error` — server bug
2. **Headers**: same format as request
   - `Content-Type` — what format is the body (so the client knows how to render it)
   - `Content-Length` — how many bytes (so the client knows when to stop reading)
3. **Body**: the actual payload

## What Node Gives You

When `http.createServer(handler)` calls your `handler(req, res)`:

- `req` is a **readable stream** of the parsed request:
  - `req.method` — `'GET'`, `'POST'`, etc.
  - `req.url` — the path + query string (`'/hello?name=alice'`)
  - `req.headers` — an object of header name → value
  - `req` is also a stream: you can listen to `'data'` and `'end'` events to read the body (project 05)

- `res` is a **writable stream** you use to build the response:
  - `res.statusCode = 200` — set the status
  - `res.setHeader('Content-Type', 'text/plain')` — set a header
  - `res.end('Hello, world.\n')` — send the body and close the connection
  - You can also `res.write('chunk')` multiple times, but you must call `res.end()` exactly once

That's the whole API. `req` is incoming. `res` is outgoing. You bridge them.

## Why 30 Lines Is Enough

Our entire server is 30 lines because the model is simple. The complexity of a *real* server — handling 10,000 concurrent connections, parsing query strings, validating bodies, managing sessions, talking to a database — is *all* layered on top of this 30-line core. When you understand the core, the layers become intelligible. When you don't, the layers are magic.

## Common Confusions (read these — they will save you hours)

**Confusion 1: "What's the difference between `http` and `https`?"**
`https` is `http` over an encrypted TLS connection. The server speaks the same HTTP protocol, but the bytes are encrypted before they go on the wire. For now, we use plain `http`. We'll discuss TLS in a later project.

**Confusion 2: "Why port 3000?"**
Ports are just numbers from 0 to 65535 used to identify which *program* on a machine should receive incoming connections. Port 80 is HTTP, 443 is HTTPS, 22 is SSH, 5432 is Postgres. Ports below 1024 are "privileged" (need root on Linux). Ports above 1024 are free for anyone. We use 3000 because it's the convention for "I'm a dev server, don't take this seriously."

**Confusion 3: "What is `localhost`?"**
`localhost` is a name that resolves to the IP `127.0.0.1`, which always means "this machine." So `http://localhost:3000` means "talk to a server running on this machine, on port 3000." If you deploy to a real server, you'd use its public IP or domain name.

**Confusion 4: "Why does `res.end()` close the connection?"**
HTTP/1.1 by default uses *persistent connections*: after one response, the connection stays open for more requests. But once you call `res.end()`, *this* response is done — the connection can be reused. The server doesn't *force* a close unless the client sent `Connection: close`. But for our purposes, we don't need to think about this.

**Confusion 5: "What is a stream?"**
A stream is an object that produces or consumes data in chunks, not all at once. `req` is a *readable* stream (data flows in, you listen for chunks). `res` is a *writable* stream (you push chunks, they flow out). Streams are how Node handles large data without loading it all into memory. We use them lightly here; project 05 (Body Parser) uses them seriously.

**Confusion 6: "What happens if I forget `res.end()`?"**
The client hangs. It waits forever for the response. The connection times out after a while (browser default: 30s). The user sees a spinner. The server holds the connection open. Memory leaks accumulate under load. Always call `res.end()`.

**Confusion 7: "What is `Content-Type` for?"**
It tells the client how to interpret the body. `text/plain` means "this is just text." `text/html` means "this is HTML, render it as a page." `application/json` means "this is JSON, parse it." If you don't set it, the client guesses (and usually guesses `text/html`, which can be a security hole — see XSS in project 17).

## What We Are About to Build

We are about to build the simplest possible server:

```js
const http = require('node:http');

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello, world.\n');
});

server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

That's it. In [BUILD.md](./BUILD.md) we will go line by line and explain every single character.

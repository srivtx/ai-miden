# The Build

> *"Every character earns its place."*

We are going to build the echo server, line by line, character by character. By the end, you will not just know what each line does — you will know *why* it exists, what would happen without it, and what trade-offs were made.

## The File

Create a new file called `server.js`. We will fill it in together.

```bash
touch server.js
```

That's our entire project. No `package.json`. No `node_modules`. No `npm install`. Just one file. This is the smallest possible Node program that does something useful.

---

## Line 1: The Import

```js
const http = require('node:http');
```

### What it does

Loads Node's built-in HTTP module and assigns it to the constant `http`.

### Why `node:http` and not just `http`?

Both work, but the `node:` prefix is a Node.js convention introduced in v14 to make it obvious that a module is built-in (core) rather than third-party (from `npm`). With the prefix, anyone reading your code instantly knows: "this is a Node built-in, no install needed." Without the prefix, they might wonder if `http` is a typo of some npm package.

The convention is recommended but not required. We use it for clarity.

### What does this line actually do?

When Node starts up, it has a registry of *core modules* compiled into the binary. `http` is one of them. `require('node:http')` looks up that module in the registry and returns it. It does not touch the network. It does not read the file system. It just gives you back an object with functions on it: `http.createServer`, `http.request`, `http.get`, etc.

### What if I forget this line?

The next line (`http.createServer`) will throw `ReferenceError: http is not defined`. Node will crash before the server even starts. Imports are not optional.

### A tiny side note

You might also see `import http from 'node:http'` if the file has `"type": "module"` in `package.json`. We are using the older CommonJS `require` syntax because it works in any Node project with no configuration. Project 02 will keep using it. We will discuss ES modules when we have a reason to.

---

## Line 3: The Server Factory

```js
const server = http.createServer((req, res) => {
```

### What it does

Calls `http.createServer(handler)` where `handler` is the function `(req, res) => { ... }`. This *creates* a server object — but does not start it yet. The server is like a phone that is plugged in but not ringing.

### What is `req`?

`req` (short for "request") is an object Node gives you representing the incoming HTTP request. It is *not* the raw bytes from the network — Node has already parsed the request line and headers for you. You get a clean object with useful properties:

- `req.method` — a string like `'GET'`, `'POST'`, `'PUT'`, `'DELETE'`
- `req.url` — a string like `'/'` or `'/users?role=admin'`
- `req.headers` — an object of header name → value (e.g., `req.headers['user-agent']`)

In project 05 we will see that `req` is also a *readable stream*, and we can read its body. For now, we only use `req.method` and `req.url`.

### What is `res`?

`res` (short for "response") is an object you use to build the outgoing HTTP response. It is a *writable stream*. You push data into it; Node sends it down the TCP connection. Methods:

- `res.statusCode = 200` — set the HTTP status code (default is 200)
- `res.setHeader('Content-Type', 'text/plain')` — set a header
- `res.write('chunk')` — push a chunk of body data
- `res.end('final chunk')` — push the last chunk and signal "I'm done"

`res.end()` is **mandatory**. If you don't call it, the client will hang forever waiting for the response. (We'll explore this in the experiments section.)

### What is the arrow function?

`((req, res) => { ... })` is an arrow function — a shorthand for a function expression. It is *the same thing* as:

```js
function handler(req, res) {
  // ...
}
```

The arrow syntax is shorter. The semantics are essentially identical (one difference: arrow functions don't have their own `this`, but we don't use `this` here).

The handler is called by Node **every time a new request arrives**. If 1,000 clients connect at the same time, Node calls your handler 1,000 times (potentially concurrently — Node is single-threaded but uses async I/O, so concurrency comes from the event loop).

### What does `createServer` return?

A `http.Server` object. It has methods:

- `server.listen(port, callback)` — start listening for connections
- `server.close()` — stop listening
- `server.on('request', handler)` — the same as passing the handler to `createServer`

We use the first form here.

### Why is `const server =` there?

So we can later call `server.listen(...)`. If we did `http.createServer(handler).listen(3000)`, it would work too, but we wouldn't have a reference to the server object. Keeping the reference lets us close the server, attach more handlers, or pass it to tests. Conventions matter; this is a clean one.

---

## Line 4: The Status Code

```js
  res.statusCode = 200;
```

### What it does

Sets the HTTP status code of the response to `200`. This becomes the first thing written to the response: `HTTP/1.1 200 OK`.

### Why 200?

`200` means "OK — success, here's the body." It is the default for any successful operation. Other common codes:

- `201 Created` — used after a `POST` that created a resource
- `204 No Content` — used after a `DELETE` that succeeded (no body to send back)
- `301 Moved Permanently` — redirect
- `400 Bad Request` — client sent malformed input
- `401 Unauthorized` — needs authentication
- `403 Forbidden` — authed but not allowed
- `404 Not Found` — URL doesn't exist
- `500 Internal Server Error` — your code crashed

If you don't set `res.statusCode`, Node defaults to `200`. So this line is technically optional in this case. But setting it explicitly is good practice — it makes your intent clear to anyone reading the code. And in project 02, when we have many routes returning different codes, the explicit assignment will matter.

### What is a status code "for"?

It is a *contract* between your server and the client. The client uses it to decide what to do. A browser sees `301` and follows the redirect. A fetch client sees `401` and prompts for credentials. A retry library sees `500` and tries again. Without status codes, the client would have to parse the body to figure out what happened — error-prone and slow.

---

## Line 5: The Header

```js
  res.setHeader('Content-Type', 'text/plain');
```

### What it does

Sets the `Content-Type` header of the response to `text/plain`. This tells the client: "the body I am about to send is plain text."

### Why do we need this?

Without a `Content-Type`, the client doesn't know how to interpret the body. The browser would default to sniffing the content (looking for `<html>` tags etc.) which is slow and a security risk. A fetch client would have to guess. A typed API client would fail. Always set `Content-Type`.

Common values:

- `text/plain` — plain text
- `text/html` — HTML
- `application/json` — JSON
- `image/png`, `image/jpeg` — images
- `application/octet-stream` — binary data, "just save it"

We use `text/plain` because our body `'Hello, world.\n'` is plain text.

### Why is this a method call and not an assignment?

Node stores headers in a special internal data structure (it has to send them before the body, and the body is streaming). `setHeader` is the API for adding to that structure. You can also call `res.writeHead(statusCode, headers)` to set status and headers in one shot, but using `statusCode` and `setHeader` separately is more flexible when you build the response incrementally.

### What if I forget this?

Most browsers will *probably* still display "Hello, world." — but they will guess the type, which can lead to XSS vulnerabilities when the body contains user-controlled data. For an API, the client will fail to parse. Always set it.

---

## Line 6: The Body

```js
  res.end('Hello, world.\n');
```

### What it does

Sends the string `'Hello, world.\n'` as the body, then closes the response (or signals "no more chunks coming" if the connection is persistent).

### Three things happen here

1. **The body is written**: Node takes the string, encodes it to bytes (UTF-8 by default), and writes them to the underlying TCP socket.
2. **The response is finalized**: Node sends the empty line that separates headers from body, and signals to the TCP layer that we are done writing.
3. **The handler returns**: control goes back to Node's event loop.

### Why is `res.end()` mandatory?

`res` is a writable stream. Streams have two phases: writing data, and ending. If you write but don't end, the stream is in an indeterminate state — the receiver doesn't know if more data is coming. So `end()` is how you say "I'm done." If you don't call it, the client will wait forever (until its timeout).

### What does `\n` do?

It's a newline character. Just for prettiness — `curl` will print `Hello, world.` followed by a newline. Without it, your terminal prompt would appear immediately after the period.

### What if I want to send a JSON object?

You would do:

```js
res.setHeader('Content-Type', 'application/json');
res.end(JSON.stringify({ message: 'Hello, world.' }));
```

This is project 03's whole premise. For now, plain text.

### What if I want to send binary data (an image)?

You would do:

```js
const fs = require('node:fs');
const image = fs.readFileSync('./logo.png');
res.setHeader('Content-Type', 'image/png');
res.end(image);
```

`res.end()` accepts a Buffer as well as a string. We'll see this in project 20 (Uploader).

### What if the body is huge?

You don't want to load it all into memory. You would do:

```js
const fs = require('node:fs');
const stream = fs.createReadStream('./huge-video.mp4');
res.setHeader('Content-Type', 'video/mp4');
stream.pipe(res); // automatically calls res.end() when done
```

We'll see this in project 20 (Uploader) and project 51 (Streams).

---

## Line 7: Close the Handler

```js
});
```

### What it does

Closes the arrow function and the `createServer` call. Just a brace and a paren.

---

## Line 9: Start Listening

```js
server.listen(3000, () => {
```

### What it does

Tells the server to start listening for connections on port 3000. The second argument is a *callback* — a function that runs *once*, after the server is ready to accept connections.

### Why does it have a callback?

`listen` is asynchronous. It has to ask the operating system for permission to bind to port 3000. That takes a few milliseconds. You don't want to start sending traffic to the server before it's ready. The callback fires when binding is complete and the server is officially "listening."

The callback is optional. If you don't care when listening starts, omit it. But for the startup log, it's perfect.

### What is "binding"?

When the OS starts a process, it has 65,535 ports it can listen on. "Binding" means claiming one. Until you bind, no one can connect to you on that port. After binding, connections start arriving in the kernel's buffer, and Node picks them up and calls your handler.

### Why does the callback have empty parens after the arrow?

Because we don't use any arguments. The callback receives no useful data here. The empty `()` is the parameter list. (Some style guides allow `_ =>` to indicate "ignored parameter," but `() =>` is fine and common.)

---

## Line 10: The Log

```js
  console.log('Server listening on http://localhost:3000');
```

### What it does

Prints a confirmation message to the terminal.

### Why?

So *you* know the server started. If this line never prints, the server didn't start, and you can investigate before wondering why `curl` is hanging.

### What is `localhost`?

A name that resolves to the IP `127.0.0.1`, which always means "this machine." From outside this machine, this address is unreachable — you would need the machine's public IP or a domain name. For development, `localhost` is the right choice.

---

## Line 11: Close the Listen Callback

```js
});
```

Just closing the callback and the call. Same as before.

---

## The Full File

Let me lay out the entire file with line numbers:

```js
1  const http = require('node:http');
2
3  const server = http.createServer((req, res) => {
4    res.statusCode = 200;
5    res.setHeader('Content-Type', 'text/plain');
6    res.end('Hello, world.\n');
7  });
8
9  server.listen(3000, () => {
10   console.log('Server listening on http://localhost:3000');
11 });
```

Eleven lines of code. Three conceptual parts:

- **Line 1**: load the HTTP module
- **Lines 3-7**: define the request handler (what to do when a request comes in)
- **Lines 9-11**: start the server listening

That's it. That is a web server.

---

## Run It

```bash
node server.js
```

You should see:

```
Server listening on http://localhost:3000
```

In a new terminal:

```bash
curl http://localhost:3000
```

You should see:

```
Hello, world.
```

Congratulations. You have just built a web server from scratch.

---

## Experiments

To really internalize this, break things on purpose. Change the code, run it, see what happens. Here are some experiments to try:

### Experiment 1: Forget `res.end()`

```js
const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.write('Hello, world.\n');
  // forgot res.end()
});
```

Run it. `curl` will hang. Press Ctrl+C. This teaches you that `res.end()` is not optional decoration — it is the signal that closes the response.

### Experiment 2: Set the wrong status code

```js
res.statusCode = 500;
```

Run it. `curl -i` will show `HTTP/1.1 500 Internal Server Error`. Now run it with `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000` and you'll see `500`. The client (browser, fetch, anything) will see a 500 and may show an error.

### Experiment 3: Forget the Content-Type

```js
// res.setHeader('Content-Type', 'text/plain');
// (commented out)
```

Run it. `curl -i` will not show a Content-Type header. The body will still arrive, but the client doesn't know what to do with it. In a browser, the page will probably still display (browsers sniff), but an API client would fail.

### Experiment 4: Send HTML

```js
res.setHeader('Content-Type', 'text/html');
res.end('<h1>Hello, world.</h1>');
```

Run it. Open `http://localhost:3000` in a browser. You will see a giant "Hello, world." rendered as a heading. This is the simplest possible web page.

### Experiment 5: Multiple requests

Open two terminals. In one, run `node server.js`. In the other, run `curl http://localhost:3000 & curl http://localhost:3000 & curl http://localhost:3000 &`. The `&` runs them in parallel. Your handler will be called three times. The log will not show three "listening" messages — only the initial one — but Node is handling all three requests concurrently via the event loop. This is the magic of Node: single-threaded, but handling thousands of connections.

### Experiment 6: Make it crash

```js
const server = http.createServer((req, res) => {
  throw new Error('boom');
});
```

Run it. `curl` will get... a connection, then nothing. The connection hangs. The server doesn't crash (Node catches the throw inside the handler), but the response is never sent. The client times out. This is a bug. Project 15 (Error Wall) is about catching this properly.

---

## Summary

You now have a working HTTP server. You understand:

- What a request is (method, URL, headers, body)
- What a response is (status, headers, body)
- That HTTP is a string protocol over TCP
- That Node hides the TCP layer and gives you parsed objects
- That `res.end()` is mandatory
- That `Content-Type` tells the client how to interpret the body

These are the foundations. Project 02 (Router) will extend this by adding multiple URLs. Project 03 (JSON API) will change the body format. Each project adds one thing, and by the end, you have a real server.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves for the next one.

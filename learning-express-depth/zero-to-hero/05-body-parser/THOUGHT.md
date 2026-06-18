# The Thought

> *"Streams are how Node handles data that hasn't arrived yet. Read the chunks. Wait for the end. Parse. Use."*

## What a Stream Is

A stream is an object that produces or consumes data in *chunks*, not all at once. Node uses streams for:

- **Network I/O** (HTTP requests/responses)
- **File I/O** (reading a file)
- **Standard input/output** (process.stdin, process.stdout)
- **Compression** (gzip, deflate)
- **Encryption** (TLS)
- **Child processes** (stdout, stderr)

The alternative to streams is *buffers* — loading all the data into memory at once. For a 10 GB file upload, that would require 10 GB of RAM. With streams, you process 64 KB at a time, using a constant amount of memory.

Streams are how Node handles large data without running out of memory.

## Readable Streams and the `'data'` / `'end'` Events

`req` is a *readable stream* — data flows *in*. The stream emits events:

- `'data'` — emitted when a new chunk of data arrives. The chunk is a `Buffer` (raw bytes).
- `'end'` — emitted when the data is done. No more chunks will come.
- `'error'` — emitted if something goes wrong (e.g., the client disconnects mid-body).
- `'close'` — emitted when the underlying resource is closed.

To read the entire body:

```js
const chunks = [];
req.on('data', (chunk) => {
  chunks.push(chunk);
});
req.on('end', () => {
  const body = Buffer.concat(chunks).toString('utf8');
  // body is now the full text of the request body
});
```

This is the standard pattern. The `'data'` listener collects chunks. The `'end'` listener runs when there's nothing left.

## Why Not Read Synchronously?

You might think: "Why can't I just call `req.read()` and get the body?"

Because the data hasn't arrived yet. The client is still sending. If you call `req.read()` immediately, you get an empty buffer. You have to wait.

Streams use *events* instead of return values precisely because the data is *not available yet*. When a `'data'` event fires, that chunk has arrived. When `'end'` fires, you're done. The pattern is *event-driven*, not *call-and-return*.

This is what "asynchronous" means in Node. The rest of the program continues while the body is being received. When the body is fully received, *then* we run the handler.

## Buffers: Raw Bytes

A `Buffer` is Node's way of representing raw bytes. It's like a `Uint8Array` (typed array of bytes) with extra methods for binary data.

When you push a chunk to `chunks`, you're pushing a Buffer. Each Buffer is a chunk of bytes:

```
chunks = [
  <Buffer 7b 22 6e 61 6d 65 22 3a 20 22 45 76 65 22 7d>,  // {"name": "Eve"}
]
```

Each byte is shown in hex. `7b` is `{`, `22` is `"`, `6e` is `n`, etc. Together, they spell out the JSON.

`Buffer.concat(chunks)` concatenates all the chunks into one Buffer. `Buffer.concat([b1, b2, b3])` is the same as `b1 + b2 + b3` (in bytes).

`buf.toString('utf8')` decodes the bytes as UTF-8 text. Now we have the full string `{"name": "Eve"}`.

## JSON.parse

Once we have the text, we can parse it as JSON:

```js
const obj = JSON.parse('{"name": "Eve"}');
// obj: { name: 'Eve' }
```

`JSON.parse` throws on invalid JSON. So we wrap it in `try/catch`:

```js
try {
  req.body = JSON.parse(raw);
} catch (err) {
  json(res, 400, { error: 'Invalid JSON' });
  return;
}
```

`400 Bad Request` is the right code. The client sent something we couldn't parse.

## Empty Body

`GET` requests (and some `POST`s) have no body. In that case, no `'data'` events fire, only `'end'`. `chunks` is `[]`, `Buffer.concat([])` is an empty buffer, `toString('utf8')` is `''`.

We check `if (raw)` before parsing. If the body is empty, we set `req.body = {}` so handlers can safely do `req.body.name` (which would be `undefined`).

## Why We Dispatch *Inside* the `'end'` Listener

The dispatch can't happen until we have the body. So the dispatch is inside the `'end'` handler:

```js
req.on('end', () => {
  // parse the body
  // then dispatch
});
```

This means the handler runs asynchronously, after the body is received. From the handler's perspective, `req.body` is already a real object.

This is the same pattern every framework uses. The handler doesn't know about streams; the framework handles the reading and parsing.

## The Order: Streams First, Then Dispatch

In our previous projects, the dispatch was synchronous:

```js
const server = http.createServer((req, res) => {
  const handler = routes.get(`${req.method} ${path}`);
  handler(req, res);
});
```

Now, it's async:

```js
const server = http.createServer((req, res) => {
  const chunks = [];
  req.on('data', (chunk) => chunks.push(chunk));
  req.on('end', () => {
    // dispatch
  });
});
```

The handler still looks the same. The framework (our dispatch) handles the async I/O.

## Common Confusions (read these)

**Confusion 1: "What if the body is huge?"**
We accumulate all chunks in an array, then concatenate. For a 10 GB body, that's 10 GB of memory. We can avoid this by processing chunks as they arrive (streaming), but for now, our bodies are small. We'll add a size limit in project 14.

**Confusion 2: "Why is the body a stream but the response is just a string?"**
The request body is a stream because the client is sending it incrementally (and we might not have the whole thing yet). The response body is also a stream, but we typically write it all at once with `res.end(string)`. For a streaming response, we'd use `res.write(chunk)` multiple times. We don't, because our responses are small.

**Confusion 3: "What if the client disconnects mid-body?"**
The `'error'` event fires on `req`. We could listen for it and clean up. We don't, because we haven't felt the pain yet. We'll add it in project 15 (Error Wall) or 25 (Cron).

**Confusion 4: "What if the body is not JSON?"**
`Content-Type: application/json` is what the client sends. If the client sends `Content-Type: text/plain` and the body is `hello`, we still try to JSON.parse and fail with 400. We should respect `Content-Type` and only parse if it's JSON. We do, by only setting `req.body` inside the `try` block. If `Content-Type` is not JSON, we'd want to handle it differently. We don't, because we don't have other content types yet. (We'll add `multipart/form-data` in project 20.)

**Confusion 5: "Why not use `req.text()` or `req.json()` like in newer APIs?"**
The `fetch` API in browsers has `.text()` and `.json()` methods on requests. Node's `IncomingMessage` (the type of `req`) doesn't have these out of the box (yet). We could add them as a helper:

```js
function readJson(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));
      } catch (err) {
        reject(err);
      }
    });
    req.on('error', reject);
  });
}
```

Then the handler would be `async (req, res) => { req.body = await readJson(req); ... }`. We don't, because async adds complexity. We use the synchronous-feeling approach (read in the dispatch, handler is sync). Project 07 (Framework Pivot) will use Express's `express.json()` middleware, which is more polished.

**Confusion 6: "What about Content-Length?"**
The `Content-Length` header tells you the size of the body in bytes. You could pre-allocate a buffer. We don't, because Node handles it for us. We just accumulate chunks.

**Confusion 7: "What if the body is a form (URL-encoded)?"**
`Content-Type: application/x-www-form-urlencoded`. The body is `name=Eve&role=admin`. We'd parse it with `URLSearchParams`, just like the query string. We don't handle this here. We'll add it when needed (probably in a frontend-related project).

**Confusion 8: "What's `Buffer`?"**
A `Buffer` is Node's class for raw bytes. It's a subclass of `Uint8Array`. You can convert it to a string with `buf.toString('utf8')` or to JSON with `buf.toString('utf8')` followed by `JSON.parse`. You create one with `Buffer.from(string)`.

## What We Are About to Build

A 70-line server that:

1. Has a `Map` of routes (from project 02)
2. Parses the query (from project 04)
3. **NEW**: Reads the body as a stream, concatenates chunks, parses as JSON
4. **NEW**: Handles invalid JSON with a 400
5. Dispatches to the handler with `req.body` populated

The new code is the `'data'`/`'end'` listener inside the dispatch. The handlers are unchanged in shape — they just have access to `req.body` now.

In [BUILD.md](./BUILD.md) we will go line by line.

# The Problem

> *"Query is in the URL. Body is in the payload. They are two halves of input."*

## Why the Body Exists

A `GET` request asks the server for data. The data the server returns is in the response body. The client doesn't send anything significant (just headers).

A `POST` request *creates* something. The client must send *data*: the user to create, the post to publish, the order to place. That data goes in the *request body*.

The URL (`/users`) identifies the resource. The body (`{"name": "Eve"}`) is the data the client is sending.

## What Pain Is This Solving?

In projects 02-04, our `POST /users` handler ignored the body entirely. The client could send:

```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Eve"}'
```

…and the server would respond `{"id": 4, "name": "Dave", "email": "dave@example.com"}` (a hardcoded user). The body was thrown away. The client had no way to actually *create* a user.

**The pain**: Real APIs accept input. To accept it, we need to *read* the request body.

## The Deeper Problem: The Body is a Stream

The body might be 0 bytes (for `GET`), 100 bytes (for a small JSON), or 10 GB (for a file upload). It might arrive in one chunk, or a hundred, or arrive slowly over a slow network.

We can't just say "give me the body" because it hasn't arrived yet. The client is still sending. We have to *wait* for it.

The way Node handles this is *streams*. A stream is an object that produces data in chunks. We listen for `'data'` events (each chunk) and an `'end'` event (the body is done). We accumulate the chunks, decode them, parse them, and use the result.

This is asynchronous. The dispatch can't just call the handler — it has to wait for the body first.

## What This Project Will Solve

This project will:

1. Listen for `'data'` events on `req` to collect chunks
2. Listen for the `'end'` event to know the body is done
3. Concatenate the chunks into a single buffer
4. Decode the buffer as UTF-8 text
5. Parse the text as JSON (since `Content-Type: application/json`)
6. Put the parsed object on `req.body`
7. Handle invalid JSON with a `400 Bad Request`
8. Only *after* the body is parsed, dispatch to the handler

By the end, `req.body` is a real JS object, and the handler can use it.

## What This Project Will *Not* Solve

- **Other content types** — we only parse `application/json`. We'll add `multipart/form-data` (for file uploads) in project 20 and `application/x-www-form-urlencoded` (for HTML forms) in a future project.
- **Streaming JSON** — for huge bodies, we'd parse the JSON as a stream (e.g., `JSONStream`). We don't, because we don't have huge bodies yet.
- **Size limits** — we accept any size body. A malicious client could send 10GB. We'll add a limit in project 14 (Validator) or 24 (Rate Limiter).
- **Validation** — we accept any JSON object. `{name: 123}` is accepted. We'll add validation in project 14.
- **Async handlers** — the handlers are still synchronous. We'll make them async when we have a real database (project 10+).

## The Question This Project Answers

> *"How do I read the data the client sent me?"*

If you can answer: "listen for `'data'` and `'end'` on `req`, concatenate chunks, parse as JSON, put on `req.body`," you are ready for project 06.

# The Problem

> *"Programs don't read English. They read JSON."*

## Why JSON?

In project 02, we returned `'Alice, Bob, Carol\n'`. A human reads this fine. A program can't:

- Is the separator a comma and a space? Or just a comma? Or a newline?
- Are there 3 users, or one user with a comma in their name?
- Is the list complete, or did the server truncate it?

A program needs *structure*. The list is `['Alice', 'Bob', 'Carol']` — a real array. Or better, `[{id: 1, name: 'Alice'}, {id: 2, name: 'Bob'}]` — a list of *objects* with multiple fields.

The format that gives us this is **JSON**.

## What Pain Is This Solving?

Imagine you are building a frontend. You fetch `/users` and get `'Alice, Bob, Carol\n'`. Now you need to display them in a table. You do:

```js
const text = await response.text();
const names = text.split(', '); // ['Alice', 'Bob', 'Carol\n']
```

But what if a user's name contains a comma? `"Smith, John"`. Now the split is wrong. What if the name contains a newline? What if there are 10,000 users? The string gets huge.

JSON solves this by being a *structured* format. A program parses it once and gets a real array of strings or objects. No string manipulation. No ambiguity.

```json
[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
```

This is unambiguous. A parser turns it into:

```js
[{id: 1, name: 'Alice'}, {id: 2, name: 'Bob'}]
```

A real array of real objects. The frontend can map, filter, sort — anything.

## The Deeper Problem: HTTP Is a String Protocol

HTTP only sends *bytes* over the wire. Those bytes can be interpreted as text, JSON, XML, HTML, binary, whatever. The server and the client must agree on the format.

The way they agree is the `Content-Type` header:

- `text/plain` — plain text (project 02)
- `application/json` — JSON
- `text/html` — HTML
- `application/octet-stream` — binary
- `multipart/form-data` — file uploads
- ...

The header doesn't change the *bytes*. It changes the *interpretation*. The same bytes might be valid JSON and valid plain text (just text that happens to be JSON-shaped). The header tells the client which interpretation to use.

In project 02 we sent `text/plain`. The client *could* parse the body as JSON, but it has no way to know that's the right thing to do. By sending `application/json`, we tell the client: "parse this as JSON." It does, and it gets a real JS object.

## What This Project Will Solve

This project will:

1. Introduce JSON as a string format
2. Show how to *serialize* a JS object to JSON with `JSON.stringify`
3. Show how to set the `Content-Type: application/json` header
4. Introduce a `json(res, status, body)` helper to avoid boilerplate
5. Use `201 Created` for `POST` that creates a resource (vs. `200 OK` for general success)

By the end, our API will speak the language of the modern web.

## What This Project Will *Not* Solve

- **Reading JSON bodies** — we can send JSON, but we still can't receive it. Project 05 (Body Parser) reads the request body.
- **Nested structures** — JSON supports nesting, but we don't use it heavily here. We will, in project 17 (REST Refactor) and beyond.
- **Streaming JSON** — for huge arrays, you'd stream JSON. We will discuss this in project 18 (Paginator) and project 51 (Streams).
- **Validation** — the JSON we send back is "obviously correct" because we made it. JSON we *receive* might be malformed or have the wrong shape. Project 14 (Validator) addresses this.
- **Error JSON shapes** — when a request fails, what's the right JSON shape? `{"error": "..."}` is common. We'll standardize in project 15 (Error Wall).

## The Question This Project Answers

> *"How do I send and accept structured data over HTTP?"*

If you can answer: "set `Content-Type: application/json`, use `JSON.stringify` to send, `JSON.parse` to receive," you are ready for project 04.

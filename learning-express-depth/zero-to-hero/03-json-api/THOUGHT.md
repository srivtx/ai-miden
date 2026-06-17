# The Thought

> *"JSON is a string. JavaScript objects are memory. `JSON.parse` and `JSON.stringify` are the bridge."*

## What JSON Actually Is

JSON stands for **JavaScript Object Notation**. It is a *string format* for representing structured data. The format looks like JavaScript object syntax, but it is not JavaScript — it is text.

Example JSON:

```json
{
  "name": "Alice",
  "age": 30,
  "isAdmin": false,
  "hobbies": ["reading", "hiking"],
  "address": {
    "street": "123 Main St",
    "city": "Springfield"
  }
}
```

Notice:

- Keys are **double-quoted strings**. Single quotes are not valid JSON.
- String values are **double-quoted**. `'Alice'` is not valid JSON; `"Alice"` is.
- Booleans are `true` and `false` (lowercase, not `True` or `TRUE`).
- `null` is the only null value (not `None` or `nil`).
- Numbers can be integer or floating-point.
- Arrays use square brackets `[]`.
- Objects use curly braces `{}`.

The full grammar fits on a postcard. This is one of JSON's strengths: it is simple enough that you can write a parser in an afternoon.

## JSON Is a Subset of JavaScript Object Syntax — Almost

JavaScript object literals and JSON look almost identical. The differences:

1. **Keys must be quoted** in JSON. In JS, you can write `{name: "Alice"}` (unquoted key, valid JS). In JSON, you must write `{"name": "Alice"}`.
2. **Strings must use double quotes** in JSON. In JS, you can use single quotes: `{name: 'Alice'}`. In JSON, that's invalid.
3. **No trailing commas** in JSON. `{a: 1,}` is valid JS but invalid JSON.
4. **No functions, no `undefined`, no `Date` objects, no `Map`, no `Set`**, etc. JSON is data only.

So JSON is a *restricted* version of JS object syntax. Anything that is valid JSON is also valid JS. The reverse is not true.

## The Bridge: `JSON.stringify` and `JSON.parse`

Two functions convert between JS values and JSON strings.

### `JSON.stringify(value)`

Takes a JS value (object, array, string, number, boolean, null) and returns a JSON string.

```js
JSON.stringify({name: 'Alice', age: 30});
// '{"name":"Alice","age":30}'

JSON.stringify([1, 2, 3]);
// '[1,2,3]'

JSON.stringify('hello');
// '"hello"'
```

Things to know:

- `undefined`, functions, and symbols are *omitted* (not converted to `null`):

  ```js
  JSON.stringify({a: 1, b: undefined, c: () => {}});
  // '{"a":1}'
  ```

- `NaN` and `Infinity` become `null`:

  ```js
  JSON.stringify(NaN); // 'null'
  JSON.stringify(Infinity); // 'null'
  ```

- `Date` objects become ISO strings:

  ```js
  JSON.stringify(new Date()); // '"2024-01-15T10:30:00.000Z"'
  ```

- The second argument is a *replacer* (filter or transform). We won't use it here.
- The third argument is *indentation* for pretty-printing. `JSON.stringify(obj, null, 2)` makes it readable.

### `JSON.parse(string)`

Takes a JSON string and returns a JS value.

```js
JSON.parse('{"name":"Alice","age":30}');
// {name: 'Alice', age: 30}

JSON.parse('[1,2,3]');
// [1, 2, 3]

JSON.parse('"hello"');
// 'hello'
```

Things to know:

- It throws on invalid JSON. We'll catch this in project 15 (Error Wall).
- The second argument is a *reviver* (transform). We won't use it here.

## Content-Type: `application/json`

The MIME type for JSON is `application/json`. This tells the client: "the body is JSON, parse it."

`Content-Type` is a *contract*. If we send `application/json` but the body is `<html>`, the client will try to parse `<html>` as JSON, fail, and return an error to the user. We must be honest.

The reverse is also true: if we send `text/plain` but the body is JSON, the client won't know to parse it. It will just display the JSON as a string (literally: `{"name":"Alice"}`).

The convention is strict: the `Content-Type` header must match the body format.

## The `json(res, status, body)` Helper

Sending JSON is three steps every time:

1. Set the status code
2. Set the `Content-Type` header
3. Stringify and send the body

If we did this in every handler, we'd have 3 lines of boilerplate per response. A helper reduces it to one line.

```js
function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(body));
}
```

Now every handler is:

```js
get('/users', (req, res) => {
  json(res, 200, [{id: 1, name: 'Alice'}]);
});
```

One line. Express's `res.json(body)` does the same thing (and defaults to status 200 if you don't pass it).

## Why `201 Created` for `POST`?

When a `POST` request *creates* a resource, the convention is to return `201 Created` (not `200 OK`). The difference:

- `200 OK` — generic success. Used for `GET`, `PUT`, `PATCH`, and for `POST` that don't create (e.g., `POST /login` returns a token, not a created user).
- `201 Created` — specifically for `POST` (or `PUT`) that *created a new resource*. The response should include the new resource (so the client knows its id, etc.).
- `204 No Content` — used for `DELETE` that succeeded, with no body.

This is a small detail, but it is the kind of detail that makes an API feel professional. The status code is part of the protocol. Using it correctly is a sign of care.

## Common Confusions (read these — they will save you hours)

**Confusion 1: "JSON is the same as JavaScript objects, right?"**
No. JSON is a *string*. A JS object is a *memory structure*. They look similar but are different things. `JSON.parse` and `JSON.stringify` are the bridge.

**Confusion 2: "Can I send functions in JSON?"**
No. JSON is data only. No functions, no `undefined`, no `Date` objects (well, `Date` becomes a string), no `Map`, no `Set`. If you need to send behavior, send a string and interpret it on the client.

**Confusion 3: "What if my object has a circular reference?"**
`JSON.stringify` throws. Circular references are common in graph-like data structures. We'll address this in project 17 (REST Refactor) when we deal with user → posts → comments → user cycles.

**Confusion 4: "What if my object has a `toJSON` method?"**
`JSON.stringify` calls it. So if you have a class with a `toJSON()` method, you can control how it serializes. We don't need this yet.

**Confusion 5: "Why is there a `null` in JSON but no `undefined`?"**
`undefined` is a JS-only concept. It means "this property doesn't exist." In JSON, the equivalent is to *omit* the property, or use `null` for "this property exists but has no value." `JSON.stringify` omits `undefined` properties; you can't represent them explicitly.

**Confusion 6: "Can JSON have comments?"**
No. JSON is intentionally minimal. If you want comments, use JSON5, YAML, or TOML. But for APIs, plain JSON is the standard.

**Confusion 7: "What's the difference between `application/json` and `text/json`?"**
`text/json` is technically valid but obsolete. Use `application/json` always. Browsers and clients know to parse `application/json`; some may not handle `text/json`.

## What We Are About to Build

A 60-line server that:

1. Uses a `Map` of routes (from project 02)
2. Has a `json(res, status, body)` helper
3. Returns JSON for all responses
4. Uses `201 Created` for `POST` that creates
5. Returns `404` as JSON for unmatched routes

That's it. The router logic is unchanged. The handlers now return structured data. The 404 fallback is also JSON.

In [BUILD.md](./BUILD.md) we will go line by line.

# The Thought

> *"Path is the noun. Query is the modifier. `URLSearchParams` is the parser."*

## The Anatomy of a URL

A URL has seven parts:

```
scheme://user:password@host:port/path?query#fragment
https://alice:hunter2@example.com:8080/users?role=admin&limit=10#top
```

For our purposes, the relevant parts are:

- **path**: `/users` — identifies the resource
- **query**: `role=admin&limit=10` — modifies the request (filter, sort, paginate)
- **fragment**: `top` — used by the browser, never sent to the server

The `path` is what we route on. The `query` is what we filter on. The `fragment` is invisible to the server.

## How to Split Path from Query

The query is always separated from the path by `?`. So:

```js
const url = '/users?role=admin&limit=10';
const [path, queryString] = url.split('?');
// path: '/users'
// queryString: 'role=admin&limit=10'
```

If there is no `?`, `queryString` is `undefined`:

```js
const url = '/users';
const [path, queryString] = url.split('?');
// path: '/users'
// queryString: undefined
```

We use `queryString || ''` to handle the no-query case.

## How to Parse the Query String

The query is a series of `key=value` pairs separated by `&`. So:

```
role=admin&limit=10
```

becomes:

```js
{
  role: 'admin',
  limit: '10',
}
```

We could write a parser. It would be ~10 lines. But Node ships with `URLSearchParams`, a standard library class for exactly this. We use it.

### `URLSearchParams`

`new URLSearchParams(string)` creates a parser. It has methods to extract key-value pairs:

```js
const params = new URLSearchParams('role=admin&limit=10');
params.get('role');     // 'admin'
params.get('limit');    // '10'
params.has('role');     // true
params.getAll('tag');   // ['a', 'b'] (for ?tag=a&tag=b)
[...params.entries()];  // [['role', 'admin'], ['limit', '10']]
[...params.keys()];     // ['role', 'limit']
```

The values are *always strings*. `limit=10` becomes `'10'`, not `10`. If you need a number, parse it: `Number(params.get('limit'))` or `parseInt(params.get('limit'), 10)`.

### Convert to a Plain Object

`URLSearchParams` is iterable, but most code wants a plain object `{ role: 'admin', limit: '10' }`. We use `Object.fromEntries`:

```js
const params = new URLSearchParams('role=admin&limit=10');
const query = Object.fromEntries(params);
// query: { role: 'admin', limit: '10' }
```

This is a one-liner that does the conversion.

### Multi-Value Query

`URLSearchParams` supports multi-value: `?tag=a&tag=b` becomes `{ tag: ['a', 'b'] }`. But `Object.fromEntries` only takes the *last* value:

```js
const params = new URLSearchParams('tag=a&tag=b');
Object.fromEntries(params);
// { tag: 'b' }  // 'a' is lost
```

If you need all values, iterate manually:

```js
const query = {};
for (const [key, value] of new URLSearchParams(queryString)) {
  if (query[key] === undefined) {
    query[key] = value;
  } else if (Array.isArray(query[key])) {
    query[key].push(value);
  } else {
    query[key] = [query[key], value];
  }
}
```

This is more code. We don't need multi-value yet. We use the simple form. We'll revisit in project 18 (Paginator) or 19 (Searcher) if needed.

## URL Encoding

Some characters can't be in a URL raw. Spaces become `%20` (or `+`). `&` and `=` are reserved for query syntax. `URLSearchParams` handles all of this:

- `?name=Alice%20Smith` → `{ name: 'Alice Smith' }`
- `?greeting=hello%20world` → `{ greeting: 'hello world' }`
- `?email=alice%40example.com` → `{ email: 'alice@example.com' }`

This is called *URL encoding* or *percent encoding*. `URLSearchParams` decodes for you. If you wrote a parser by hand, you'd have to handle this. Another reason to use the standard library.

## Why We Strip the Query Before the Lookup

The route key is `METHOD path`. The path is the *resource*. The query is *not* part of the resource. So:

- Route on `path`
- Read the query separately

If we routed on the full URL, then `GET /users` and `GET /users?role=admin` would be different routes. That's wrong. They are the *same* route with *different filters*.

The convention is universal. Every router in every framework does this. We do it too.

## Common Confusions (read these)

**Confusion 1: "What's the difference between a query string and a body?"**
The query string is in the URL. It's for `GET` requests (read-only). The body is sent after the headers. It's for `POST`, `PUT`, `PATCH` (writes).

```
GET /users?role=admin        # query
POST /users  body: {name:..} # body
```

Mixing them is allowed but not recommended: `GET` with a body is technically valid but most clients don't support it well.

**Confusion 2: "Can the query have nested objects?"**
Not in the standard. `?user[name]=Alice` is a *convention* (PHP/Rails style) but not a standard. Most APIs use flat keys: `?user_name=Alice&user_id=42`. We use flat keys.

**Confusion 3: "What if the same key appears twice?"**
`?tag=a&tag=b`. The convention is "the last value wins" (with `Object.fromEntries`) or "all values as an array" (with manual iteration). We use the simple form. We'll revisit if needed.

**Confusion 4: "What about empty values?"**
`?role=&limit=10`. The empty value is an empty string. We don't treat it specially. If the client wanted "no role filter," they'd omit the key.

**Confusion 5: "Why not just pass the raw query string to the handler?"**
Because the handler would have to parse it every time. The convention is to parse once, in the framework, and give the handler a clean object. The handler can focus on *business logic* (filter, sort, paginate) instead of *parsing*.

**Confusion 6: "Why `URLSearchParams` and not `querystring` (the legacy module)?"**
`querystring` is a Node built-in but legacy. `URLSearchParams` is the standard, available in Node and the browser, and has a cleaner API. We use `URLSearchParams`.

**Confusion 7: "What if I want to use `req.url` later?"**
We don't modify `req.url`. We add `req.query` and `req.path`. The original `req.url` is still there. Some frameworks (Express) also add `req.path` (the URL without the query). We add `req.query` only.

## What We Are About to Build

A 65-line server that:

1. Splits `req.url` into `path` and `queryString` in the dispatch
2. Looks up the route by `METHOD path` (not the full URL)
3. Parses the query with `URLSearchParams` and puts it on `req.query`
4. The handler reads `req.query.role` and filters accordingly

The handlers that *use* the query are the new addition. The router code is one extra line.

In [BUILD.md](./BUILD.md) we will go line by line.

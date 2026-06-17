# 57 — CORS

**New concept:** cross-origin resource sharing.

By default, browsers block JavaScript from site A (e.g. `localhost:3001`) from calling site B (e.g. `localhost:3000`). This is a security feature called **same-origin policy**.

CORS is a way for site B to say "actually, I want site A to be able to call me." It uses special headers.

## Run it

```bash
npm install
node server.js
```

```bash
# Make a request with Origin header
curl -i -H "Origin: http://localhost:3001" http://localhost:3000/api/data
# HTTP/1.1 200 OK
# Access-Control-Allow-Origin: http://localhost:3001
# Vary: Origin
# ...

# Preflight (browser sends OPTIONS before non-simple requests)
curl -i -X OPTIONS -H "Origin: http://localhost:3001" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  http://localhost:3000/api/data
# HTTP/1.1 204 No Content
# Access-Control-Allow-Origin: http://localhost:3001
# Access-Control-Allow-Methods: GET, POST, ...
```

## How to think about it

CORS is like a guest list. By default, only people from the same building (origin) can come in. CORS is a way to say "actually, people from building B are also welcome."

## How to build it (line by line)

```js
res.set('Access-Control-Allow-Origin', origin);
```

**Line 12.** Tell the browser "this origin is allowed."

**`Access-Control-Allow-Origin`** is the main CORS header. It can be `*` (anyone) or a specific origin.

**We don't use `*` here** because we want to control who can call us. We list allowed origins.

```js
if (req.method === 'OPTIONS') {
  return res.status(204).end();
}
```

**Lines 22-24.** Handle the preflight request. Browsers send an OPTIONS request before non-simple requests (POST, custom headers, etc.) to ask "is this OK?"

**We respond with 204** and the right headers. Then the browser sends the real request.

## What we learned

1. Same-origin policy: browsers block cross-origin requests by default
2. CORS headers: `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, etc.
3. Preflight: browsers send OPTIONS before non-simple requests
4. We control who can call us via the `ALLOWED_ORIGINS` list
5. The `cors` npm package does all this for you (we built it manually here)
6. Never use `Access-Control-Allow-Origin: *` with credentials

## What's next

In **58-helmet** we use Helmet, a package that sets many security headers at once.

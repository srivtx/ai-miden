## Why it exists (THE PROBLEM)

Python's FastAPI is excellent for ML model serving. But 70% of production backends run on Node.js/Express. When you join a company, the ML model lives in Python, but the API that serves it — authentication, rate limiting, caching, user management, payment handling — lives in Express. You need to speak both languages.

Express is the most popular Node.js framework. It's minimal (15KB), unopinionated (you choose the database, auth, ORM), and has the largest ecosystem of middleware. Every AI/ML engineer who deploys models to production touches Express at some point — either building the API themselves or integrating their Python model with an existing Express backend.

## Definition

**Express** = a request-response framework. You define routes (`app.get('/users', handler)`), attach middleware (functions that run before the handler), and return responses. That's it. Everything else — database, auth, validation, logging — is middleware you add.

## Project: Basic Express API

```javascript
// projects/express_api/basic/server.js
const express = require('express');
const app = express();

// 1. Built-in middleware
app.use(express.json());  // parse JSON bodies
app.use(express.urlencoded({ extended: true }));  // parse form data

// 2. Custom logging middleware
app.use((req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
        const ms = Date.now() - start;
        console.log(`${req.method} ${req.originalUrl} ${res.statusCode} ${ms}ms`);
    });
    next();
});

// 3. Routes — the core of Express
app.get('/health', (req, res) => {
    res.json({ status: 'ok', uptime: process.uptime() });
});

app.post('/echo', (req, res) => {
    const { message } = req.body;
    res.json({ echo: message, received: new Date().toISOString() });
});

// 4. Route parameters and query strings
app.get('/users/:id', (req, res) => {
    const userId = req.params.id;       // /users/42 -> "42"
    const include = req.query.include;   // /users/42?include=posts -> "posts"
    res.json({ id: userId, include });
});

// 5. Error handling middleware (4 args = error handler)
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Internal server error' });
});

// 6. 404 handler (must be last)
app.use((req, res) => {
    res.status(404).json({ error: 'Not found' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
```

**Run:** `node server.js` → `curl http://localhost:3000/health`

## Key Express concepts

| Concept | What it is | Why it matters |
|---|---|---|
| **Middleware** | Functions that run in order: `(req, res, next)` | Auth, logging, parsing, rate limiting — all middleware |
| **Route** | URL pattern + HTTP method + handler | `app.get('/path', handler)` |
| **Request** | `req.params` (URL segments), `req.query` (?key=val), `req.body` (POST data), `req.headers` | All input comes through the request object |
| **Response** | `res.json()`, `res.status()`, `res.send()`, `res.redirect()` | All output goes through the response object |
| **Error handling** | 4-argument middleware: `(err, req, res, next)` | Express routing skips normal handlers and jumps to error handler |
| **Static files** | `express.static('public')` | Serve HTML, CSS, JS, images |

## Express vs FastAPI (Python)

Both are request-response frameworks. The patterns are identical — only the syntax differs.

| Pattern | Express | FastAPI |
|---|---|---|
| Route definition | `app.get('/path', handler)` | `@app.get('/path')` |
| Path params | `req.params.id` | `path: str` (function arg) |
| Query params | `req.query.key` | `key: str = None` (function arg) |
| JSON body | `express.json()` middleware → `req.body` | Pydantic model → function arg |
| Middleware | `app.use(fn)` | `@app.middleware` or `add_middleware` |
| Error handling | `(err, req, res, next)` | `@app.exception_handler` |
| Async | Callbacks or `async/await` | Native `async def` |
| Type checking | None (JavaScript) | Pydantic (automatic) |

## Common confusion

1. **"Express is synchronous — it can't handle ML inference."** Express handlers can be `async`. Use `async (req, res) => { await model.predict(); res.json(result); }`. The event loop is non-blocking.

2. **"Express is just for websites."** Express is a minimal HTTP framework. It's used for: REST APIs (GitHub, Uber), real-time apps (Socket.io on Express), microservices, and API gateways. Same role as FastAPI in Python.

3. **"Node.js is single-threaded, so it can't do ML."** The ML computation happens in Python (separate process, GPU). Express handles: auth, routing, request validation, caching, rate limiting — all lightweight I/O. Python handles: model inference — heavy compute. Express + Python child process = production ML architecture.

## Connection to our projects

**cortexcode:** The FastAPI server in `cortexcode_api.py` can be replaced with Express. The model runs in Python (separate process), Express handles: auth, rate limiting, caching, and proxying requests to the Python model server. This is the standard pattern: Express as API gateway, Python as ML worker.

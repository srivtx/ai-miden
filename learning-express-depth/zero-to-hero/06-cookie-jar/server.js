// server.js
//
// Project 06: The Cookie Jar
// ==========================
// Adds cookie and session support. The server can now recognize
// returning users via a session ID stored in a cookie.
//
// To run:   node server.js
// To test:
//   curl -X POST http://localhost:3000/login \
//     -H "Content-Type: application/json" \
//     -d '{"username": "alice"}' \
//     -c cookies.txt
//   curl http://localhost:3000/me -b cookies.txt

const http = require('node:http');

const routes = new Map();

function get(path, handler) {
  routes.set(`GET ${path}`, handler);
}

function post(path, handler) {
  routes.set(`POST ${path}`, handler);
}

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(body));
}

function setCookie(res, name, value) {
  res.setHeader('Set-Cookie', `${name}=${value}; HttpOnly; Path=/`);
}

function parseCookies(header) {
  const cookies = {};
  if (!header) return cookies;
  for (const pair of header.split(';')) {
    const [name, ...rest] = pair.trim().split('=');
    cookies[name] = rest.join('=');
  }
  return cookies;
}

const SESSIONS = new Map();
let nextSessionId = 1;

get('/', (req, res) => {
  json(res, 200, { message: 'Welcome to the API.' });
});

get('/health', (req, res) => {
  json(res, 200, { status: 'ok' });
});

post('/login', (req, res) => {
  const sessionId = String(nextSessionId++);
  SESSIONS.set(sessionId, { username: req.body.username, createdAt: Date.now() });
  setCookie(res, 'sessionId', sessionId);
  json(res, 200, { sessionId, username: req.body.username });
});

get('/me', (req, res) => {
  const session = SESSIONS.get(req.cookies.sessionId);
  if (!session) {
    json(res, 401, { error: 'Not authenticated' });
    return;
  }
  json(res, 200, session);
});

const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split('?');
  req.query = Object.fromEntries(new URLSearchParams(queryString || ''));
  req.cookies = parseCookies(req.headers.cookie);

  const chunks = [];
  req.on('data', (chunk) => chunks.push(chunk));
  req.on('end', () => {
    const raw = Buffer.concat(chunks).toString('utf8');
    if (raw) {
      try {
        req.body = JSON.parse(raw);
      } catch (err) {
        json(res, 400, { error: 'Invalid JSON' });
        return;
      }
    } else {
      req.body = {};
    }

    const handler = routes.get(`${req.method} ${path}`);
    if (!handler) {
      json(res, 404, { error: 'Not Found' });
      return;
    }
    handler(req, res);
  });
});

server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});

// server.js
//
// Project 05: The Body Parser
// ===========================
// Reads the request body as a stream, concatenates chunks, parses as JSON,
// and puts the result on req.body. The dispatch is now async — it waits
// for the body to arrive before dispatching to the handler.
//
// To run:   node server.js
// To test:  curl -X POST http://localhost:3000/users \
//            -H "Content-Type: application/json" \
//            -d '{"name": "Eve"}'

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

const USERS = [
  { id: 1, name: 'Alice', role: 'admin' },
  { id: 2, name: 'Bob', role: 'user' },
];

get('/', (req, res) => {
  json(res, 200, { message: 'Welcome to the API.' });
});

get('/users', (req, res) => {
  json(res, 200, USERS);
});

post('/users', (req, res) => {
  const user = {
    id: USERS.length + 1,
    name: req.body.name,
    role: req.body.role || 'user',
  };
  USERS.push(user);
  json(res, 201, user);
});

get('/health', (req, res) => {
  json(res, 200, { status: 'ok' });
});

const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split('?');
  req.query = Object.fromEntries(new URLSearchParams(queryString || ''));

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

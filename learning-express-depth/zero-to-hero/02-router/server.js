// server.js
//
// Project 02: The Router
// =======================
// A 50-line HTTP server with a Map-based router.
// Same shape as Express's app.get / app.post, but built by hand.
//
// To run:   node server.js
// To test:  curl http://localhost:3000/users
//           curl -X POST http://localhost:3000/users

const http = require('node:http');

const routes = new Map();

function get(path, handler) {
  routes.set(`GET ${path}`, handler);
}

function post(path, handler) {
  routes.set(`POST ${path}`, handler);
}

get('/', (req, res) => {
  res.end('Welcome to the API.\n');
});

get('/users', (req, res) => {
  res.end('Alice, Bob, Carol\n');
});

post('/users', (req, res) => {
  res.end('User created.\n');
});

get('/health', (req, res) => {
  res.end('OK\n');
});

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'text/plain');
  const handler = routes.get(`${req.method} ${req.url}`);
  if (!handler) {
    res.statusCode = 404;
    res.end('Not Found\n');
    return;
  }
  handler(req, res);
});

server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});

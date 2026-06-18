// server.js
//
// Project 04: The Query-String Reader
// ===================================
// Adds query string support. The router matches the path; the query
// is parsed once in the dispatch and put on req.query.
//
// To run:   node server.js
// To test:  curl 'http://localhost:3000/users?role=admin'

const http = require("node:http");

const routes = new Map();

function get(path, handler) {
  routes.set(`GET ${path}`, handler);
}

function post(path, handler) {
  routes.set(`POST ${path}`, handler);
}

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(body));
}

const USERS = [
  { id: 1, name: "Alice", role: "admin" },
  { id: 2, name: "Bob", role: "user" },
  { id: 3, name: "Carol", role: "admin" },
  { id: 4, name: "Dave", role: "user" },
];

get("/", (req, res) => {
  json(res, 200, { message: "Welcome to the API." });
});

get("/users", (req, res) => {
  let users = USERS;
  if (req.query.role) {
    users = users.filter((u) => u.role === req.query.role);
  }
  json(res, 200, users);
});

get("/health", (req, res) => {
  json(res, 200, { status: "ok" });
});

const server = http.createServer((req, res) => {
  const [path, queryString] = req.url.split("?");
  req.query = Object.fromEntries(new URLSearchParams(queryString || ""));
  const handler = routes.get(`${req.method} ${path}`);
  if (!handler) {
    json(res, 404, { error: "Not Found" });
    return;
  }
  handler(req, res);
});

server.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});

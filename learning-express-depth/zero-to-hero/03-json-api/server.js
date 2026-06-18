// server.js
//
// Project 03: The JSON API
// ========================
// A 60-line HTTP server that speaks JSON for every response.
// The router is unchanged from project 02. The handlers now return
// structured data via a `json(res, status, body)` helper.
//
// To run:   node server.js
// To test:  curl http://localhost:3000/users
//           curl -X POST http://localhost:3000/users

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

get("/", (req, res) => {
  json(res, 200, { message: "Welcome to the API." });
});

get("/users", (req, res) => {
  json(res, 200, [
    { id: 1, name: "Alice" },
    { id: 2, name: "Bob" },
    { id: 3, name: "Carol" },
  ]);
});

get("/users/1", (req, res) => {
  json(res, 200, { id: 1, name: "Alice", email: "alice@example.com" });
});

post("/users", (req, res) => {
  json(res, 201, { id: 4, name: "Dave", email: "dave@example.com" });
});

get("/health", (req, res) => {
  json(res, 200, { status: "ok" });
});

const server = http.createServer((req, res) => {
  const handler = routes.get(`${req.method} ${req.url}`);
  if (!handler) {
    json(res, 404, { error: "Not Found" });
    return;
  }
  handler(req, res);
});

server.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});

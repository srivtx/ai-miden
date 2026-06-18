// server.js
//
// Project 01: The Echo Server
// =============================
// A 30-line HTTP server with no framework, no dependencies, no magic.
// This is the foundation. Every framework in existence does
// approximately what this file does, just with more features.
//
// To run:   node server.js
// To test:  curl http://localhost:3000

const http = require("node:http");

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "text/plain");
  res.end("Hello, world.\n");
});

server.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});

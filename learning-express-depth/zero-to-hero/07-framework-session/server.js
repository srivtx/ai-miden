// server.js
//
// Project 07: The Framework Pivot + Session
// =========================================
// Adopts Express. Replaces our hand-rolled dispatch with Express middleware.
// Uses express.json() (body parsing), cookie-parser (cookies), express-session
// (sessions). The handlers stay the same shape: (req, res) => { ... }.
//
// Setup:
//   npm init -y
//   npm install express cookie-parser express-session
//   node server.js
//
// Test:
//   curl -X POST http://localhost:3000/login \
//     -H "Content-Type: application/json" \
//     -d '{"username": "alice"}' \
//     -c cookies.txt
//   curl http://localhost:3000/me -b cookies.txt

const express = require("express");
const cookieParser = require("cookie-parser");
const session = require("express-session");

const app = express();

app.use(express.json());
app.use(cookieParser());
app.use(
  session({
    secret: "dev-secret-change-in-prod",
    resave: false,
    saveUninitialized: false,
  }),
);

app.get("/", (req, res) => {
  res.json({ message: "Welcome to the API." });
});

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.post("/login", (req, res) => {
  if (!req.body.username) {
    return res.status(400).json({ error: "username required" });
  }
  req.session.username = req.body.username;
  req.session.createdAt = Date.now();
  res.json({ username: req.session.username });
});

app.get("/me", (req, res) => {
  if (!req.session.username) {
    return res.status(401).json({ error: "Not authenticated" });
  }
  res.json({
    username: req.session.username,
    createdAt: req.session.createdAt,
  });
});

app.post("/logout", (req, res) => {
  req.session.destroy(() => {
    res.json({ message: "Logged out" });
  });
});

app.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});

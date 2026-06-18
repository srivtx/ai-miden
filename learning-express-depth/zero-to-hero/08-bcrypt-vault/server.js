// server.js
//
// Project 08: The Bcrypt Vault
// =============================
// Real authentication with bcrypt. Users sign up with a password
// (hashed and stored). Users log in with a password (compared to the
// stored hash). The plaintext password is never stored.
//
// Setup:
//   npm install bcrypt
//   node server.js
//
// Test:
//   curl -X POST http://localhost:3000/signup \
//     -H "Content-Type: application/json" \
//     -d '{"username":"alice","password":"hunter2"}'
//   curl -X POST http://localhost:3000/login \
//     -H "Content-Type: application/json" \
//     -d '{"username":"alice","password":"hunter2"}' \
//     -c cookies.txt

const express = require("express");
const cookieParser = require("cookie-parser");
const session = require("express-session");
const bcrypt = require("bcrypt");

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

const USERS = new Map();

app.get("/", (req, res) => {
  res.json({ message: "Welcome to the API." });
});

app.post("/signup", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "username and password required" });
  }
  if (USERS.has(username)) {
    return res.status(409).json({ error: "username already taken" });
  }
  const hash = await bcrypt.hash(password, 10);
  USERS.set(username, { username, hash, createdAt: Date.now() });
  res.status(201).json({ username });
});

app.post("/login", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "username and password required" });
  }
  const user = USERS.get(username);
  if (!user) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  const ok = await bcrypt.compare(password, user.hash);
  if (!ok) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  req.session.username = user.username;
  req.session.userId = user.username;
  res.json({ username: user.username });
});

app.get("/me", (req, res) => {
  if (!req.session.username) {
    return res.status(401).json({ error: "Not authenticated" });
  }
  res.json({ username: req.session.username });
});

app.post("/logout", (req, res) => {
  req.session.destroy(() => {
    res.json({ message: "Logged out" });
  });
});

app.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});

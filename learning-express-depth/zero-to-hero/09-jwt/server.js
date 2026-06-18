// server.js
//
// Project 09: The JWT
// ===================
// Replaces sessions with stateless JWT. Login issues a signed token.
// Protected routes use authMiddleware to verify the token.
// The server has zero session state.
//
// Setup:
//   npm install jsonwebtoken
//   node server.js
//
// Test:
//   TOKEN=$(curl -X POST http://localhost:3000/login \
//     -H "Content-Type: application/json" \
//     -d '{"username":"alice","password":"hunter2"}' \
//     | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
//   curl http://localhost:3000/me -H "Authorization: Bearer $TOKEN"

const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");

const SECRET = "dev-secret-change-in-prod";
const TOKEN_TTL = "7d";

const app = express();
app.use(express.json());

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
  const token = jwt.sign(
    { userId: user.username, username: user.username },
    SECRET,
    { expiresIn: TOKEN_TTL },
  );
  res.json({ token, username: user.username });
});

function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith("Bearer ")) {
    return res
      .status(401)
      .json({ error: "missing or invalid authorization header" });
  }
  const token = auth.slice(7);
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: "invalid or expired token" });
  }
}

app.get("/me", authMiddleware, (req, res) => {
  res.json({ user: req.user });
});

app.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});

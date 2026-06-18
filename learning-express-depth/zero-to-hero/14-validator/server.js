// server.js
//
// Project 14: The Validator
// ==========================
// Adds Zod schema validation. Bad input is rejected with 400 and
// structured errors. Good input is normalized. Handlers use req.validated.
//
// Setup:
//   npm install knex better-sqlite3 zod
//   node server.js

const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const knex = require("knex");
const { z } = require("zod");

const SECRET = "dev-secret-change-in-prod";
const TOKEN_TTL = "7d";

const app = express();
app.use(express.json());

const db = knex({
  client: "better-sqlite3",
  connection: { filename: "app.db" },
  useNullAsDefault: true,
});

async function migrate() {
  await db.schema.createTableIfNotExists("users", (t) => {
    t.increments("id").primary();
    t.string("username").unique().notNullable();
    t.string("hash").notNullable();
    t.string("email").unique();
    t.bigInteger("created_at").notNullable();
  });

  await db.schema.createTableIfNotExists("posts", (t) => {
    t.increments("id").primary();
    t.integer("user_id")
      .notNullable()
      .references("id")
      .inTable("users")
      .onDelete("CASCADE");
    t.string("title").notNullable();
    t.text("body").notNullable();
    t.bigInteger("created_at").notNullable();
  });
}

migrate().then(() => {
  app.listen(3000, () =>
    console.log("Server listening on http://localhost:3000"),
  );
});

const signupSchema = z.object({
  username: z
    .string()
    .min(3)
    .max(30)
    .regex(/^[a-zA-Z0-9_]+$/),
  password: z.string().min(8).max(100),
  email: z.string().email().optional(),
});

const loginSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

const postSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1).max(10000),
});

function validate(schema) {
  return (req, res, next) => {
    try {
      req.validated = schema.parse(req.body);
      next();
    } catch (err) {
      if (err.issues) {
        return res.status(400).json({
          error: "Validation failed",
          issues: err.issues.map((i) => ({
            path: i.path.join("."),
            message: i.message,
          })),
        });
      }
      next(err);
    }
  };
}

app.get("/", (req, res) => {
  res.json({ message: "Welcome to the API." });
});

app.post("/signup", validate(signupSchema), async (req, res) => {
  const { username, password, email } = req.validated;
  const existing = await db("users").where({ username }).first();
  if (existing) {
    return res.status(409).json({ error: "username already taken" });
  }
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db("users").insert({
    username,
    hash,
    email: email || null,
    created_at: Date.now(),
  });
  res.status(201).json({ id, username, email: email || null });
});

app.post("/login", validate(loginSchema), async (req, res) => {
  const { username, password } = req.validated;
  const user = await db("users").where({ username }).first();
  if (!user) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  const ok = await bcrypt.compare(password, user.hash);
  if (!ok) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  const token = jwt.sign({ userId: user.id, username: user.username }, SECRET, {
    expiresIn: TOKEN_TTL,
  });
  res.json({
    token,
    user: { id: user.id, username: user.username, email: user.email },
  });
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

app.post("/posts", authMiddleware, validate(postSchema), async (req, res) => {
  const { title, body } = req.validated;
  const [id] = await db("posts").insert({
    user_id: req.user.userId,
    title,
    body,
    created_at: Date.now(),
  });
  res.status(201).json({ id, userId: req.user.userId, title, body });
});

app.get("/posts", async (req, res) => {
  const posts = await db("posts")
    .join("users", "posts.user_id", "users.id")
    .select("posts.*", "users.username as author")
    .orderBy("posts.created_at", "desc");
  res.json(posts);
});

app.get("/posts/:id", async (req, res) => {
  const post = await db("posts")
    .join("users", "posts.user_id", "users.id")
    .select("posts.*", "users.username as author")
    .where("posts.id", req.params.id)
    .first();
  if (!post) {
    return res.status(404).json({ error: "Not Found" });
  }
  res.json(post);
});

app.get("/users/:id/posts", async (req, res) => {
  const posts = await db("posts")
    .where({ user_id: req.params.id })
    .orderBy("created_at", "desc");
  res.json(posts);
});

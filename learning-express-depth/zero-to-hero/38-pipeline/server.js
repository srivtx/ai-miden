// server.js
//
// Project 38: The Pipeline
// =========================
// GitHub Actions CI/CD. Same app as 37. Added .github/workflows/ci.yml and
// .github/workflows/cd.yml. CI runs on every push/PR: lint + test + build.
// CD runs on merge to main: docker build + push to ghcr.io + SSH deploy.
//
// Setup:
//   mkdir -p .github/workflows
//   # write ci.yml and cd.yml
//   git push origin main   # triggers CI
//   git merge feature       # triggers CD on merge to main

const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const knex = require("knex");
const { z } = require("zod");
const pino = require("pino");
const crypto = require("node:crypto");

const SECRET = "dev-secret-change-in-prod";
const TOKEN_TTL = "7d";

const logger = pino({ level: process.env.LOG_LEVEL || "info" });

const db = knex(
  process.env.DATABASE_URL
    ? { client: "better-sqlite3", connection: process.env.DATABASE_URL, useNullAsDefault: true }
    : { client: "better-sqlite3", connection: { filename: "/data/app.db" }, useNullAsDefault: true }
);

async function migrate() {
  await db.schema.createTableIfNotExists("users", (t) => {
    t.increments("id").primary();
    t.string("username").unique().notNullable();
    t.string("hash").notNullable();
    t.bigInteger("created_at").notNullable();
  });
  await db.schema.createTableIfNotExists("posts", (t) => {
    t.increments("id").primary();
    t.integer("user_id").notNullable().references("id").inTable("users");
    t.string("title").notNullable();
    t.text("body").notNullable();
    t.bigInteger("created_at").notNullable();
  });
}

class HttpError extends Error {
  constructor(s, c, m) { super(m); this.status = s; this.code = c; }
}
class ValidationError extends HttpError {
  constructor(i) { super(400, "VALIDATION", "Validation failed"); this.issues = i; }
}
class UnauthorizedError extends HttpError {
  constructor(m = "Unauthorized") { super(401, "UNAUTHORIZED", m); }
}
class ForbiddenError extends HttpError {
  constructor(m = "Forbidden") { super(403, "FORBIDDEN", m); }
}

function asyncHandler(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}
function errorHandler(err, req, res, next) {
  req.log.error({ err: err.message, code: err.code, status: err.status }, err.message);
  if (err instanceof HttpError) {
    const body = { error: err.message, code: err.code };
    if (err.issues) body.issues = err.issues;
    return res.status(err.status).json(body);
  }
  res.status(500).json({ error: "Internal Server Error", code: "INTERNAL" });
}

const userSchema = z.object({
  username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/),
  password: z.string().min(8).max(100),
});
const sessionSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

function validate(schema) {
  return (req, res, next) => {
    try { req.validated = schema.parse(req.body); next(); }
    catch (err) { if (err.issues) return next(new ValidationError(err.issues)); next(err); }
  };
}
function auth(req, res, next) {
  const a = req.headers.authorization;
  if (!a || !a.startsWith("Bearer ")) return next(new UnauthorizedError());
  try { req.user = jwt.verify(a.slice(7), SECRET); next(); }
  catch (e) { next(new UnauthorizedError()); }
}

const app = express();
app.use(express.json());

app.get("/", (req, res) => res.json({ status: "healthy", version: "1.0.0" }));
app.get("/health", (req, res) => res.json({ status: "ok" }));

app.post("/users", validate(userSchema), asyncHandler(async (req, res) => {
  const { username, password } = req.validated;
  if (await db("users").where({ username }).first()) throw new ConflictError("username already taken");
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db("users").insert({ username, hash, created_at: Date.now() });
  res.status(201).json({ id, username });
}));

app.post("/sessions", validate(sessionSchema), asyncHandler(async (req, res) => {
  const { username, password } = req.validated;
  const u = await db("users").where({ username }).first();
  if (!u) throw new UnauthorizedError();
  if (!(await bcrypt.compare(password, u.hash))) throw new UnauthorizedError();
  const token = jwt.sign({ userId: u.id, username: u.username }, SECRET, { expiresIn: TOKEN_TTL });
  res.status(201).json({ token, user: { id: u.id, username: u.username } });
}));

app.get("/sessions/me", auth, asyncHandler(async (req, res) => {
  const u = await db("users").select("id", "username").where({ id: req.user.userId }).first();
  if (!u) throw new NotFoundError();
  res.json(u);
}));

app.use(errorHandler);

module.exports = { app, db, migrate };

if (require.main === module) {
  migrate().then(() => {
    app.listen(3000, () => logger.info("Listening on :3000"));
  });
}

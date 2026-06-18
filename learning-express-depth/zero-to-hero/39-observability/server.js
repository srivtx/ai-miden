// server.js
//
// Project 39: The Observability
// ==============================
// prom-client + RED method (Rate / Errors / Duration). Each HTTP request
// increments a counter for its route+method, and records latency in a
// Histogram. Exposing /metrics on port 9090 so Prometheus can scrape it.
//
// Setup:
//   redis-server
//   npm install ioredis rate-limiter-flexible prom-client express pino knex better-sqlite3
//   node server.js
//   curl http://localhost:9090/metrics
//
// Prometheus config (prometheus.yml):
//   scrape_configs:
//     - job_name: "api"
//       static_configs:
//         - targets: ["host.docker.internal:9090"]

const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const knex = require("knex");
const { z } = require("zod");
const pino = require("pino");
const crypto = require("node:crypto");
const prom = require("prom-client");

const SECRET = "dev-secret-change-in-prod";
const TOKEN_TTL = "7d";

const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  transport: process.env.NODE_ENV === "production" ? undefined : { target: "pino-pretty" },
});

// PROJECT 39: Prometheus metrics
const collectDefault = prom.collectDefaultMetrics;
collectDefault({ prefix: "myapp_" });

const httpRequestsTotal = new prom.Counter({
  name: "myapp_http_requests_total",
  help: "Total HTTP requests",
  labelNames: ["method", "route", "status_code"],
});

const httpRequestDuration = new prom.Histogram({
  name: "myapp_http_request_duration_seconds",
  help: "HTTP request duration in seconds",
  labelNames: ["method", "route", "status_code"],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
});

const dbPoolSize = new prom.Gauge({
  name: "myapp_db_pool_size",
  help: "Active DB connections",
});

function metricsMiddleware(req, res, next) {
  const end = httpRequestDuration.startTimer();
  res.on("finish", () => {
    const route = req.route ? req.route.path : req.path;
    httpRequestsTotal.inc({
      method: req.method,
      route,
      status_code: res.statusCode,
    });
    end({
      method: req.method,
      route,
      status_code: res.statusCode,
    });
  });
  next();
}

const db = knex({
  client: "better-sqlite3",
  connection: { filename: "app.db" },
  useNullAsDefault: true,
  pool: {
    afterCreate: (conn, cb) => { dbPoolSize.inc(); cb(null, conn); },
  },
});

async function migrate() {
  await db.schema.createTableIfNotExists("users", (t) => {
    t.increments("id").primary();
    t.string("username").unique().notNullable();
    t.string("hash").notNullable();
    t.string("email").unique();
    t.bigInteger("created_at").notNullable();
    t.integer("balance").notNullable().defaultTo(0);
  });
  await db.schema.createTableIfNotExists("posts", (t) => {
    t.increments("id").primary();
    t.integer("user_id").notNullable().references("id").inTable("users").onDelete("CASCADE");
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
class NotFoundError extends HttpError {
  constructor(m = "Not Found") { super(404, "NOT_FOUND", m); }
}
class ConflictError extends HttpError {
  constructor(m = "Conflict") { super(409, "CONFLICT", m); }
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

const userCreateSchema = z.object({
  username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/),
  password: z.string().min(8).max(100),
  email: z.string().email().optional(),
});
const sessionCreateSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});
const postCreateSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1).max(10000),
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
function paginate(req) {
  const limit = Math.min(parseInt(req.query.limit) || 20, 100);
  const offset = parseInt(req.query.offset) || 0;
  return { limit, offset };
}
function meta(total, limit, offset) {
  return { total, limit, offset, page: Math.floor(offset / limit) + 1, totalPages: Math.ceil(total / limit) };
}

const app = express();
app.use(express.json());
app.use(metricsMiddleware);

app.get("/", (req, res) => res.json({ message: "Welcome. /metrics for Prometheus." }));
app.get("/health", (req, res) => res.json({ status: "ok" }));

app.post("/users", validate(userCreateSchema), asyncHandler(async (req, res) => {
  const { username, password, email } = req.validated;
  if (await db("users").where({ username }).first()) throw new ConflictError("username already taken");
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db("users").insert({ username, hash, email: email || null, balance: 0, created_at: Date.now() });
  res.status(201).json({ id, username, email: email || null });
}));

app.get("/users", asyncHandler(async (req, res) => {
  const { limit, offset } = paginate(req);
  const [users, c] = await Promise.all([
    db("users").select("id", "username", "email", "balance", "created_at").orderBy("created_at", "desc").limit(limit).offset(offset),
    db("users").count("id as count").first(),
  ]);
  res.json({ data: users, meta: meta(c.count, limit, offset) });
}));

app.get("/users/:id", asyncHandler(async (req, res) => {
  const u = await db("users").select("id", "username", "email", "balance", "created_at").where({ id: req.params.id }).first();
  if (!u) throw new NotFoundError("User not found");
  res.json(u);
}));

app.patch("/users/:id", auth, asyncHandler(async (req, res) => {
  if (Number(req.params.id) !== req.user.userId) throw new ForbiddenError();
  const { username, email } = req.body;
  const updates = {};
  if (username) updates.username = username;
  if (email) updates.email = email;
  if (Object.keys(updates).length === 0) throw new ValidationError([{ path: "", message: "no fields" }]);
  await db("users").where({ id: req.params.id }).update(updates);
  res.json(await db("users").select("id", "username", "email", "balance", "created_at").where({ id: req.params.id }).first());
}));

app.post("/sessions", validate(sessionCreateSchema), asyncHandler(async (req, res) => {
  const { username, password } = req.validated;
  const u = await db("users").where({ username }).first();
  if (!u) throw new UnauthorizedError();
  if (!(await bcrypt.compare(password, u.hash))) throw new UnauthorizedError();
  const token = jwt.sign({ userId: u.id, username: u.username }, SECRET, { expiresIn: TOKEN_TTL });
  res.status(201).json({ token, user: { id: u.id, username: u.username, email: u.email } });
}));

app.get("/sessions/me", auth, asyncHandler(async (req, res) => {
  const u = await db("users").select("id", "username", "email", "balance", "created_at").where({ id: req.user.userId }).first();
  if (!u) throw new NotFoundError();
  res.json(u);
}));

app.get("/posts", asyncHandler(async (req, res) => {
  const { limit, offset } = paginate(req);
  const [posts, c] = await Promise.all([
    db("posts").join("users", "posts.user_id", "users.id").select("posts.*", "users.username as author").orderBy("posts.created_at", "desc").limit(limit).offset(offset),
    db("posts").count("id as count").first(),
  ]);
  res.json({ data: posts, meta: meta(c.count, limit, offset) });
}));

app.post("/posts", auth, validate(postCreateSchema), asyncHandler(async (req, res) => {
  const { title, body } = req.validated;
  const [id] = await db("posts").insert({ user_id: req.user.userId, title, body, created_at: Date.now() });
  res.status(201).json({ id, userId: req.user.userId, title, body });
}));

app.get("/posts/:id", asyncHandler(async (req, res) => {
  const p = await db("posts").join("users", "posts.user_id", "users.id").select("posts.*", "users.username as author").where("posts.id", req.params.id).first();
  if (!p) throw new NotFoundError("Post not found");
  res.json(p);
}));

app.patch("/posts/:id", auth, asyncHandler(async (req, res) => {
  const p = await db("posts").where({ id: req.params.id }).first();
  if (!p) throw new NotFoundError();
  if (p.user_id !== req.user.userId) throw new ForbiddenError();
  const { title, body } = req.body;
  const updates = {};
  if (title) updates.title = title;
  if (body) updates.body = body;
  await db("posts").where({ id: req.params.id }).update(updates);
  res.json(await db("posts").where({ id: req.params.id }).first());
}));

app.delete("/posts/:id", auth, asyncHandler(async (req, res) => {
  const p = await db("posts").where({ id: req.params.id }).first();
  if (!p) throw new NotFoundError();
  if (p.user_id !== req.user.userId) throw new ForbiddenError();
  await db("posts").where({ id: req.params.id }).delete();
  res.status(204).end();
}));

app.use(errorHandler);

module.exports = { app, db, migrate };

if (require.main === module) {
  migrate().then(() => {
    app.listen(3000, () => logger.info("App: http://localhost:3000"));
    // Metrics on a separate port so Prometheus scrapes independently
    const metricsApp = express();
    metricsApp.get("/metrics", async (req, res) => {
      res.set("Content-Type", prom.register.contentType);
      res.end(await prom.register.metrics());
    });
    metricsApp.listen(9090, () => logger.info("Metrics: http://localhost:9090/metrics"));
  });
}

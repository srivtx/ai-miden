// server.js
//
// Project 40: The Microservices
// ==============================
// Eight services split by bounded context, connected through an API gateway.
// Each service owns its own SQLite database. Communication is synchronous
// via HTTP (for reads/commands) and async via Redis pub/sub (for events).
//
// Services:
//   1. gateway    (port 8000) - routes to internal services + auth
//   2. users      (port 8001) - user registration, profiles
//   3. auth       (port 8002) - login, JWT issuance, token verification
//   4. posts      (port 8003) - crud for posts
//   5. workspace  (port 8004) - workspaces, membership, RBAC
//   6. search     (port 8005) - full-text search over posts
//   7. files      (port 8006) - file upload/download
//   8. webhook    (port 8007) - outbound webhook registration + firing
//
// Async events (Redis pub/sub channels):
//   user.created  -> posts, workspace, files, webhook
//   post.created  -> search, webhook
//
// Setup:
//   redis-server
//   npm install express bcrypt jsonwebtoken knex better-sqlite3 zod multer ioredis
//   node server.js

const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const knex = require("knex");
const { z } = require("zod");
const Redis = require("ioredis");
const multer = require("multer");
const path = require("node:path");
const crypto = require("node:crypto");
const fs = require("node:fs");

const JWT_SECRET = "dev-secret";
const TOKEN_TTL = "7d";
const redis = new Redis({ host: "localhost", port: 6379, maxRetriesPerRequest: null });

const uploadDir = path.join(__dirname, "uploads");
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
const upload = multer({ dest: uploadDir, limits: { fileSize: 10 * 1024 * 1024 } });

function makeDb(name) {
  return knex({ client: "better-sqlite3", connection: { filename: `${name}.db` }, useNullAsDefault: true });
}

// ----- 1. Gateway -----
const gateway = express();
gateway.use(express.json());

const GATEWAY_KEY = "gateway-internal-key";

async function gatewayAuth(req, res, next) {
  const a = req.headers.authorization;
  if (!a) return next();
  try {
    req.user = jwt.verify(a.slice(7), JWT_SECRET);
  } catch (e) { /* pass */ }
  next();
}

gateway.use(gatewayAuth);

function forward(serviceUrl) {
  return async (req, res) => {
    try {
      const target = new URL(req.originalUrl, serviceUrl);
      target.search = new URL(req.url, serviceUrl).search;
      const opts = {
        method: req.method,
        headers: {
          "Content-Type": "application/json",
          "X-Gateway-Key": GATEWAY_KEY,
          "X-User-Id": req.user ? String(req.user.userId) : "",
        },
      };
      if (req.user) opts.headers["X-User-Id"] = String(req.user.userId);
      if (req.body && Object.keys(req.body).length) opts.body = JSON.stringify(req.body);
      const r = await fetch(target.href, opts);
      const text = await r.text();
      res.status(r.status).set("Content-Type", r.headers.get("Content-Type")).send(text);
    } catch (err) {
      res.status(502).json({ error: "Gateway error", detail: err.message });
    }
  };
}

// Public routes
gateway.post("/users", forward("http://localhost:8001"));
gateway.post("/sessions", forward("http://localhost:8002"));
gateway.get("/sessions/me", forward("http://localhost:8002"));
gateway.get("/users", forward("http://localhost:8001"));
gateway.get("/users/:id", forward("http://localhost:8001"));
// Posts
gateway.get("/posts", forward("http://localhost:8003"));
gateway.get("/posts/:id", forward("http://localhost:8003"));
gateway.post("/posts", forward("http://localhost:8003"));
gateway.patch("/posts/:id", forward("http://localhost:8003"));
gateway.delete("/posts/:id", forward("http://localhost:8003"));
// Workspaces
gateway.get("/workspaces", forward("http://localhost:8004"));
gateway.post("/workspaces", forward("http://localhost:8004"));
gateway.get("/workspaces/:id", forward("http://localhost:8004"));
gateway.post("/workspaces/:id/members", forward("http://localhost:8004"));
// Search
gateway.get("/search", forward("http://localhost:8005"));
// Files
gateway.post("/files", forward("http://localhost:8006"));
gateway.get("/files/:name", forward("http://localhost:8006"));
// Webhooks
gateway.post("/webhooks", forward("http://localhost:8007"));
gateway.get("/webhooks", forward("http://localhost:8007"));
gateway.delete("/webhooks/:id", forward("http://localhost:8007"));

gateway.get("/", (req, res) => res.json({ services: ["gateway:8000", "users:8001", "auth:8002", "posts:8003", "workspace:8004", "search:8005", "files:8006", "webhook:8007"] }));

// ----- 2. Users -----
const usersDb = makeDb("users_service");
const usersApp = express();
usersApp.use(express.json());

usersApp.use((req, res, next) => {
  if (req.headers["x-gateway-key"] !== GATEWAY_KEY) return res.status(403).json({ error: "Forbidden" });
  next();
});

usersApp.post("/users", async (req, res) => {
  const schema = z.object({ username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/), password: z.string().min(8).max(100), email: z.string().email().optional() });
  const { username, password, email } = schema.parse(req.body);
  if (await usersDb("users").where({ username }).first()) return res.status(409).json({ error: "Conflict" });
  const hash = await bcrypt.hash(password, 10);
  const [id] = await usersDb("users").insert({ username, hash, email: email || null, created_at: Date.now() });
  redis.publish("user.created", JSON.stringify({ id, username, email }));
  res.status(201).json({ id, username, email: email || null });
});

usersApp.get("/users", async (req, res) => {
  const users = await usersDb("users").select("id", "username", "email", "created_at").orderBy("created_at", "desc").limit(50);
  res.json({ data: users });
});

usersApp.get("/users/:id", async (req, res) => {
  const u = await usersDb("users").select("id", "username", "email", "created_at").where("id", req.params.id).first();
  if (!u) return res.status(404).json({ error: "Not Found" });
  res.json(u);
});

// ----- 3. Auth -----
const authDb = makeDb("auth_service");
const authApp = express();
authApp.use(express.json());
authApp.use((req, res, next) => {
  if (req.headers["x-gateway-key"] !== GATEWAY_KEY) return res.status(403).json({ error: "Forbidden" });
  next();
});

authApp.post("/sessions", async (req, res) => {
  const { username, password } = req.body;
  const u = await usersDb("users").where({ username }).first();
  if (!u) return res.status(401).json({ error: "Unauthorized" });
  if (!(await bcrypt.compare(password, u.hash))) return res.status(401).json({ error: "Unauthorized" });
  const token = jwt.sign({ userId: u.id, username: u.username }, JWT_SECRET, { expiresIn: TOKEN_TTL });
  res.status(201).json({ token, user: { id: u.id, username: u.username, email: u.email } });
});

authApp.get("/sessions/me", async (req, res) => {
  const uid = req.headers["x-user-id"];
  if (!uid) return res.status(401).json({ error: "Unauthorized" });
  const u = await usersDb("users").select("id", "username", "email", "created_at").where({ id: uid }).first();
  if (!u) return res.status(404).json({ error: "Not Found" });
  res.json(u);
});

// ----- 4. Posts -----
const postsDb = makeDb("posts_service");
const postsApp = express();
postsApp.use(express.json());
postsApp.use((req, res, next) => {
  if (req.headers["x-gateway-key"] !== GATEWAY_KEY) return res.status(403).json({ error: "Forbidden" });
  next();
});

postsApp.post("/posts", async (req, res) => {
  const uid = parseInt(req.headers["x-user-id"]);
  if (!uid) return res.status(401).json({ error: "Unauthorized" });
  const { title, body } = req.body;
  if (!title || !body) return res.status(400).json({ error: "Validation" });
  const [id] = await postsDb("posts").insert({ user_id: uid, title, body, created_at: Date.now() });
  redis.publish("post.created", JSON.stringify({ id, userId: uid, title }));
  res.status(201).json({ id, userId: uid, title, body });
});

postsApp.get("/posts", async (req, res) => {
  const posts = await postsDb("posts").select("*").orderBy("created_at", "desc").limit(50);
  res.json({ data: posts });
});

postsApp.get("/posts/:id", async (req, res) => {
  const p = await postsDb("posts").where("id", req.params.id).first();
  if (!p) return res.status(404).json({ error: "Not Found" });
  res.json(p);
});

postsApp.patch("/posts/:id", async (req, res) => {
  const uid = parseInt(req.headers["x-user-id"]);
  if (!uid) return res.status(401).json({ error: "Unauthorized" });
  const p = await postsDb("posts").where("id", req.params.id).first();
  if (!p) return res.status(404).json({ error: "Not Found" });
  if (p.user_id !== uid) return res.status(403).json({ error: "Forbidden" });
  const { title, body } = req.body;
  const u = {};
  if (title) u.title = title;
  if (body) u.body = body;
  await postsDb("posts").where("id", req.params.id).update(u);
  res.json(await postsDb("posts").where("id", req.params.id).first());
});

postsApp.delete("/posts/:id", async (req, res) => {
  const uid = parseInt(req.headers["x-user-id"]);
  if (!uid) return res.status(401).json({ error: "Unauthorized" });
  const p = await postsDb("posts").where("id", req.params.id).first();
  if (!p) return res.status(404).json({ error: "Not Found" });
  if (p.user_id !== uid) return res.status(403).json({ error: "Forbidden" });
  await postsDb("posts").where("id", req.params.id).delete();
  res.status(204).end();
});

// ----- 5. Workspace -----
const wsDb = makeDb("workspace_service");
const wsApp = express();
wsApp.use(express.json());
wsApp.use((req, res, next) => {
  if (req.headers["x-gateway-key"] !== GATEWAY_KEY) return res.status(403).json({ error: "Forbidden" });
  next();
});

const roleHierarchy = { owner: 4, admin: 3, member: 2, guest: 1 };

async function requireRole(workspaceId, userId, role) {
  const m = await wsDb("workspace_members").where({ workspace_id: workspaceId, user_id: userId }).first();
  if (!m || roleHierarchy[m.role] < roleHierarchy[role]) return false;
  return true;
}

wsApp.post("/workspaces", async (req, res) => {
  const uid = parseInt(req.headers["x-user-id"]);
  if (!uid) return res.status(401).json({ error: "Unauthorized" });
  const { name } = req.body;
  const [id] = await wsDb("workspaces").insert({ name, owner_id: uid, created_at: Date.now() });
  await wsDb("workspace_members").insert({ workspace_id: id, user_id: uid, role: "owner" });
  redis.publish("workspace.created", JSON.stringify({ id, name, ownerId: uid }));
  res.status(201).json({ id, name });
});

wsApp.get("/workspaces", async (req, res) => {
  const uid = parseInt(req.headers["x-user-id"]);
  const memberOf = uid ? await wsDb("workspace_members").where({ user_id: uid }).select("workspace_id") : [];
  const ids = memberOf.map((m) => m.workspace_id);
  const ws = ids.length ? await wsDb("workspaces").whereIn("id", ids) : [];
  res.json({ data: ws });
});

wsApp.get("/workspaces/:id", async (req, res) => {
  const uid = parseInt(req.headers["x-user-id"]);
  if (!(await requireRole(req.params.id, uid, "guest"))) return res.status(403).json({ error: "Forbidden" });
  const w = await wsDb("workspaces").where("id", req.params.id).first();
  const members = await wsDb("workspace_members").where("workspace_id", req.params.id);
  res.json({ ...w, members });
});

wsApp.post("/workspaces/:id/members", async (req, res) => {
  const uid = parseInt(req.headers["x-user-id"]);
  if (!(await requireRole(req.params.id, uid, "admin"))) return res.status(403).json({ error: "Forbidden" });
  const { userId, role } = req.body;
  await wsDb("workspace_members").insert({ workspace_id: req.params.id, user_id: userId, role });
  redis.publish("workspace.member_added", JSON.stringify({ workspaceId: req.params.id, userId, role }));
  res.status(201).json({ message: "Member added" });
});

// ----- 6. Search -----
const searchDb = makeDb("search_service");
const searchApp = express();
searchApp.use(express.json());
searchApp.use((req, res, next) => {
  if (req.headers["x-gateway-key"] !== GATEWAY_KEY) return res.status(403).json({ error: "Forbidden" });
  next();
});

searchApp.get("/search", async (req, res) => {
  const q = req.query.q;
  if (!q) return res.json({ data: [] });
  const posts = await searchDb("posts").where("body", "like", `%${q}%`).orWhere("title", "like", `%${q}%`).limit(20);
  res.json({ data: posts });
});

// ----- 7. Files -----
const filesDb = makeDb("files_service");
const filesApp = express();
filesApp.use((req, res, next) => {
  if (req.headers["x-gateway-key"] !== GATEWAY_KEY) return res.status(403).json({ error: "Forbidden" });
  next();
});

filesApp.post("/files", upload.single("file"), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No file" });
  await filesDb("files").insert({ name: req.file.filename, original_name: req.file.originalname, size: req.file.size, uploaded_by: req.headers["x-user-id"] || "0", created_at: Date.now() });
  res.status(201).json({ name: req.file.filename, originalName: req.file.originalname, size: req.file.size });
});

filesApp.get("/files/:name", (req, res) => {
  const filePath = path.join(uploadDir, req.params.name);
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: "Not Found" });
  res.sendFile(filePath);
});

// ----- 8. Webhook -----
const webhookDb = makeDb("webhook_service");
const webhookApp = express();
webhookApp.use(express.json());
webhookApp.use((req, res, next) => {
  if (req.headers["x-gateway-key"] !== GATEWAY_KEY) return res.status(403).json({ error: "Forbidden" });
  next();
});

async function fireWebhook(eventName, data) {
  const hooks = await webhookDb("webhooks").where({ active: 1 });
  const matching = hooks.filter((h) => { const ev = JSON.parse(h.events || "[]"); return ev.includes(eventName) || ev.includes("*"); });
  for (const h of matching) {
    const body = JSON.stringify({ id: crypto.randomUUID(), event: eventName, data });
    fetch(h.url, { method: "POST", headers: { "Content-Type": "application/json", "X-Webhook-Event": eventName }, body, signal: AbortSignal.timeout(5000) }).catch(() => {});
  }
}

// Subscribe to events and fire matching webhooks
redis.subscribe("user.created", "post.created", "workspace.created", "workspace.member_added", (err) => {
  if (err) console.error("Redis subscribe error:", err);
});
redis.on("message", (channel, message) => {
  try { fireWebhook(channel, JSON.parse(message)); } catch (e) {}
});

webhookApp.post("/webhooks", async (req, res) => {
  const { url, events } = req.body;
  const secret = `whsec_${crypto.randomBytes(24).toString("hex")}`;
  const [id] = await webhookDb("webhooks").insert({ owner_id: req.headers["x-user-id"] || 0, url, secret, events: JSON.stringify(events), active: 1, created_at: Date.now() });
  res.status(201).json({ id, url, events, secret, active: true });
});

webhookApp.get("/webhooks", async (req, res) => {
  const uid = req.headers["x-user-id"] || 0;
  const hooks = await webhookDb("webhooks").where("owner_id", uid).select("id", "url", "events", "active", "created_at");
  res.json({ data: hooks.map((h) => ({ ...h, events: JSON.parse(h.events) })) });
});

webhookApp.delete("/webhooks/:id", async (req, res) => {
  await webhookDb("webhooks").where("id", req.params.id).delete();
  res.status(204).end();
});

// ----- MIGRATIONS -----
async function migrateAll() {
  await usersDb.schema.createTableIfNotExists("users", (t) => {
    t.increments("id").primary();
    t.string("username").unique().notNullable();
    t.string("hash").notNullable();
    t.string("email").unique();
    t.bigInteger("created_at").notNullable();
  });
  await postsDb.schema.createTableIfNotExists("posts", (t) => {
    t.increments("id").primary();
    t.integer("user_id").notNullable();
    t.string("title").notNullable();
    t.text("body").notNullable();
    t.bigInteger("created_at").notNullable();
  });
  await wsDb.schema.createTableIfNotExists("workspaces", (t) => {
    t.increments("id").primary();
    t.string("name").notNullable();
    t.integer("owner_id").notNullable();
    t.bigInteger("created_at").notNullable();
  });
  await wsDb.schema.createTableIfNotExists("workspace_members", (t) => {
    t.integer("workspace_id").notNullable();
    t.integer("user_id").notNullable();
    t.string("role").notNullable();
    t.primary(["workspace_id", "user_id"]);
  });
  await searchDb.schema.createTableIfNotExists("posts", (t) => {
    t.increments("id").primary();
    t.integer("user_id").notNullable();
    t.string("title").notNullable();
    t.text("body").notNullable();
    t.bigInteger("created_at").notNullable();
  });
  await filesDb.schema.createTableIfNotExists("files", (t) => {
    t.increments("id").primary();
    t.string("name").notNullable();
    t.string("original_name").notNullable();
    t.integer("size").notNullable();
    t.integer("uploaded_by").notNullable();
    t.bigInteger("created_at").notNullable();
  });
  await webhookDb.schema.createTableIfNotExists("webhooks", (t) => {
    t.increments("id").primary();
    t.integer("owner_id").notNullable();
    t.text("url").notNullable();
    t.string("secret").notNullable();
    t.text("events").notNullable();
    t.integer("active").notNullable().defaultTo(1);
    t.bigInteger("created_at").notNullable();
  });
}

const searcher = redis.duplicate();
searcher.subscribe("post.created", (err) => { if (!err) console.log("Search service subscribed to post.created"); });
searcher.on("message", async (channel, message) => {
  if (channel === "post.created") {
    const { id, userId, title } = JSON.parse(message);
    const p = await postsDb("posts").where("id", id).first();
    if (p) {
      await searchDb("posts").insert({ id: p.id, user_id: p.user_id, title: p.title, body: p.body, created_at: p.created_at }).onConflict("id").merge();
    }
  }
});

migrateAll().then(() => {
  gateway.listen(8000, () => console.log("Gateway:  http://localhost:8000"));
  usersApp.listen(8001, () => console.log("Users:    http://localhost:8001"));
  authApp.listen(8002, () => console.log("Auth:     http://localhost:8002"));
  postsApp.listen(8003, () => console.log("Posts:    http://localhost:8003"));
  wsApp.listen(8004, () => console.log("WS:       http://localhost:8004"));
  searchApp.listen(8005, () => console.log("Search:   http://localhost:8005"));
  filesApp.listen(8006, () => console.log("Files:    http://localhost:8006"));
  webhookApp.listen(8007, () => console.log("Webhook:  http://localhost:8007"));
});

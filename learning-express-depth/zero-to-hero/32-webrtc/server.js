// server.js
//
// Project 32: The WebRTC Voice Channel
// =====================================
// Adds WebRTC signaling. The server relays SDP and ICE messages between
// peers. The peers establish a direct peer-to-peer connection. Audio flows
// peer-to-peer (not through the server).
//
// Setup:
//   redis-server
//   npm install express bcrypt jsonwebtoken knex better-sqlite3 zod pino pino-http multer nodemailer ioredis rate-limiter-flexible node-cron bullmq ws
//   node server.js
//
// Test:
//   Open http://localhost:3000/general in two browser tabs.
//   Click "Join Channel" in both. Allow microphone. Talk to each other.
//   Phone (same WiFi): use the LAN URL printed on startup, e.g. http://192.168.x.x:3000/general
//   Phone (remote):     ngrok http 3000  →  open the https URL on your phone

const express = require("express");
const os = require("node:os");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const knex = require("knex");
const { z } = require("zod");
const pino = require("pino");
const pinoHttp = require("pino-http");
const multer = require("multer");
const path = require("node:path");
const fs = require("node:fs");
const crypto = require("node:crypto");
const nodemailer = require("nodemailer");
const Redis = require("ioredis");
const { RateLimiterRedis } = require("rate-limiter-flexible");
const cron = require("node-cron");
const { Queue, Worker } = require("bullmq");
const { WebSocketServer, WebSocket } = require("ws");

const SECRET = "dev-secret-change-in-prod";
const TOKEN_TTL = "7d";

const UPLOADS_DIR = path.join(__dirname, "uploads");
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR);

const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  transport:
    process.env.NODE_ENV === "production"
      ? undefined
      : { target: "pino-pretty" },
});

const redis = new Redis({
  host: process.env.REDIS_HOST || "localhost",
  port: parseInt(process.env.REDIS_PORT) || 6379,
  maxRetriesPerRequest: null, // required by BullMQ (uses blocking Redis commands)
});
redis.on("error", (err) => logger.error({ err: err.message }, "Redis error"));
redis.on("connect", () => logger.info("Connected to Redis"));

const emailQueue = new Queue("email", { connection: redis });
const emailWorker = new Worker(
  "email",
  async (job) => {
    if (job.name === "welcome") {
      const { email, username } = job.data;
      await sendEmail({
        to: email,
        subject: "Welcome!",
        text: `Welcome, ${username}!`,
        html: `<p>Welcome, ${username}!</p>`,
      });
    }
  },
  { connection: redis },
);
emailWorker.on("failed", (job, err) =>
  logger.error({ err: err.message }, "Email job failed"),
);

const rateLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: "rl",
  points: 100,
  duration: 60,
});

class Cache {
  constructor(redis, ttlSeconds = 60) {
    this.redis = redis;
    this.ttl = ttlSeconds;
  }
  async get(key) {
    try {
      const v = await this.redis.get(key);
      return v ? JSON.parse(v) : undefined;
    } catch (e) {
      return undefined;
    }
  }
  async set(key, value, ttlSeconds) {
    try {
      await this.redis.set(
        key,
        JSON.stringify(value),
        "EX",
        ttlSeconds || this.ttl,
      );
    } catch (e) {}
  }
  async delete(key) {
    try {
      await this.redis.del(key);
    } catch (e) {}
  }
}
const cache = new Cache(redis, 60);

const app = express();
app.set("trust proxy", 1);
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS");
  if (req.method === "OPTIONS") return res.sendStatus(200);
  next();
});
app.use("/cove", express.static(path.join(__dirname, "../../cove")));
app.use(express.json());
app.use(pinoHttp({ logger }));
app.use("/uploads", express.static(UPLOADS_DIR));

async function rateLimitMiddleware(req, res, next) {
  try {
    await rateLimiter.consume(req.ip, 1);
    next();
  } catch (err) {
    res.set("Retry-After", "60");
    res.status(429).json({ error: "Too Many Requests", code: "RATE_LIMIT" });
  }
}
app.use(rateLimitMiddleware);

let transporter;
async function setupMailer() {
  if (process.env.SMTP_HOST) {
    transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT) || 587,
      auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
    });
  } else {
    const testAccount = await nodemailer.createTestAccount();
    transporter = nodemailer.createTransport({
      host: "smtp.ethereal.email",
      port: 587,
      auth: { user: testAccount.user, pass: testAccount.pass },
    });
  }
}
setupMailer();
async function sendEmail({ to, subject, text, html }) {
  const info = await transporter.sendMail({
    from: '"MyApp" <noreply@myapp.com>',
    to,
    subject,
    text,
    html,
  });
  const url = nodemailer.getTestMessageUrl(info);
  if (url) logger.info({ url }, "Preview email at:");
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS_DIR),
  filename: (req, file, cb) =>
    cb(null, `${crypto.randomUUID()}${path.extname(file.originalname)}`),
});
const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    if (!file.mimetype.startsWith("image/"))
      return cb(new Error("Only images allowed"));
    cb(null, true);
  },
});

const db = knex({
  client: "better-sqlite3",
  connection: { filename: "app.db" },
  useNullAsDefault: true,
});

async function migrate() {
  if (!(await db.schema.hasTable("users"))) {
    await db.schema.createTable("users", (t) => {
      t.increments("id").primary();
      t.string("username").unique().notNullable();
      t.string("hash").notNullable();
      t.string("email").unique();
      t.bigInteger("created_at").notNullable();
      t.integer("balance").notNullable().defaultTo(0);
    });
  }
  if (!(await db.schema.hasTable("posts"))) {
    await db.schema.createTable("posts", (t) => {
      t.increments("id").primary();
      t.integer("user_id")
        .notNullable()
        .references("id")
        .inTable("users")
        .onDelete("CASCADE");
      t.string("title").notNullable();
      t.text("body").notNullable();
      t.string("image_url");
      t.bigInteger("created_at").notNullable();
    });
  }
}
migrate().then(() => {
  const PORT = 3000;
  const server = app.listen(PORT, "0.0.0.0", () => {
    logger.info(`Server listening on http://localhost:${PORT}`);
    const nets = os.networkInterfaces();
    for (const iface of Object.values(nets)) {
      for (const addr of iface || []) {
        if (addr.family === "IPv4" && !addr.internal) {
          logger.info(`LAN (phone on same WiFi): http://${addr.address}:${PORT}/general`);
        }
      }
    }
  });

  // WebSocket servers (chat + WebRTC signaling)
  const chatWss = new WebSocketServer({ noServer: true });
  const signalingWss = new WebSocketServer({ noServer: true });
  const signaling = new Map(); // channel -> Set of WebSocket clients
  const channelHosts = new Map(); // channel -> first WebSocket (creates the WebRTC offer)

  chatWss.on("connection", (ws) => {
    ws.send(
      JSON.stringify({ type: "welcome", message: "Connected to the chat" }),
    );

    ws.on("message", (data) => {
      try {
        const message = JSON.parse(data.toString());
        if (message.type === "chat") {
          chatWss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(
                JSON.stringify({
                  type: "chat",
                  user: message.user,
                  text: message.text,
                  timestamp: Date.now(),
                }),
              );
            }
          });
        }
      } catch (err) {}
    });
  });

  signalingWss.on("connection", (ws, req) => {
    const url = new URL(req.url, "http://localhost");
    const channel = url.pathname.slice(1);
    const MAX_VOICE_PEERS = 2;

    if (!signaling.has(channel)) signaling.set(channel, new Set());
    const peers = signaling.get(channel);
    peers.add(ws);

    // Voice is 1-to-1 — drop stale tabs so host + one guest remain
    while (peers.size > MAX_VOICE_PEERS) {
      for (const client of peers) {
        if (client !== ws && client !== channelHosts.get(channel)) {
          client.close(4000, "Too many peers — close extra tabs");
          peers.delete(client);
          break;
        }
      }
    }

    if (!channelHosts.has(channel)) channelHosts.set(channel, ws);

    const broadcastPresence = () => {
      const count = peers.size;
      for (const client of peers) {
        if (client.readyState !== WebSocket.OPEN) continue;
        const role = client === channelHosts.get(channel) ? "host" : "guest";
        client.send(JSON.stringify({ type: "presence", count, role }));
      }
    };

    logger.info(
      { channel, clientCount: peers.size, role: ws === channelHosts.get(channel) ? "host" : "guest" },
      "Peer joined channel",
    );
    broadcastPresence();

    ws.on("message", (data) => {
      try {
        const parsed = JSON.parse(data.toString());
        if (parsed.type === "presence") return;
      } catch (err) {}

      for (const client of peers) {
        if (client !== ws && client.readyState === WebSocket.OPEN) {
          client.send(data.toString());
        }
      }
    });

    ws.on("close", () => {
      peers.delete(ws);
      if (channelHosts.get(channel) === ws) {
        const next = peers.values().next().value;
        if (next) channelHosts.set(channel, next);
        else channelHosts.delete(channel);
      }
      if (!peers.size) signaling.delete(channel);
      logger.info(
        { channel, clientCount: peers.size },
        "Peer left channel",
      );
      if (peers.size) broadcastPresence();
    });
  });

  server.on("upgrade", (req, socket, head) => {
    const url = new URL(req.url, "http://localhost");
    if (url.pathname === "/" || url.pathname === "/chat") {
      chatWss.handleUpgrade(req, socket, head, (ws) =>
        chatWss.emit("connection", ws, req),
      );
    } else {
      signalingWss.handleUpgrade(req, socket, head, (ws) =>
        signalingWss.emit("connection", ws, req),
      );
    }
  });
});

class HttpError extends Error {
  constructor(s, c, m) {
    super(m);
    this.status = s;
    this.code = c;
  }
}
class ValidationError extends HttpError {
  constructor(i) {
    super(400, "VALIDATION", "Validation failed");
    this.issues = i;
  }
}
class UnauthorizedError extends HttpError {
  constructor(m = "Unauthorized") {
    super(401, "UNAUTHORIZED", m);
  }
}
class ForbiddenError extends HttpError {
  constructor(m = "Forbidden") {
    super(403, "FORBIDDEN", m);
  }
}
class NotFoundError extends HttpError {
  constructor(m = "Not Found") {
    super(404, "NOT_FOUND", m);
  }
}
class ConflictError extends HttpError {
  constructor(m = "Conflict") {
    super(409, "CONFLICT", m);
  }
}

function asyncHandler(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}
function errorHandler(err, req, res, next) {
  req.log.error(
    { err: err.message, code: err.code, status: err.status },
    err.message,
  );
  if (err instanceof HttpError) {
    const body = { error: err.message, code: err.code };
    if (err.issues) body.issues = err.issues;
    return res.status(err.status).json(body);
  }
  res.status(500).json({ error: "Internal Server Error", code: "INTERNAL" });
}

const userCreateSchema = z.object({
  username: z
    .string()
    .min(3)
    .max(30)
    .regex(/^[a-zA-Z0-9_]+$/),
  password: z.string().min(8).max(100),
  email: z.string().email().optional(),
});
const userUpdateSchema = z.object({
  username: z
    .string()
    .min(3)
    .max(30)
    .regex(/^[a-zA-Z0-9_]+$/)
    .optional(),
  email: z.string().email().optional(),
});
const sessionCreateSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});
const forgotPasswordSchema = z.object({ email: z.string().email() });
const resetPasswordSchema = z.object({
  token: z.string().min(1),
  password: z.string().min(8).max(100),
});
const postCreateSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1).max(10000),
});
const postUpdateSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  body: z.string().min(1).max(10000).optional(),
});
const transferSchema = z.object({
  fromUserId: z.number().int().positive(),
  toUserId: z.number().int().positive(),
  amount: z.number().int().positive(),
});

function validate(schema) {
  return (req, res, next) => {
    try {
      req.validated = schema.parse(req.body);
      next();
    } catch (err) {
      if (err.issues) return next(new ValidationError(err.issues));
      next(err);
    }
  };
}
function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith("Bearer "))
    return next(
      new UnauthorizedError("missing or invalid authorization header"),
    );
  try {
    req.user = jwt.verify(auth.slice(7), SECRET);
    next();
  } catch (err) {
    return next(new UnauthorizedError("invalid or expired token"));
  }
}
function paginate(req) {
  const limit = Math.min(parseInt(req.query.limit) || 20, 100);
  const offset = parseInt(req.query.offset) || 0;
  return { limit, offset };
}
function meta(total, limit, offset) {
  return {
    total,
    limit,
    offset,
    page: Math.floor(offset / limit) + 1,
    totalPages: Math.ceil(total / limit),
  };
}

app.get("/", (req, res) => res.json({ message: "Welcome to the API." }));

app.post(
  "/users",
  validate(userCreateSchema),
  asyncHandler(async (req, res) => {
    const { username, password, email } = req.validated;
    if (await db("users").where({ username }).first())
      throw new ConflictError("username already taken");
    const hash = await bcrypt.hash(password, 10);
    const [id] = await db("users").insert({
      username,
      hash,
      email: email || null,
      balance: 0,
      created_at: Date.now(),
    });
    if (email)
      await emailQueue.add(
        "welcome",
        { userId: id, email, username },
        { attempts: 3, backoff: { type: "exponential", delay: 1000 } },
      );
    res.status(201).json({ id, username, email: email || null });
  }),
);

app.get(
  "/users",
  asyncHandler(async (req, res) => {
    const { limit, offset } = paginate(req);
    const [users, c] = await Promise.all([
      db("users")
        .select("id", "username", "email", "balance", "created_at")
        .orderBy("created_at", "desc")
        .limit(limit)
        .offset(offset),
      db("users").count("id as count").first(),
    ]);
    res.json({ data: users, meta: meta(c.count, limit, offset) });
  }),
);
app.get(
  "/users/:id",
  asyncHandler(async (req, res) => {
    const k = `user:${req.params.id}`;
    const c = await cache.get(k);
    if (c) return res.json(c);
    const u = await db("users")
      .select("id", "username", "email", "balance", "created_at")
      .where({ id: req.params.id })
      .first();
    if (!u) throw new NotFoundError("User not found");
    await cache.set(k, u);
    res.json(u);
  }),
);
app.patch(
  "/users/:id",
  authMiddleware,
  validate(userUpdateSchema),
  asyncHandler(async (req, res) => {
    if (Number(req.params.id) !== req.user.userId)
      throw new ForbiddenError("You can only update your own user");
    const updates = req.validated;
    if (Object.keys(updates).length === 0)
      throw new ValidationError([{ path: "", message: "no fields to update" }]);
    await db("users").where({ id: req.params.id }).update(updates);
    await cache.delete(`user:${req.params.id}`);
    const u = await db("users")
      .select("id", "username", "email", "balance", "created_at")
      .where({ id: req.params.id })
      .first();
    res.json(u);
  }),
);
app.delete(
  "/users/:id",
  authMiddleware,
  asyncHandler(async (req, res) => {
    if (Number(req.params.id) !== req.user.userId)
      throw new ForbiddenError("You can only delete your own user");
    await db("users").where({ id: req.params.id }).delete();
    await cache.delete(`user:${req.params.id}`);
    res.status(204).end();
  }),
);

app.post(
  "/sessions",
  validate(sessionCreateSchema),
  asyncHandler(async (req, res) => {
    const { username, password } = req.validated;
    const u = await db("users").where({ username }).first();
    if (!u) throw new UnauthorizedError("invalid credentials");
    if (!(await bcrypt.compare(password, u.hash)))
      throw new UnauthorizedError("invalid credentials");
    const token = jwt.sign({ userId: u.id, username: u.username }, SECRET, {
      expiresIn: TOKEN_TTL,
    });
    res
      .status(201)
      .json({
        token,
        user: { id: u.id, username: u.username, email: u.email },
      });
  }),
);
app.delete(
  "/sessions",
  authMiddleware,
  asyncHandler(async (req, res) => res.status(204).end()),
);
app.get(
  "/sessions/me",
  authMiddleware,
  asyncHandler(async (req, res) => {
    const k = `user:${req.user.userId}`;
    const c = await cache.get(k);
    if (c) return res.json(c);
    const u = await db("users")
      .select("id", "username", "email", "balance", "created_at")
      .where({ id: req.user.userId })
      .first();
    if (!u) throw new NotFoundError("User not found");
    await cache.set(k, u);
    res.json(u);
  }),
);

app.post(
  "/sessions/forgot",
  validate(forgotPasswordSchema),
  asyncHandler(async (req, res) => {
    const { email } = req.validated;
    const u = await db("users").where({ email }).first();
    if (u) {
      const t = crypto.randomBytes(32).toString("hex");
      const h = crypto.createHash("sha256").update(t).digest("hex");
      await db("users")
        .where({ id: u.id })
        .update({
          password_reset_token: h,
          password_reset_expires_at: Date.now() + 60 * 60 * 1000,
        });
      await emailQueue.add(
        "password-reset",
        { email, token: t },
        { attempts: 3, backoff: { type: "exponential", delay: 1000 } },
      );
    }
    res.json({ message: "If the email exists, a reset link has been sent" });
  }),
);
app.post(
  "/sessions/reset",
  validate(resetPasswordSchema),
  asyncHandler(async (req, res) => {
    const { token, password } = req.validated;
    const h = crypto.createHash("sha256").update(token).digest("hex");
    const u = await db("users").where({ password_reset_token: h }).first();
    if (!u || u.password_reset_expires_at < Date.now())
      throw new ValidationError([
        { path: "token", message: "invalid or expired token" },
      ]);
    await db("users")
      .where({ id: u.id })
      .update({
        hash: await bcrypt.hash(password, 10),
        password_reset_token: null,
        password_reset_expires_at: null,
      });
    await cache.delete(`user:${u.id}`);
    res.json({ message: "Password reset successful" });
  }),
);

app.post(
  "/transfer",
  authMiddleware,
  validate(transferSchema),
  asyncHandler(async (req, res) => {
    const { fromUserId, toUserId, amount } = req.validated;
    if (req.user.userId !== fromUserId)
      throw new ForbiddenError("You can only transfer from your own account");
    await db.transaction(async (trx) => {
      const fromUser = await trx("users").where({ id: fromUserId }).first();
      if (!fromUser) throw new NotFoundError("Sender not found");
      if (fromUser.balance < amount)
        throw new ValidationError([
          { path: "amount", message: "insufficient funds" },
        ]);
      const toUser = await trx("users").where({ id: toUserId }).first();
      if (!toUser) throw new NotFoundError("Receiver not found");
      await trx("users").where({ id: fromUserId }).decrement("balance", amount);
      await trx("users").where({ id: toUserId }).increment("balance", amount);
    });
    await cache.delete(`user:${fromUserId}`);
    await cache.delete(`user:${toUserId}`);
    res.json({ message: "Transfer complete" });
  }),
);

app.get(
  "/posts",
  asyncHandler(async (req, res) => {
    const { limit, offset } = paginate(req);
    const [posts, c] = await Promise.all([
      db("posts")
        .join("users", "posts.user_id", "users.id")
        .select("posts.*", "users.username as author")
        .orderBy("posts.created_at", "desc")
        .limit(limit)
        .offset(offset),
      db("posts").count("id as count").first(),
    ]);
    res.json({ data: posts, meta: meta(c.count, limit, offset) });
  }),
);
app.get(
  "/posts/:id",
  asyncHandler(async (req, res) => {
    const k = `post:${req.params.id}`;
    const c = await cache.get(k);
    if (c) return res.json(c);
    const p = await db("posts")
      .join("users", "posts.user_id", "users.id")
      .select("posts.*", "users.username as author")
      .where("posts.id", req.params.id)
      .first();
    if (!p) throw new NotFoundError("Post not found");
    await cache.set(k, p);
    res.json(p);
  }),
);
app.post(
  "/posts",
  authMiddleware,
  upload.single("image"),
  validate(postCreateSchema),
  asyncHandler(async (req, res) => {
    const { title, body } = req.validated;
    const imageUrl = req.file ? `/uploads/${req.file.filename}` : null;
    const [id] = await db("posts").insert({
      user_id: req.user.userId,
      title,
      body,
      image_url: imageUrl,
      created_at: Date.now(),
    });
    res
      .status(201)
      .json({ id, userId: req.user.userId, title, body, imageUrl });
  }),
);
app.patch(
  "/posts/:id",
  authMiddleware,
  validate(postUpdateSchema),
  asyncHandler(async (req, res) => {
    const updates = req.validated;
    if (Object.keys(updates).length === 0)
      throw new ValidationError([{ path: "", message: "no fields to update" }]);
    const p = await db("posts").where({ id: req.params.id }).first();
    if (!p) throw new NotFoundError("Post not found");
    if (p.user_id !== req.user.userId)
      throw new ForbiddenError("You can only update your own posts");
    await db("posts").where({ id: req.params.id }).update(updates);
    await cache.delete(`post:${req.params.id}`);
    res.json(await db("posts").where({ id: req.params.id }).first());
  }),
);
app.delete(
  "/posts/:id",
  authMiddleware,
  asyncHandler(async (req, res) => {
    const p = await db("posts").where({ id: req.params.id }).first();
    if (!p) throw new NotFoundError("Post not found");
    if (p.user_id !== req.user.userId)
      throw new ForbiddenError("You can only delete your own posts");
    await db("posts").where({ id: req.params.id }).delete();
    await cache.delete(`post:${req.params.id}`);
    res.status(204).end();
  }),
);

app.get(
  "/users/:id/posts",
  asyncHandler(async (req, res) => {
    const { limit, offset } = paginate(req);
    const [posts, c] = await Promise.all([
      db("posts")
        .where({ user_id: req.params.id })
        .orderBy("created_at", "desc")
        .limit(limit)
        .offset(offset),
      db("posts")
        .where({ user_id: req.params.id })
        .count("id as count")
        .first(),
    ]);
    res.json({ data: posts, meta: meta(c.count, limit, offset) });
  }),
);
app.post(
  "/users/:id/posts",
  authMiddleware,
  upload.single("image"),
  validate(postCreateSchema),
  asyncHandler(async (req, res) => {
    if (Number(req.params.id) !== req.user.userId)
      throw new ForbiddenError("You can only post as yourself");
    const { title, body } = req.validated;
    const imageUrl = req.file ? `/uploads/${req.file.filename}` : null;
    const [id] = await db("posts").insert({
      user_id: req.user.userId,
      title,
      body,
      image_url: imageUrl,
      created_at: Date.now(),
    });
    res
      .status(201)
      .json({ id, userId: req.user.userId, title, body, imageUrl });
  }),
);

// Voice channel page (project 32)
app.get("/:channel", (req, res) => {
  if (req.params.channel === "favicon.ico") return res.status(404).end();
  res.sendFile(path.join(__dirname, "voice.html"));
});

app.use(errorHandler);

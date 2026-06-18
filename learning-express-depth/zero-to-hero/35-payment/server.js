// server.js
//
// Project 35: The Payment
// ========================
// Stripe Checkout. We do NOT touch card data — Stripe's hosted page does.
// The flow: client calls /subscriptions/checkout, we create a Stripe Checkout
// Session, return its URL, the client redirects the user to Stripe, the user
// pays, Stripe redirects them to our success/cancel page, AND fires a webhook
// to /subscriptions/webhook. That webhook is the source of truth for whether
// the payment actually happened — never trust the redirect.
//
// Why raw body? Stripe's signature verification computes HMAC over the exact
// raw bytes of the request. If Express parses the body as JSON first, the
// raw bytes are lost and the signature will not match. So we mount
// express.raw() ONLY on the webhook route, before the global json parser.
//
// Setup:
//   export STRIPE_SECRET_KEY=sk_test_...
//   export STRIPE_WEBHOOK_SECRET=whsec_...
//   redis-server
//   npm install ioredis rate-limiter-flexible node-cron bullmq ws y-websocket yjs stripe
//   node server.js

const express = require("express");
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
const { setupWSConnection: setupYjs } = require("y-websocket/bin/utils");
const Stripe = require("stripe");

const SECRET = "dev-secret-change-in-prod";
const TOKEN_TTL = "7d";
const PRESENCE_CHANNEL = "presence:updates";
const PRESENCE_TTL = 30;
const HEARTBEAT_INTERVAL = 10;
const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY || "sk_test_placeholder";
const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET || "whsec_placeholder";
const STRIPE_PRICE_ID = process.env.STRIPE_PRICE_ID || "price_placeholder";
const APP_URL = process.env.APP_URL || "http://localhost:3000";
const stripe = new Stripe(STRIPE_SECRET_KEY, { apiVersion: "2024-06-20" });

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
  { connection: redis }
);
emailWorker.on("failed", (job, err) =>
  logger.error({ err: err.message }, "Email job failed")
);

const webhookDeliveryQueue = new Queue("webhook-delivery", { connection: redis });
const webhookDeliveryWorker = new Worker(
  "webhook-delivery",
  async (job) => {
    const { url, secret, payload, event } = job.data;
    const body = JSON.stringify(payload);
    const ts = Date.now();
    const signed = `${ts}.${body}`;
    const sig = crypto.createHmac("sha256", secret).update(signed).digest("hex");
    const start = Date.now();
    let res;
    try {
      res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Webhook-Event": event,
          "X-Webhook-Signature": `t=${ts},v1=${sig}`,
          "X-Webhook-Delivery": job.id,
        },
        body,
        signal: AbortSignal.timeout(10000),
      });
    } catch (err) {
      logger.warn(
        { err: err.message, url, event, attempt: job.attemptsMade + 1 },
        "Webhook delivery failed"
      );
      throw err;
    }
    const ms = Date.now() - start;
    if (res.status >= 200 && res.status < 300) {
      logger.info(
        { url, event, status: res.status, ms, attempt: job.attemptsMade + 1 },
        "Webhook delivered"
      );
      return { status: res.status, ms };
    } else {
      logger.warn(
        { url, event, status: res.status, ms, attempt: job.attemptsMade + 1 },
        "Webhook receiver returned error"
      );
      throw new Error(`HTTP ${res.status}`);
    }
  },
  { connection: redis }
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
        ttlSeconds || this.ttl
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

async function setOnline(userId) {
  await redis.set(`presence:${userId}`, Date.now(), "EX", PRESENCE_TTL);
  await redis.publish(
    PRESENCE_CHANNEL,
    JSON.stringify({ type: "connect", userId })
  );
}
async function setOffline(userId) {
  await redis.del(`presence:${userId}`);
  await redis.publish(
    PRESENCE_CHANNEL,
    JSON.stringify({ type: "disconnect", userId })
  );
}
async function refreshPresence(userId) {
  await redis.expire(`presence:${userId}`, PRESENCE_TTL);
}
async function getOnlineUsers() {
  const keys = await redis.keys("presence:*");
  return keys.map((k) => parseInt(k.split(":")[1]));
}

const roleHierarchy = { owner: 4, admin: 3, member: 2, guest: 1 };
function hasPermission(actual, required) {
  return roleHierarchy[actual] >= roleHierarchy[required];
}
function requireRole(role) {
  return async (req, res, next) => {
    try {
      const member = await db("workspace_members")
        .where({
          workspace_id: req.params.workspaceId,
          user_id: req.user.userId,
        })
        .first();
      if (!member) throw new ForbiddenError("Not a member");
      if (!hasPermission(member.role, role))
        throw new ForbiddenError(`Requires role: ${role}`);
      req.workspaceRole = member.role;
      next();
    } catch (err) {
      next(err);
    }
  };
}

async function fireWebhook(event, data) {
  const webhooks = await db("webhooks").where({ active: 1 });
  const matching = webhooks.filter((w) => {
    const events = JSON.parse(w.events || "[]");
    return events.includes(event) || events.includes("*");
  });
  if (matching.length === 0) return;
  const payload = {
    id: crypto.randomUUID(),
    event,
    created: Math.floor(Date.now() / 1000),
    data,
  };
  for (const w of matching) {
    await webhookDeliveryQueue.add(
      event,
      { url: w.url, secret: w.secret, payload, event },
      {
        attempts: 5,
        backoff: { type: "exponential", delay: 1000 },
        removeOnComplete: { count: 1000 },
        removeOnFail: { count: 5000 },
      }
    );
  }
}

const app = express();
app.set("trust proxy", 1);

// PROJECT 35: raw body for Stripe webhook — must come BEFORE express.json()
app.post(
  "/subscriptions/webhook",
  express.raw({ type: "application/json" }),
  asyncHandler(async (req, res) => {
    const sig = req.headers["stripe-signature"];
    let event;
    try {
      event = stripe.webhooks.constructEvent(req.body, sig, STRIPE_WEBHOOK_SECRET);
    } catch (err) {
      logger.warn({ err: err.message }, "Stripe signature verification failed");
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }
    logger.info({ type: event.type, id: event.id }, "Stripe webhook received");
    switch (event.type) {
      case "checkout.session.completed": {
        const session = event.data.object;
        const userId = parseInt(session.client_reference_id);
        if (userId) {
          await db("subscriptions")
            .insert({
              user_id: userId,
              stripe_customer_id: session.customer,
              stripe_subscription_id: session.subscription,
              plan: "pro",
              status: "active",
              current_period_end:
                (Date.now() / 1000 + 30 * 24 * 3600) | 0,
              created_at: Date.now(),
            })
            .onConflict("user_id")
            .merge();
          fireWebhook("subscription.activated", { userId, sessionId: session.id });
        }
        break;
      }
      case "customer.subscription.updated":
      case "customer.subscription.deleted": {
        const sub = event.data.object;
        await db("subscriptions")
          .where({ stripe_subscription_id: sub.id })
          .update({
            status: sub.status,
            current_period_end: sub.current_period_end,
          });
        fireWebhook("subscription.updated", { status: sub.status });
        break;
      }
      case "invoice.payment_failed": {
        const inv = event.data.object;
        await db("subscriptions")
          .where({ stripe_customer_id: inv.customer })
          .update({ status: "past_due" });
        fireWebhook("subscription.payment_failed", { customer: inv.customer });
        break;
      }
    }
    res.json({ received: true });
  })
);

// Now global json parser
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
  await db.schema.createTableIfNotExists("users", (t) => {
    t.increments("id").primary();
    t.string("username").unique().notNullable();
    t.string("hash").notNullable();
    t.string("email").unique();
    t.bigInteger("created_at").notNullable();
    t.integer("balance").notNullable().defaultTo(0);
    t.string("stripe_customer_id");
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
    t.string("image_url");
    t.bigInteger("created_at").notNullable();
  });
  await db.schema.createTableIfNotExists("workspaces", (t) => {
    t.increments("id").primary();
    t.string("name").notNullable();
    t.integer("owner_id")
      .notNullable()
      .references("id")
      .inTable("users");
    t.bigInteger("created_at").notNullable();
  });
  await db.schema.createTableIfNotExists("workspace_members", (t) => {
    t.integer("workspace_id")
      .notNullable()
      .references("id")
      .inTable("workspaces")
      .onDelete("CASCADE");
    t.integer("user_id")
      .notNullable()
      .references("id")
      .inTable("users")
      .onDelete("CASCADE");
    t.string("role").notNullable();
    t.primary(["workspace_id", "user_id"]);
  });
  await db.schema.createTableIfNotExists("webhooks", (t) => {
    t.increments("id").primary();
    t.integer("owner_id")
      .notNullable()
      .references("id")
      .inTable("users")
      .onDelete("CASCADE");
    t.text("url").notNullable();
    t.string("secret").notNullable();
    t.text("events").notNullable();
    t.integer("active").notNullable().defaultTo(1);
    t.bigInteger("created_at").notNullable();
  });
  // PROJECT 35: subscriptions table
  await db.schema.createTableIfNotExists("subscriptions", (t) => {
    t.increments("id").primary();
    t.integer("user_id")
      .notNullable()
      .unique()
      .references("id")
      .inTable("users")
      .onDelete("CASCADE");
    t.string("stripe_customer_id");
    t.string("stripe_subscription_id");
    t.string("plan").notNullable();
    t.string("status").notNullable();
    t.bigInteger("current_period_end");
    t.bigInteger("created_at").notNullable();
  });
}
migrate().then(() => {
  const server = app.listen(3000, () =>
    logger.info("Server listening on http://localhost:3000")
  );

  const subscriber = redis.duplicate();
  subscriber.subscribe(PRESENCE_CHANNEL);
  subscriber.on("message", (channel, message) => {
    const event = JSON.parse(message);
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({ type: "presence", event }));
      }
    });
  });

  const wss = new WebSocketServer({ server });
  wss.on("connection", async (ws, req) => {
    const url = new URL(req.url, "http://localhost");
    const token = url.searchParams.get("token");
    let user;
    try {
      user = jwt.verify(token, SECRET);
    } catch (err) {
      ws.close(1008, "Unauthorized");
      return;
    }
    await setOnline(user.userId);
    const online = await getOnlineUsers();
    ws.send(JSON.stringify({ type: "presence:list", users: online }));
    const heartbeat = setInterval(
      () => refreshPresence(user.userId),
      HEARTBEAT_INTERVAL * 1000
    );
    ws.on("message", (data) => {
      try {
        const message = JSON.parse(data.toString());
        if (message.type === "chat") {
          wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(
                JSON.stringify({
                  type: "chat",
                  user: message.user,
                  text: message.text,
                  timestamp: Date.now(),
                })
              );
            }
          });
        }
      } catch (err) {
        logger.error({ err: err.message }, "Failed to parse WebSocket message");
      }
    });
    ws.on("close", async () => {
      clearInterval(heartbeat);
      await setOffline(user.userId);
    });
  });

  const yWss = new WebSocketServer({ noServer: true });
  yWss.on("connection", setupYjs);
  server.on("upgrade", (req, socket, head) => {
    const url = new URL(req.url, "http://localhost");
    if (url.pathname === "/" || url.pathname === "/chat") {
      wss.handleUpgrade(req, socket, head, (ws) =>
        wss.emit("connection", ws, req)
      );
    } else {
      yWss.handleUpgrade(req, socket, head, (ws) =>
        yWss.emit("connection", ws, req)
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
  return (req, res, next) =>
    Promise.resolve(fn(req, res, next)).catch(next);
}

function errorHandler(err, req, res, next) {
  req.log.error(
    { err: err.message, code: err.code, status: err.status },
    err.message
  );
  if (err instanceof HttpError) {
    const body = { error: err.message, code: err.code };
    if (err.issues) body.issues = err.issues;
    return res.status(err.status).json(body);
  }
  res
    .status(500)
    .json({ error: "Internal Server Error", code: "INTERNAL" });
}

const userCreateSchema = z.object({
  username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/),
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
const workspaceCreateSchema = z.object({
  name: z.string().min(1).max(100),
});
const memberAddSchema = z.object({
  userId: z.number().int().positive(),
  role: z.enum(["admin", "member", "guest"]),
});
const memberUpdateSchema = z.object({
  role: z.enum(["admin", "member", "guest"]),
});
const webhookCreateSchema = z.object({
  url: z.string().url(),
  events: z.array(z.string().min(1)).min(1).max(50),
});
const webhookUpdateSchema = z.object({
  url: z.string().url().optional(),
  events: z.array(z.string().min(1)).min(1).max(50).optional(),
  active: z.boolean().optional(),
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
    return next(new UnauthorizedError("missing or invalid authorization header"));
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

app.get("/online", authMiddleware, asyncHandler(async (req, res) => {
  const online = await getOnlineUsers();
  res.json({ online });
}));

// PROJECT 35: subscription endpoints
app.post(
  "/subscriptions/checkout",
  authMiddleware,
  asyncHandler(async (req, res) => {
    const user = await db("users").where({ id: req.user.userId }).first();
    let customerId = user.stripe_customer_id;
    if (!customerId) {
      const customer = await stripe.customers.create({
        email: user.email,
        metadata: { userId: String(user.id), username: user.username },
      });
      customerId = customer.id;
      await db("users").where({ id: user.id }).update({ stripe_customer_id: customerId });
    }
    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      customer: customerId,
      line_items: [{ price: STRIPE_PRICE_ID, quantity: 1 }],
      success_url: `${APP_URL}/subscriptions/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${APP_URL}/subscriptions/cancel`,
      client_reference_id: String(req.user.userId),
    });
    res.json({ url: session.url, sessionId: session.id });
  })
);
app.get(
  "/subscriptions/me",
  authMiddleware,
  asyncHandler(async (req, res) => {
    const sub = await db("subscriptions")
      .where({ user_id: req.user.userId })
      .first();
    if (!sub) return res.json({ plan: "free", status: "inactive" });
    res.json({
      plan: sub.plan,
      status: sub.status,
      currentPeriodEnd: sub.current_period_end
        ? new Date(sub.current_period_end * 1000).toISOString()
        : null,
    });
  })
);
app.post(
  "/subscriptions/portal",
  authMiddleware,
  asyncHandler(async (req, res) => {
    const user = await db("users").where({ id: req.user.userId }).first();
    if (!user.stripe_customer_id)
      throw new NotFoundError("No billing account yet");
    const session = await stripe.billingPortal.sessions.create({
      customer: user.stripe_customer_id,
      return_url: `${APP_URL}/account`,
    });
    res.json({ url: session.url });
  })
);

app.post(
  "/webhooks",
  authMiddleware,
  validate(webhookCreateSchema),
  asyncHandler(async (req, res) => {
    const { url, events } = req.validated;
    const secret = `whsec_${crypto.randomBytes(24).toString("hex")}`;
    const [id] = await db("webhooks").insert({
      owner_id: req.user.userId,
      url,
      secret,
      events: JSON.stringify(events),
      active: 1,
      created_at: Date.now(),
    });
    res.status(201).json({
      id,
      url,
      events,
      secret,
      active: true,
      message: "Save the secret now. It will not be shown again.",
    });
  })
);
app.get(
  "/webhooks",
  authMiddleware,
  asyncHandler(async (req, res) => {
    const webhooks = await db("webhooks")
      .where({ owner_id: req.user.userId })
      .select("id", "url", "events", "active", "created_at");
    res.json({
      data: webhooks.map((w) => ({ ...w, events: JSON.parse(w.events) })),
    });
  })
);
app.patch(
  "/webhooks/:id",
  authMiddleware,
  validate(webhookUpdateSchema),
  asyncHandler(async (req, res) => {
    const updates = req.validated;
    if (Object.keys(updates).length === 0)
      throw new ValidationError([
        { path: "", message: "no fields to update" },
      ]);
    const w = await db("webhooks")
      .where({ id: req.params.id, owner_id: req.user.userId })
      .first();
    if (!w) throw new NotFoundError("Webhook not found");
    const set = {};
    if (updates.url !== undefined) set.url = updates.url;
    if (updates.events !== undefined)
      set.events = JSON.stringify(updates.events);
    if (updates.active !== undefined) set.active = updates.active ? 1 : 0;
    await db("webhooks").where({ id: req.params.id }).update(set);
    res.json({ message: "Webhook updated" });
  })
);
app.delete(
  "/webhooks/:id",
  authMiddleware,
  asyncHandler(async (req, res) => {
    const w = await db("webhooks")
      .where({ id: req.params.id, owner_id: req.user.userId })
      .first();
    if (!w) throw new NotFoundError("Webhook not found");
    await db("webhooks").where({ id: req.params.id }).delete();
    res.status(204).end();
  })
);

app.post(
  "/workspaces",
  authMiddleware,
  validate(workspaceCreateSchema),
  asyncHandler(async (req, res) => {
    const { name } = req.validated;
    const [id] = await db("workspaces").insert({
      name,
      owner_id: req.user.userId,
      created_at: Date.now(),
    });
    await db("workspace_members").insert({
      workspace_id: id,
      user_id: req.user.userId,
      role: "owner",
    });
    fireWebhook("workspace.created", { id, name, ownerId: req.user.userId });
    res.status(201).json({ id, name });
  })
);

app.get(
  "/workspaces/:workspaceId",
  authMiddleware,
  requireRole("guest"),
  asyncHandler(async (req, res) => {
    const ws = await db("workspaces")
      .where({ id: req.params.workspaceId })
      .first();
    if (!ws) throw new NotFoundError("Workspace not found");
    res.json(ws);
  })
);

app.post(
  "/workspaces/:workspaceId/members",
  authMiddleware,
  requireRole("admin"),
  validate(memberAddSchema),
  asyncHandler(async (req, res) => {
    const { userId, role } = req.validated;
    await db("workspace_members").insert({
      workspace_id: req.params.workspaceId,
      user_id: userId,
      role,
    });
    fireWebhook("workspace.member_added", {
      workspaceId: req.params.workspaceId,
      userId,
      role,
    });
    res.status(201).json({ message: "Member added" });
  })
);

app.patch(
  "/workspaces/:workspaceId/members/:userId",
  authMiddleware,
  requireRole("admin"),
  validate(memberUpdateSchema),
  asyncHandler(async (req, res) => {
    const { role } = req.validated;
    await db("workspace_members")
      .where({
        workspace_id: req.params.workspaceId,
        user_id: req.params.userId,
      })
      .update({ role });
    fireWebhook("workspace.role_changed", {
      workspaceId: req.params.workspaceId,
      userId: req.params.userId,
      role,
    });
    res.json({ message: "Role updated" });
  })
);

app.get(
  "/workspaces/:workspaceId/members",
  authMiddleware,
  requireRole("guest"),
  asyncHandler(async (req, res) => {
    const members = await db("workspace_members")
      .join("users", "workspace_members.user_id", "users.id")
      .where("workspace_members.workspace_id", req.params.workspaceId)
      .select(
        "users.id",
        "users.username",
        "users.email",
        "workspace_members.role"
      );
    res.json({ data: members });
  })
);

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
    if (email) {
      await emailQueue.add(
        "welcome",
        { userId: id, email, username },
        { attempts: 3, backoff: { type: "exponential", delay: 1000 } }
      );
    }
    fireWebhook("user.created", { id, username, email });
    res.status(201).json({ id, username, email: email || null });
  })
);

app.get("/users", asyncHandler(async (req, res) => {
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
}));
app.get("/users/:id", asyncHandler(async (req, res) => {
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
}));
app.patch(
  "/users/:id",
  authMiddleware,
  validate(userUpdateSchema),
  asyncHandler(async (req, res) => {
    if (Number(req.params.id) !== req.user.userId)
      throw new ForbiddenError("You can only update your own user");
    const updates = req.validated;
    if (Object.keys(updates).length === 0)
      throw new ValidationError([
        { path: "", message: "no fields to update" },
      ]);
    await db("users").where({ id: req.params.id }).update(updates);
    await cache.delete(`user:${req.params.id}`);
    fireWebhook("user.updated", {
      id: req.params.id,
      fields: Object.keys(updates),
    });
    const u = await db("users")
      .select("id", "username", "email", "balance", "created_at")
      .where({ id: req.params.id })
      .first();
    res.json(u);
  })
);
app.delete("/users/:id", authMiddleware, asyncHandler(async (req, res) => {
  if (Number(req.params.id) !== req.user.userId)
    throw new ForbiddenError("You can only delete your own user");
  await db("users").where({ id: req.params.id }).delete();
  await cache.delete(`user:${req.params.id}`);
  fireWebhook("user.deleted", { id: req.params.id });
  res.status(204).end();
}));

app.post(
  "/sessions",
  validate(sessionCreateSchema),
  asyncHandler(async (req, res) => {
    const { username, password } = req.validated;
    const u = await db("users").where({ username }).first();
    if (!u) throw new UnauthorizedError("invalid credentials");
    if (!(await bcrypt.compare(password, u.hash)))
      throw new UnauthorizedError("invalid credentials");
    const token = jwt.sign(
      { userId: u.id, username: u.username },
      SECRET,
      { expiresIn: TOKEN_TTL }
    );
    res.status(201).json({
      token,
      user: { id: u.id, username: u.username, email: u.email },
    });
  })
);
app.delete(
  "/sessions",
  authMiddleware,
  asyncHandler(async (req, res) => res.status(204).end())
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
  })
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
      await db("users").where({ id: u.id }).update({
        password_reset_token: h,
        password_reset_expires_at: Date.now() + 60 * 60 * 1000,
      });
      await emailQueue.add(
        "password-reset",
        { email, token: t },
        { attempts: 3, backoff: { type: "exponential", delay: 1000 } }
      );
    }
    res.json({ message: "If the email exists, a reset link has been sent" });
  })
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
    await db("users").where({ id: u.id }).update({
      hash: await bcrypt.hash(password, 10),
      password_reset_token: null,
      password_reset_expires_at: null,
    });
    await cache.delete(`user:${u.id}`);
    res.json({ message: "Password reset successful" });
  })
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
    fireWebhook("transfer.completed", { fromUserId, toUserId, amount });
    res.json({ message: "Transfer complete" });
  })
);

app.get("/posts", asyncHandler(async (req, res) => {
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
}));
app.get("/posts/:id", asyncHandler(async (req, res) => {
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
}));
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
    fireWebhook("post.created", { id, userId: req.user.userId, title });
    res.status(201).json({
      id,
      userId: req.user.userId,
      title,
      body,
      imageUrl,
    });
  })
);
app.patch(
  "/posts/:id",
  authMiddleware,
  validate(postUpdateSchema),
  asyncHandler(async (req, res) => {
    const updates = req.validated;
    if (Object.keys(updates).length === 0)
      throw new ValidationError([
        { path: "", message: "no fields to update" },
      ]);
    const p = await db("posts").where({ id: req.params.id }).first();
    if (!p) throw new NotFoundError("Post not found");
    if (p.user_id !== req.user.userId)
      throw new ForbiddenError("You can only update your own posts");
    await db("posts").where({ id: req.params.id }).update(updates);
    await cache.delete(`post:${req.params.id}`);
    fireWebhook("post.updated", { id: req.params.id, fields: Object.keys(updates) });
    res.json(await db("posts").where({ id: req.params.id }).first());
  })
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
    fireWebhook("post.deleted", { id: req.params.id });
    res.status(204).end();
  })
);

app.get("/users/:id/posts", asyncHandler(async (req, res) => {
  const { limit, offset } = paginate(req);
  const [posts, c] = await Promise.all([
    db("posts")
      .where({ user_id: req.params.id })
      .orderBy("created_at", "desc")
      .limit(limit)
      .offset(offset),
    db("posts").where({ user_id: req.params.id }).count("id as count").first(),
  ]);
  res.json({ data: posts, meta: meta(c.count, limit, offset) });
}));
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
    fireWebhook("post.created", { id, userId: req.user.userId, title });
    res.status(201).json({
      id,
      userId: req.user.userId,
      title,
      body,
      imageUrl,
    });
  })
);

app.use(errorHandler);

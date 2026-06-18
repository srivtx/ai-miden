// server.js
//
// Project 19: The Searcher
// =========================
// Adds FTS5 full-text search. Creates a posts_fts virtual table, indexes
// title and body, and adds ?q= to GET /posts. Results are ranked by BM25.
//
// Setup:
//   rm -f app.db
//   npm install knex better-sqlite3 zod pino pino-http pino-pretty
//   NODE_ENV=development node server.js
//
// (Migrations include the FTS table and triggers. Existing data is lost.)

const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const knex = require("knex");
const { z } = require("zod");
const pino = require("pino");
const pinoHttp = require("pino-http");

const SECRET = "dev-secret-change-in-prod";
const TOKEN_TTL = "7d";

const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  transport:
    process.env.NODE_ENV === "production"
      ? undefined
      : { target: "pino-pretty" },
});

const app = express();
app.use(express.json());
app.use(pinoHttp({ logger }));

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

  // FTS5 virtual table + triggers
  await db.raw(`
    CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
      title, body, content='posts', content_rowid='id'
    )
  `);

  await db.raw(`
    CREATE TRIGGER IF NOT EXISTS posts_ai AFTER INSERT ON posts BEGIN
      INSERT INTO posts_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
    END
  `);

  await db.raw(`
    CREATE TRIGGER IF NOT EXISTS posts_ad AFTER DELETE ON posts BEGIN
      INSERT INTO posts_fts(posts_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
    END
  `);

  await db.raw(`
    CREATE TRIGGER IF NOT EXISTS posts_au AFTER UPDATE ON posts BEGIN
      INSERT INTO posts_fts(posts_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
      INSERT INTO posts_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
    END
  `);
}

migrate().then(() => {
  app.listen(3000, () =>
    logger.info("Server listening on http://localhost:3000"),
  );
});

class HttpError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

class ValidationError extends HttpError {
  constructor(issues) {
    super(400, "VALIDATION", "Validation failed");
    this.issues = issues;
  }
}

class UnauthorizedError extends HttpError {
  constructor(message = "Unauthorized") {
    super(401, "UNAUTHORIZED", message);
  }
}

class ForbiddenError extends HttpError {
  constructor(message = "Forbidden") {
    super(403, "FORBIDDEN", message);
  }
}

class NotFoundError extends HttpError {
  constructor(message = "Not Found") {
    super(404, "NOT_FOUND", message);
  }
}

class ConflictError extends HttpError {
  constructor(message = "Conflict") {
    super(409, "CONFLICT", message);
  }
}

function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

function errorHandler(err, req, res, next) {
  req.log.error({ err, code: err.code, status: err.status }, err.message);
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

const postCreateSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1).max(10000),
});

const postUpdateSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  body: z.string().min(1).max(10000).optional(),
});

function validate(schema) {
  return (req, res, next) => {
    try {
      req.validated = schema.parse(req.body);
      next();
    } catch (err) {
      if (err.issues) {
        return next(new ValidationError(err.issues));
      }
      next(err);
    }
  };
}

function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith("Bearer ")) {
    return next(
      new UnauthorizedError("missing or invalid authorization header"),
    );
  }
  const token = auth.slice(7);
  try {
    req.user = jwt.verify(token, SECRET);
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

app.get("/", (req, res) => {
  res.json({ message: "Welcome to the API." });
});

app.post(
  "/users",
  validate(userCreateSchema),
  asyncHandler(async (req, res) => {
    const { username, password, email } = req.validated;
    const existing = await db("users").where({ username }).first();
    if (existing) {
      throw new ConflictError("username already taken");
    }
    const hash = await bcrypt.hash(password, 10);
    const [id] = await db("users").insert({
      username,
      hash,
      email: email || null,
      created_at: Date.now(),
    });
    res.status(201).json({ id, username, email: email || null });
  }),
);

app.get(
  "/users",
  asyncHandler(async (req, res) => {
    const { limit, offset } = paginate(req);
    const [users, countResult] = await Promise.all([
      db("users")
        .select("id", "username", "email", "created_at")
        .orderBy("created_at", "desc")
        .limit(limit)
        .offset(offset),
      db("users").count("id as count").first(),
    ]);
    res.json({ data: users, meta: meta(countResult.count, limit, offset) });
  }),
);

app.get(
  "/users/:id",
  asyncHandler(async (req, res) => {
    const user = await db("users")
      .select("id", "username", "email", "created_at")
      .where({ id: req.params.id })
      .first();
    if (!user) {
      throw new NotFoundError("User not found");
    }
    res.json(user);
  }),
);

app.patch(
  "/users/:id",
  authMiddleware,
  validate(userUpdateSchema),
  asyncHandler(async (req, res) => {
    if (Number(req.params.id) !== req.user.userId) {
      throw new ForbiddenError("You can only update your own user");
    }
    const updates = req.validated;
    if (Object.keys(updates).length === 0) {
      throw new ValidationError([{ path: "", message: "no fields to update" }]);
    }
    await db("users").where({ id: req.params.id }).update(updates);
    const user = await db("users")
      .select("id", "username", "email", "created_at")
      .where({ id: req.params.id })
      .first();
    res.json(user);
  }),
);

app.delete(
  "/users/:id",
  authMiddleware,
  asyncHandler(async (req, res) => {
    if (Number(req.params.id) !== req.user.userId) {
      throw new ForbiddenError("You can only delete your own user");
    }
    await db("users").where({ id: req.params.id }).delete();
    res.status(204).end();
  }),
);

app.post(
  "/sessions",
  validate(sessionCreateSchema),
  asyncHandler(async (req, res) => {
    const { username, password } = req.validated;
    const user = await db("users").where({ username }).first();
    if (!user) {
      throw new UnauthorizedError("invalid credentials");
    }
    const ok = await bcrypt.compare(password, user.hash);
    if (!ok) {
      throw new UnauthorizedError("invalid credentials");
    }
    const token = jwt.sign(
      { userId: user.id, username: user.username },
      SECRET,
      { expiresIn: TOKEN_TTL },
    );
    res.status(201).json({
      token,
      user: { id: user.id, username: user.username, email: user.email },
    });
  }),
);

app.delete(
  "/sessions",
  authMiddleware,
  asyncHandler(async (req, res) => {
    res.status(204).end();
  }),
);

app.get(
  "/sessions/me",
  authMiddleware,
  asyncHandler(async (req, res) => {
    const user = await db("users")
      .select("id", "username", "email", "created_at")
      .where({ id: req.user.userId })
      .first();
    if (!user) {
      throw new NotFoundError("User not found");
    }
    res.json(user);
  }),
);

app.get(
  "/posts",
  asyncHandler(async (req, res) => {
    const { limit, offset } = paginate(req);
    const q = req.query.q;

    let dataQuery;
    let countQuery;

    if (q) {
      dataQuery = db("posts_fts")
        .join("posts", "posts_fts.rowid", "posts.id")
        .join("users", "posts.user_id", "users.id")
        .select("posts.*", "users.username as author", "posts_fts.rank")
        .where("posts_fts", "MATCH", q)
        .orderBy("posts_fts.rank")
        .limit(limit)
        .offset(offset);
      countQuery = db("posts_fts")
        .where("posts_fts", "MATCH", q)
        .count("* as count")
        .first();
    } else {
      dataQuery = db("posts")
        .join("users", "posts.user_id", "users.id")
        .select("posts.*", "users.username as author")
        .orderBy("posts.created_at", "desc")
        .limit(limit)
        .offset(offset);
      countQuery = db("posts").count("id as count").first();
    }

    const [posts, countResult] = await Promise.all([dataQuery, countQuery]);
    res.json({ data: posts, meta: meta(countResult.count, limit, offset) });
  }),
);

app.get(
  "/posts/:id",
  asyncHandler(async (req, res) => {
    const post = await db("posts")
      .join("users", "posts.user_id", "users.id")
      .select("posts.*", "users.username as author")
      .where("posts.id", req.params.id)
      .first();
    if (!post) {
      throw new NotFoundError("Post not found");
    }
    res.json(post);
  }),
);

app.post(
  "/posts",
  authMiddleware,
  validate(postCreateSchema),
  asyncHandler(async (req, res) => {
    const { title, body } = req.validated;
    const [id] = await db("posts").insert({
      user_id: req.user.userId,
      title,
      body,
      created_at: Date.now(),
    });
    res.status(201).json({ id, userId: req.user.userId, title, body });
  }),
);

app.patch(
  "/posts/:id",
  authMiddleware,
  validate(postUpdateSchema),
  asyncHandler(async (req, res) => {
    const updates = req.validated;
    if (Object.keys(updates).length === 0) {
      throw new ValidationError([{ path: "", message: "no fields to update" }]);
    }
    const post = await db("posts").where({ id: req.params.id }).first();
    if (!post) {
      throw new NotFoundError("Post not found");
    }
    if (post.user_id !== req.user.userId) {
      throw new ForbiddenError("You can only update your own posts");
    }
    await db("posts").where({ id: req.params.id }).update(updates);
    const updated = await db("posts").where({ id: req.params.id }).first();
    res.json(updated);
  }),
);

app.delete(
  "/posts/:id",
  authMiddleware,
  asyncHandler(async (req, res) => {
    const post = await db("posts").where({ id: req.params.id }).first();
    if (!post) {
      throw new NotFoundError("Post not found");
    }
    if (post.user_id !== req.user.userId) {
      throw new ForbiddenError("You can only delete your own posts");
    }
    await db("posts").where({ id: req.params.id }).delete();
    res.status(204).end();
  }),
);

app.get(
  "/users/:id/posts",
  asyncHandler(async (req, res) => {
    const { limit, offset } = paginate(req);
    const [posts, countResult] = await Promise.all([
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
    res.json({ data: posts, meta: meta(countResult.count, limit, offset) });
  }),
);

app.post(
  "/users/:id/posts",
  authMiddleware,
  validate(postCreateSchema),
  asyncHandler(async (req, res) => {
    if (Number(req.params.id) !== req.user.userId) {
      throw new ForbiddenError("You can only post as yourself");
    }
    const { title, body } = req.validated;
    const [id] = await db("posts").insert({
      user_id: req.user.userId,
      title,
      body,
      created_at: Date.now(),
    });
    res.status(201).json({ id, userId: req.user.userId, title, body });
  }),
);

app.use(errorHandler);

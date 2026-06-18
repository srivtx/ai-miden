// server.js
//
// Project 16: The Logger
// =======================
// Adds structured JSON logging with pino. pino-http logs every request
// with method, URL, status, duration, and a request ID. The error wall
// logs errors with context. Logs are queryable and aggregatable.
//
// Setup:
//   npm install knex better-sqlite3 zod pino pino-http pino-pretty
//   NODE_ENV=development node server.js

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const knex = require('knex');
const { z } = require('zod');
const pino = require('pino');
const pinoHttp = require('pino-http');

const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'production' ? undefined : { target: 'pino-pretty' },
});

const app = express();
app.use(express.json());
app.use(pinoHttp({ logger }));

const db = knex({
  client: 'better-sqlite3',
  connection: { filename: 'app.db' },
  useNullAsDefault: true,
});

async function migrate() {
  await db.schema.createTableIfNotExists('users', (t) => {
    t.increments('id').primary();
    t.string('username').unique().notNullable();
    t.string('hash').notNullable();
    t.string('email').unique();
    t.bigInteger('created_at').notNullable();
  });

  await db.schema.createTableIfNotExists('posts', (t) => {
    t.increments('id').primary();
    t.integer('user_id').notNullable().references('id').inTable('users').onDelete('CASCADE');
    t.string('title').notNullable();
    t.text('body').notNullable();
    t.bigInteger('created_at').notNullable();
  });
}

migrate().then(() => {
  app.listen(3000, () => logger.info('Server listening on http://localhost:3000'));
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
    super(400, 'VALIDATION', 'Validation failed');
    this.issues = issues;
  }
}

class UnauthorizedError extends HttpError {
  constructor(message = 'Unauthorized') {
    super(401, 'UNAUTHORIZED', message);
  }
}

class NotFoundError extends HttpError {
  constructor(message = 'Not Found') {
    super(404, 'NOT_FOUND', message);
  }
}

class ConflictError extends HttpError {
  constructor(message = 'Conflict') {
    super(409, 'CONFLICT', message);
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
  res.status(500).json({ error: 'Internal Server Error', code: 'INTERNAL' });
}

const signupSchema = z.object({
  username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/),
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
        return next(new ValidationError(err.issues));
      }
      next(err);
    }
  };
}

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API.' });
});

app.post('/signup', validate(signupSchema), asyncHandler(async (req, res) => {
  const { username, password, email } = req.validated;
  const existing = await db('users').where({ username }).first();
  if (existing) {
    req.log.warn({ username }, 'signup conflict');
    throw new ConflictError('username already taken');
  }
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db('users').insert({ username, hash, email: email || null, created_at: Date.now() });
  req.log.info({ userId: id, username }, 'user created');
  res.status(201).json({ id, username, email: email || null });
}));

app.post('/login', validate(loginSchema), asyncHandler(async (req, res) => {
  const { username, password } = req.validated;
  const user = await db('users').where({ username }).first();
  if (!user) {
    throw new UnauthorizedError('invalid credentials');
  }
  const ok = await bcrypt.compare(password, user.hash);
  if (!ok) {
    throw new UnauthorizedError('invalid credentials');
  }
  const token = jwt.sign({ userId: user.id, username: user.username }, SECRET, { expiresIn: TOKEN_TTL });
  req.log.info({ userId: user.id, username }, 'user logged in');
  res.json({ token, user: { id: user.id, username: user.username, email: user.email } });
}));

function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) {
    return next(new UnauthorizedError('missing or invalid authorization header'));
  }
  const token = auth.slice(7);
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (err) {
    return next(new UnauthorizedError('invalid or expired token'));
  }
}

app.post('/posts', authMiddleware, validate(postSchema), asyncHandler(async (req, res) => {
  const { title, body } = req.validated;
  const [id] = await db('posts').insert({ user_id: req.user.userId, title, body, created_at: Date.now() });
  req.log.info({ postId: id, userId: req.user.userId, title }, 'post created');
  res.status(201).json({ id, userId: req.user.userId, title, body });
}));

app.get('/posts', asyncHandler(async (req, res) => {
  const posts = await db('posts')
    .join('users', 'posts.user_id', 'users.id')
    .select('posts.*', 'users.username as author')
    .orderBy('posts.created_at', 'desc');
  res.json(posts);
}));

app.get('/posts/:id', asyncHandler(async (req, res) => {
  const post = await db('posts')
    .join('users', 'posts.user_id', 'users.id')
    .select('posts.*', 'users.username as author')
    .where('posts.id', req.params.id)
    .first();
  if (!post) {
    throw new NotFoundError('Post not found');
  }
  res.json(post);
}));

app.get('/users/:id/posts', asyncHandler(async (req, res) => {
  const posts = await db('posts').where({ user_id: req.params.id }).orderBy('created_at', 'desc');
  res.json(posts);
}));

app.use(errorHandler);

// server.js
//
// Project 23: The Redis Switch
// =============================
// Replaces in-memory cache with Redis. Shared across processes. Same
// Cache API (get, set, delete). Async. Fail open on errors.
//
// Setup:
//   brew install redis
//   redis-server
//   npm install ioredis
//   node server.js
//
// Test:
//   redis-cli ping
//   curl http://localhost:3000/posts/1
//   redis-cli get post:1

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const knex = require('knex');
const { z } = require('zod');
const pino = require('pino');
const pinoHttp = require('pino-http');
const multer = require('multer');
const path = require('node:path');
const fs = require('node:fs');
const crypto = require('node:crypto');
const nodemailer = require('nodemailer');
const Redis = require('ioredis');

const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const UPLOADS_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR);

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'production' ? undefined : { target: 'pino-pretty' },
});

const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT) || 6379,
  password: process.env.REDIS_PASSWORD,
});
redis.on('error', (err) => logger.error({ err: err.message }, 'Redis error'));
redis.on('connect', () => logger.info('Connected to Redis'));

class Cache {
  constructor(redis, ttlSeconds = 60) {
    this.redis = redis;
    this.ttl = ttlSeconds;
  }
  async get(key) {
    try {
      const value = await this.redis.get(key);
      return value ? JSON.parse(value) : undefined;
    } catch (err) {
      logger.error({ err: err.message, key }, 'Cache get error');
      return undefined;
    }
  }
  async set(key, value, ttlSeconds) {
    try {
      const ttl = ttlSeconds || this.ttl;
      await this.redis.set(key, JSON.stringify(value), 'EX', ttl);
    } catch (err) {
      logger.error({ err: err.message, key }, 'Cache set error');
    }
  }
  async delete(key) {
    try {
      await this.redis.del(key);
    } catch (err) {
      logger.error({ err: err.message, key }, 'Cache delete error');
    }
  }
}

const cache = new Cache(redis, 60);

const app = express();
app.use(express.json());
app.use(pinoHttp({ logger }));
app.use('/uploads', express.static(UPLOADS_DIR));

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
      host: 'smtp.ethereal.email',
      port: 587,
      auth: { user: testAccount.user, pass: testAccount.pass },
    });
  }
}
setupMailer();

async function sendEmail({ to, subject, text, html }) {
  const info = await transporter.sendMail({ from: '"MyApp" <noreply@myapp.com>', to, subject, text, html });
  const url = nodemailer.getTestMessageUrl(info);
  if (url) logger.info({ url }, 'Preview email at:');
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS_DIR),
  filename: (req, file, cb) => { cb(null, `${crypto.randomUUID()}${path.extname(file.originalname)}`); },
});
const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    if (!file.mimetype.startsWith('image/')) return cb(new Error('Only images allowed'));
    cb(null, true);
  },
});

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
    t.string('image_url');
    t.bigInteger('created_at').notNullable();
  });
}

migrate().then(() => {
  app.listen(3000, () => logger.info('Server listening on http://localhost:3000'));
});

class HttpError extends Error { constructor(s, c, m) { super(m); this.status = s; this.code = c; } }
class ValidationError extends HttpError { constructor(i) { super(400, 'VALIDATION', 'Validation failed'); this.issues = i; } }
class UnauthorizedError extends HttpError { constructor(m = 'Unauthorized') { super(401, 'UNAUTHORIZED', m); } }
class ForbiddenError extends HttpError { constructor(m = 'Forbidden') { super(403, 'FORBIDDEN', m); } }
class NotFoundError extends HttpError { constructor(m = 'Not Found') { super(404, 'NOT_FOUND', m); } }
class ConflictError extends HttpError { constructor(m = 'Conflict') { super(409, 'CONFLICT', m); } }

function asyncHandler(fn) { return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next); }

function errorHandler(err, req, res, next) {
  req.log.error({ err: err.message, code: err.code, status: err.status }, err.message);
  if (err instanceof HttpError) {
    const body = { error: err.message, code: err.code };
    if (err.issues) body.issues = err.issues;
    return res.status(err.status).json(body);
  }
  res.status(500).json({ error: 'Internal Server Error', code: 'INTERNAL' });
}

const userCreateSchema = z.object({ username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/), password: z.string().min(8).max(100), email: z.string().email().optional() });
const userUpdateSchema = z.object({ username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/).optional(), email: z.string().email().optional() });
const sessionCreateSchema = z.object({ username: z.string().min(1), password: z.string().min(1) });
const forgotPasswordSchema = z.object({ email: z.string().email() });
const resetPasswordSchema = z.object({ token: z.string().min(1), password: z.string().min(8).max(100) });
const postCreateSchema = z.object({ title: z.string().min(1).max(200), body: z.string().min(1).max(10000) });
const postUpdateSchema = z.object({ title: z.string().min(1).max(200).optional(), body: z.string().min(1).max(10000).optional() });

function validate(schema) { return (req, res, next) => { try { req.validated = schema.parse(req.body); next(); } catch (err) { if (err.issues) return next(new ValidationError(err.issues)); next(err); } }; }

function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) return next(new UnauthorizedError('missing or invalid authorization header'));
  try { req.user = jwt.verify(auth.slice(7), SECRET); next(); } catch (err) { return next(new UnauthorizedError('invalid or expired token')); }
}

function paginate(req) { const limit = Math.min(parseInt(req.query.limit) || 20, 100); const offset = parseInt(req.query.offset) || 0; return { limit, offset }; }
function meta(total, limit, offset) { return { total, limit, offset, page: Math.floor(offset / limit) + 1, totalPages: Math.ceil(total / limit) }; }

app.get('/', (req, res) => res.json({ message: 'Welcome to the API.' }));

app.post('/users', validate(userCreateSchema), asyncHandler(async (req, res) => {
  const { username, password, email } = req.validated;
  if (await db('users').where({ username }).first()) throw new ConflictError('username already taken');
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db('users').insert({ username, hash, email: email || null, created_at: Date.now() });
  if (email) await sendEmail({ to: email, subject: 'Welcome!', text: `Welcome, ${username}!`, html: `<p>Welcome, ${username}!</p>` });
  res.status(201).json({ id, username, email: email || null });
}));

app.get('/users', asyncHandler(async (req, res) => {
  const { limit, offset } = paginate(req);
  const [users, countResult] = await Promise.all([
    db('users').select('id', 'username', 'email', 'created_at').orderBy('created_at', 'desc').limit(limit).offset(offset),
    db('users').count('id as count').first(),
  ]);
  res.json({ data: users, meta: meta(countResult.count, limit, offset) });
}));

app.get('/users/:id', asyncHandler(async (req, res) => {
  const cacheKey = `user:${req.params.id}`;
  const cached = await cache.get(cacheKey);
  if (cached) return res.json(cached);
  const user = await db('users').select('id', 'username', 'email', 'created_at').where({ id: req.params.id }).first();
  if (!user) throw new NotFoundError('User not found');
  await cache.set(cacheKey, user);
  res.json(user);
}));

app.patch('/users/:id', authMiddleware, validate(userUpdateSchema), asyncHandler(async (req, res) => {
  if (Number(req.params.id) !== req.user.userId) throw new ForbiddenError('You can only update your own user');
  const updates = req.validated;
  if (Object.keys(updates).length === 0) throw new ValidationError([{ path: '', message: 'no fields to update' }]);
  await db('users').where({ id: req.params.id }).update(updates);
  await cache.delete(`user:${req.params.id}`);
  const user = await db('users').select('id', 'username', 'email', 'created_at').where({ id: req.params.id }).first();
  res.json(user);
}));

app.delete('/users/:id', authMiddleware, asyncHandler(async (req, res) => {
  if (Number(req.params.id) !== req.user.userId) throw new ForbiddenError('You can only delete your own user');
  await db('users').where({ id: req.params.id }).delete();
  await cache.delete(`user:${req.params.id}`);
  res.status(204).end();
}));

app.post('/sessions', validate(sessionCreateSchema), asyncHandler(async (req, res) => {
  const { username, password } = req.validated;
  const user = await db('users').where({ username }).first();
  if (!user) throw new UnauthorizedError('invalid credentials');
  if (!await bcrypt.compare(password, user.hash)) throw new UnauthorizedError('invalid credentials');
  const token = jwt.sign({ userId: user.id, username: user.username }, SECRET, { expiresIn: TOKEN_TTL });
  res.status(201).json({ token, user: { id: user.id, username: user.username, email: user.email } });
}));

app.delete('/sessions', authMiddleware, asyncHandler(async (req, res) => res.status(204).end()));

app.get('/sessions/me', authMiddleware, asyncHandler(async (req, res) => {
  const cacheKey = `user:${req.user.userId}`;
  const cached = await cache.get(cacheKey);
  if (cached) return res.json(cached);
  const user = await db('users').select('id', 'username', 'email', 'created_at').where({ id: req.user.userId }).first();
  if (!user) throw new NotFoundError('User not found');
  await cache.set(cacheKey, user);
  res.json(user);
}));

app.post('/sessions/forgot', validate(forgotPasswordSchema), asyncHandler(async (req, res) => {
  const { email } = req.validated;
  const user = await db('users').where({ email }).first();
  if (user) {
    const resetToken = crypto.randomBytes(32).toString('hex');
    const hashedToken = crypto.createHash('sha256').update(resetToken).digest('hex');
    await db('users').where({ id: user.id }).update({ password_reset_token: hashedToken, password_reset_expires_at: Date.now() + 60 * 60 * 1000 });
    await sendEmail({ to: email, subject: 'Reset', text: `http://localhost:3000/sessions/reset?token=${resetToken}`, html: `<a href="http://localhost:3000/sessions/reset?token=${resetToken}">reset</a>` });
  }
  res.json({ message: 'If the email exists, a reset link has been sent' });
}));

app.post('/sessions/reset', validate(resetPasswordSchema), asyncHandler(async (req, res) => {
  const { token, password } = req.validated;
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex');
  const user = await db('users').where({ password_reset_token: hashedToken }).first();
  if (!user || user.password_reset_expires_at < Date.now()) throw new ValidationError([{ path: 'token', message: 'invalid or expired token' }]);
  const hash = await bcrypt.hash(password, 10);
  await db('users').where({ id: user.id }).update({ hash, password_reset_token: null, password_reset_expires_at: null });
  await cache.delete(`user:${user.id}`);
  res.json({ message: 'Password reset successful' });
}));

app.get('/posts', asyncHandler(async (req, res) => {
  const { limit, offset } = paginate(req);
  const [posts, countResult] = await Promise.all([
    db('posts').join('users', 'posts.user_id', 'users.id').select('posts.*', 'users.username as author').orderBy('posts.created_at', 'desc').limit(limit).offset(offset),
    db('posts').count('id as count').first(),
  ]);
  res.json({ data: posts, meta: meta(countResult.count, limit, offset) });
}));

app.get('/posts/:id', asyncHandler(async (req, res) => {
  const cacheKey = `post:${req.params.id}`;
  const cached = await cache.get(cacheKey);
  if (cached) return res.json(cached);
  const post = await db('posts').join('users', 'posts.user_id', 'users.id').select('posts.*', 'users.username as author').where('posts.id', req.params.id).first();
  if (!post) throw new NotFoundError('Post not found');
  await cache.set(cacheKey, post);
  res.json(post);
}));

app.post('/posts', authMiddleware, upload.single('image'), validate(postCreateSchema), asyncHandler(async (req, res) => {
  const { title, body } = req.validated;
  const imageUrl = req.file ? `/uploads/${req.file.filename}` : null;
  const [id] = await db('posts').insert({ user_id: req.user.userId, title, body, image_url: imageUrl, created_at: Date.now() });
  res.status(201).json({ id, userId: req.user.userId, title, body, imageUrl });
}));

app.patch('/posts/:id', authMiddleware, validate(postUpdateSchema), asyncHandler(async (req, res) => {
  const updates = req.validated;
  if (Object.keys(updates).length === 0) throw new ValidationError([{ path: '', message: 'no fields to update' }]);
  const post = await db('posts').where({ id: req.params.id }).first();
  if (!post) throw new NotFoundError('Post not found');
  if (post.user_id !== req.user.userId) throw new ForbiddenError('You can only update your own posts');
  await db('posts').where({ id: req.params.id }).update(updates);
  await cache.delete(`post:${req.params.id}`);
  const updated = await db('posts').where({ id: req.params.id }).first();
  res.json(updated);
}));

app.delete('/posts/:id', authMiddleware, asyncHandler(async (req, res) => {
  const post = await db('posts').where({ id: req.params.id }).first();
  if (!post) throw new NotFoundError('Post not found');
  if (post.user_id !== req.user.userId) throw new ForbiddenError('You can only delete your own posts');
  await db('posts').where({ id: req.params.id }).delete();
  await cache.delete(`post:${req.params.id}`);
  res.status(204).end();
}));

app.get('/users/:id/posts', asyncHandler(async (req, res) => {
  const { limit, offset } = paginate(req);
  const [posts, countResult] = await Promise.all([
    db('posts').where({ user_id: req.params.id }).orderBy('created_at', 'desc').limit(limit).offset(offset),
    db('posts').where({ user_id: req.params.id }).count('id as count').first(),
  ]);
  res.json({ data: posts, meta: meta(countResult.count, limit, offset) });
}));

app.post('/users/:id/posts', authMiddleware, upload.single('image'), validate(postCreateSchema), asyncHandler(async (req, res) => {
  if (Number(req.params.id) !== req.user.userId) throw new ForbiddenError('You can only post as yourself');
  const { title, body } = req.validated;
  const imageUrl = req.file ? `/uploads/${req.file.filename}` : null;
  const [id] = await db('posts').insert({ user_id: req.user.userId, title, body, image_url: imageUrl, created_at: Date.now() });
  res.status(201).json({ id, userId: req.user.userId, title, body, imageUrl });
}));

app.use(errorHandler);

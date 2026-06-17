// 12_logging.js — Structured logging: simple console, morgan, winston, levels, correlation IDs.
const express = require('express');
const morgan = require('morgan');
const winston = require('winston');
const { v4: uuidv4 } = require('uuid');
const app = express();

// ---- Level 1: Morgan (simple HTTP request logging) ----
app.use(morgan('dev')); // :method :url :status :response-time ms - :res[content-length]

// ---- Level 2: Winston (structured JSON, log levels, file output) ----
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
  transports: [
    new winston.transports.Console({ format: winston.format.combine(winston.format.colorize(), winston.format.simple()) }),
    new winston.transports.File({ filename: 'app.log', maxsize: 10 * 1024 * 1024, maxFiles: 5 }),
  ],
});

// ---- Level 3: Correlation IDs (trace a request through logs) ----
app.use((req, res, next) => {
  req.correlationId = req.headers['x-correlation-id'] || uuidv4();
  res.set('X-Correlation-ID', req.correlationId);
  res.locals.logger = logger.child({ correlationId: req.correlationId, method: req.method, url: req.url });
  next();
});

// ---- Using different log levels ----
app.get('/api/data', (req, res) => {
  logger.info('Fetching data', { userId: req.query.userId, correlationId: req.correlationId });
  try {
    const data = [1, 2, 3];
    logger.debug('Data retrieved', { count: data.length });
    res.json({ data });
  } catch (err) {
    logger.error('Data fetch failed', { error: err.message, stack: err.stack });
    res.status(500).json({ error: 'Internal' });
  }
});

app.post('/api/risky', (req, res) => {
  logger.warn('Risky operation attempted', { body: req.body, ip: req.ip });
  res.json({ status: 'processed' });
});

app.get('/health', (req, res) => {
  logger.verbose('Health check'); // won't show at 'info' level
  res.json({ status: 'ok' });
});

app.listen(3000, () => {
  logger.info('Server started', { port: 3000, env: process.env.NODE_ENV || 'development' });
  console.log('http://localhost:3000');
});

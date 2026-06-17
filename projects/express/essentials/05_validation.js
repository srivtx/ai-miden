// 05_validation.js — Request validation with Joi. Guard every endpoint.

const express = require('express');
const Joi = require('joi');
const app = express();
app.use(express.json());

// Reusable middleware factory: validate body against a Joi schema
function validate(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body, { abortEarly: false, stripUnknown: true });
    if (error) return res.status(400).json({ errors: error.details.map(d => d.message) });
    req.body = value; // sanitized body
    next();
  };
}

function validateQuery(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.query, { stripUnknown: true });
    if (error) return res.status(400).json({ errors: error.details.map(d => d.message) });
    req.query = value;
    next();
  };
}

// Schema definitions
const userSchema = Joi.object({
  name: Joi.string().min(2).max(50).required(),
  email: Joi.string().email().required(),
  age: Joi.number().integer().min(1).max(150),
  role: Joi.string().valid('user', 'admin').default('user'),
});

const listSchema = Joi.object({
  page: Joi.number().integer().min(1).default(1),
  limit: Joi.number().integer().min(1).max(100).default(10),
  sort: Joi.string().valid('name', 'email', 'age').default('name'),
  order: Joi.string().valid('asc', 'desc').default('asc'),
});

const users = [];

app.post('/users', validate(userSchema), (req, res) => {
  const user = { id: users.length + 1, ...req.body, created: new Date() };
  users.push(user);
  res.status(201).json(user);
});

app.put('/users/:id', validate(userSchema), (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (!user) return res.status(404).json({ error: 'Not found' });
  Object.assign(user, req.body);
  res.json(user);
});

app.get('/users', validateQuery(listSchema), (req, res) => {
  let result = [...users];
  result.sort((a, b) => {
    const cmp = String(a[req.query.sort]).localeCompare(String(b[req.query.sort]));
    return req.query.order === 'desc' ? -cmp : cmp;
  });
  const start = (req.query.page - 1) * req.query.limit;
  res.json({ total: result.length, page: req.query.page, data: result.slice(start, start + req.query.limit) });
});

app.listen(3000, () => console.log('Validation demo :3000'));

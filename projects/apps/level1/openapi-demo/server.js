// OpenAPI Demo — Spec-first API design, with auto-generated docs UI.
const express = require('express');
const app = express();
app.use(express.json());

// === OpenAPI 3.0 spec (define your API here, then implement to match) ===
const spec = {
  openapi: '3.0.3',
  info: { title: 'Tasks API', version: '1.0.0', description: 'A simple task management API' },
  servers: [{ url: 'http://localhost:3000', description: 'Local dev' }],
  paths: {
    '/tasks': {
      get: { summary: 'List all tasks', parameters: [{ name: 'done', in: 'query', schema: { type: 'boolean' } }, { name: 'limit', in: 'query', schema: { type: 'integer', default: 20 } }], responses: { 200: { description: 'OK', content: { 'application/json': { schema: { type: 'array', items: { $ref: '#/components/schemas/Task' } } } } } } },
      post: { summary: 'Create a task', requestBody: { required: true, content: { 'application/json': { schema: { $ref: '#/components/schemas/TaskInput' } } } }, responses: { 201: { description: 'Created', content: { 'application/json': { schema: { $ref: '#/components/schemas/Task' } } } }, 422: { description: 'Validation error' } } },
    },
    '/tasks/{id}': {
      get: { summary: 'Get a task', parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'string' } }], responses: { 200: { description: 'OK' }, 404: { description: 'Not found' } } },
      patch: { summary: 'Update a task', parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'string' } }], responses: { 200: { description: 'OK' } } },
      delete: { summary: 'Delete a task', parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'string' } }], responses: { 204: { description: 'No content' } } },
    },
  },
  components: {
    schemas: {
      Task: { type: 'object', properties: { id: { type: 'string' }, title: { type: 'string' }, done: { type: 'boolean' }, createdAt: { type: 'string', format: 'date-time' } } },
      TaskInput: { type: 'object', required: ['title'], properties: { title: { type: 'string', minLength: 1, maxLength: 200 }, done: { type: 'boolean', default: false } } },
    },
  },
};

// === Simple in-memory task store ===
const tasks = new Map();
let nextId = 1;

// === Tiny Swagger UI (no external lib) ===
function swaggerUI(spec) {
  return (req, res) => {
    res.type('html').send(`<!DOCTYPE html>
<html><head><title>${spec.info.title} - API Docs</title>
<style>body{font-family:system-ui;max-width:900px;margin:40px auto;padding:0 20px;color:#222}
.path{margin:20px 0;border:1px solid #ddd;border-radius:8px;overflow:hidden}
.path-head{background:#f5f5f5;padding:12px 16px;display:flex;gap:12px;align-items:center;cursor:pointer}
.method{font-weight:700;padding:4px 10px;border-radius:4px;color:#fff;font-size:13px}
.get{background:#61affe}.post{background:#49cc90}.put{background:#fca130}.delete{background:#f93e3e}.patch{background:#50e3f2;color:#000}
.path-body{padding:16px;display:none}
.path.open .path-body{display:block}
pre{background:#f8f8f8;padding:12px;border-radius:4px;overflow-x:auto;font-size:13px}
h1{border-bottom:2px solid #eee;padding-bottom:8px}</style></head>
<body><h1>${spec.info.title} <small>v${spec.info.version}</small></h1>
<p>${spec.info.description}</p>
<p>Full spec: <a href="/openapi.json">/openapi.json</a></p>
${Object.entries(spec.paths).map(([path, methods]) => Object.entries(methods).map(([method, op]) => `
<div class="path"><div class="path-head" onclick="this.parentElement.classList.toggle('open')">
<span class="method ${method}">${method.toUpperCase()}</span>
<span><code>${path}</code></span>
<span style="margin-left:auto;color:#666">${op.summary || ''}</span>
</div><div class="path-body">${op.description ? `<p>${op.description}</p>` : ''}
${op.parameters ? `<h4>Parameters</h4><ul>${op.parameters.map(p => `<li><code>${p.name}</code> (${p.in}, ${p.schema?.type || '?'}) — ${p.description || ''}</li>`).join('')}</ul>` : ''}
${op.requestBody ? `<h4>Request body</h4><pre>${JSON.stringify(op.requestBody.content['application/json'].schema, null, 2)}</pre>` : ''}
<h4>Responses</h4><ul>${Object.entries(op.responses || {}).map(([code, r]) => `<li><b>${code}</b> — ${r.description}</li>`).join('')}</ul>
</div></div>
`).join('')).join('')}
</body></html>`);
  };
}

// === Endpoints ===
app.get('/openapi.json', (req, res) => res.json(spec));
app.get('/docs', swaggerUI(spec));

app.get('/tasks', (req, res) => {
  const list = Array.from(tasks.values()).filter(t => req.query.done === undefined ? true : t.done === (req.query.done === 'true'));
  res.json(list.slice(0, parseInt(req.query.limit) || 20));
});

app.post('/tasks', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'missing_title' });
  const id = 't_' + nextId++;
  const task = { id, title: req.body.title, done: req.body.done || false, createdAt: new Date().toISOString() };
  tasks.set(id, task);
  res.status(201).json(task);
});

app.get('/tasks/:id', (req, res) => {
  const task = tasks.get(req.params.id);
  task ? res.json(task) : res.status(404).json({ error: 'not_found' });
});

app.patch('/tasks/:id', (req, res) => {
  const task = tasks.get(req.params.id);
  if (!task) return res.status(404).json({ error: 'not_found' });
  Object.assign(task, req.body);
  res.json(task);
});

app.delete('/tasks/:id', (req, res) => {
  tasks.delete(req.params.id) ? res.status(204).end() : res.status(404).json({ error: 'not_found' });
});

app.listen(3000, () => console.log('OpenAPI demo :3000 — GET /docs for API documentation'));
module.exports = app;

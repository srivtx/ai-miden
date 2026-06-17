// Multi-Tenant SaaS — Organizations, members, roles, resource isolation.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const organizations = []; const memberships = []; const resources = []; let oId = 1, mId = 1, rId = 1;
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }
function getMember(orgId, userId) { return memberships.find(m => m.orgId === orgId && m.userId === userId); }
function getOrg(orgId) { return organizations.find(o => o.id === orgId); }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// Organizations
app.post('/organizations', auth, (req, res) => {
  const { name, slug } = req.body;
  if (!name) return res.status(400).json({ error: 'name required' });
  const orgSlug = slug || name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  if (organizations.find(o => o.slug === orgSlug)) return res.status(409).json({ error: 'slug exists' });
  const org = { id: oId++, slug: orgSlug, name, ownerId: req.user.id, plan: 'free', memberCount: 1, createdAt: new Date().toISOString() };
  organizations.push(org);
  // Owner gets admin role
  memberships.push({ id: mId++, orgId: org.id, userId: req.user.id, role: 'owner', joinedAt: new Date().toISOString() });
  res.status(201).json(org);
});

app.get('/organizations', auth, (req, res) => {
  const userOrgs = memberships.filter(m => m.userId === req.user.id).map(m => ({ ...getOrg(m.orgId), role: m.role }));
  res.json(userOrgs);
});

app.get('/organizations/:slug', auth, (req, res) => {
  const org = getOrg(organizations.find(o => o.slug === req.params.slug)?.id);
  if (!org) return res.status(404).json({ error: 'Not found' });
  const member = getMember(org.id, req.user.id);
  if (!member) return res.status(403).json({ error: 'Not a member' });
  res.json({ ...org, role: member.role, members: memberships.filter(m => m.orgId === org.id).map(m => ({ userId: m.userId, name: users.find(u => u.id === m.userId)?.name, email: users.find(u => u.id === m.userId)?.email, role: m.role, joinedAt: m.joinedAt })) });
});

// Members
app.post('/organizations/:slug/members', auth, (req, res) => {
  const org = getOrg(organizations.find(o => o.slug === req.params.slug)?.id);
  if (!org) return res.status(404).json({ error: 'Not found' });
  const caller = getMember(org.id, req.user.id);
  if (!caller || !['owner', 'admin'].includes(caller.role)) return res.status(403).json({ error: 'Owner/admin only' });
  const { email, role } = req.body;
  const user = users.find(u => u.email === email);
  if (!user) return res.status(404).json({ error: 'User not found' });
  if (getMember(org.id, user.id)) return res.status(409).json({ error: 'Already member' });
  memberships.push({ id: mId++, orgId: org.id, userId: user.id, role: role || 'member', joinedAt: new Date().toISOString() });
  org.memberCount++;
  res.status(201).json({ added: true, role });
});

// Resources (anything multi-tenant: projects, tasks, etc.)
app.post('/organizations/:slug/resources', auth, (req, res) => {
  const org = getOrg(organizations.find(o => o.slug === req.params.slug)?.id);
  if (!org) return res.status(404).json({ error: 'Not found' });
  const member = getMember(org.id, req.user.id);
  if (!member) return res.status(403).json({ error: 'Not a member' });
  const { type, name, data } = req.body;
  if (!name) return res.status(400).json({ error: 'name required' });
  const r = { id: rId++, orgId: org.id, type: type || 'generic', name, data: data || {}, createdBy: req.user.id, createdAt: new Date().toISOString() };
  resources.push(r);
  res.status(201).json(r);
});

app.get('/organizations/:slug/resources', auth, (req, res) => {
  const org = getOrg(organizations.find(o => o.slug === req.params.slug)?.id);
  if (!org) return res.status(404).json({ error: 'Not found' });
  const member = getMember(org.id, req.user.id);
  if (!member) return res.status(403).json({ error: 'Not a member' });
  res.json(resources.filter(r => r.orgId === org.id));
});

app.listen(3000, () => console.log('Multi-Tenant :3000'));
module.exports = app;

// Job Board — Listings, applications, search, filters by location/type/company.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const jobs = []; const applications = []; let jobId = 1, appId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }
function role(r) { return (req, res, next) => req.user.role === r ? next() : res.status(403).json({ error: `Requires ${r} role` }); }

// AUTH (with role)
app.post('/auth/register', async (req, res) => {
  const { name, email, password, role: r } = req.body;
  if (!name || !email || !password) return res.status(400).json({ error: 'name, email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), role: r === 'employer' ? 'employer' : 'jobseeker' };
  users.push(user);
  res.status(201).json({ user: { id: user.id, name, email, role: user.role }, token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '1h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '1h' }) });
});

// JOBS (post: employer only, view: anyone)
app.post('/jobs', auth, role('employer'), (req, res) => {
  const { title, company, location, type, salary, description, requirements } = req.body;
  if (!title || !company || !description) return res.status(400).json({ error: 'title, company, description required' });
  const job = { id: jobId++, title, company, location: location || 'Remote', type: type || 'full-time', salary: salary || null, description, requirements: requirements || [], postedBy: req.user.id, postedAt: new Date().toISOString(), active: true };
  jobs.push(job);
  res.status(201).json(job);
});

app.get('/jobs', (req, res) => {
  let result = jobs.filter(j => j.active);
  if (req.query.type) result = result.filter(j => j.type === req.query.type);
  if (req.query.location) result = result.filter(j => j.location.toLowerCase().includes(req.query.location.toLowerCase()));
  if (req.query.company) result = result.filter(j => j.company.toLowerCase().includes(req.query.company.toLowerCase()));
  if (req.query.search) {
    const q = req.query.search.toLowerCase();
    result = result.filter(j => j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q) || j.description.toLowerCase().includes(q) || j.requirements.some(r => r.toLowerCase().includes(q)));
  }
  if (req.query.salary) result = result.filter(j => j.salary >= parseInt(req.query.salary));
  result.sort((a, b) => new Date(b.postedAt) - new Date(a.postedAt));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = Math.min(50, parseInt(req.query.limit) || 20);
  const total = result.length;
  res.json({ total, page, pages: Math.ceil(total / limit), data: result.slice((page - 1) * limit, page * limit) });
});

app.get('/jobs/:id', (req, res) => {
  const job = jobs.find(j => j.id === parseInt(req.params.id));
  job ? res.json(job) : res.status(404).json({ error: 'Not found' });
});

// APPLICATIONS (jobseeker only)
app.post('/jobs/:id/apply', auth, role('jobseeker'), (req, res) => {
  const job = jobs.find(j => j.id === parseInt(req.params.id));
  if (!job) return res.status(404).json({ error: 'Job not found' });
  if (applications.find(a => a.jobId === job.id && a.userId === req.user.id)) return res.status(409).json({ error: 'Already applied' });
  const app = { id: appId++, jobId: job.id, userId: req.user.id, coverLetter: req.body.coverLetter || '', status: 'pending', appliedAt: new Date().toISOString() };
  applications.push(app);
  res.status(201).json(app);
});

// MY APPLICATIONS
app.get('/applications', auth, role('jobseeker'), (req, res) => {
  const myApps = applications.filter(a => a.userId === req.user.id).map(a => ({ ...a, job: jobs.find(j => j.id === a.jobId) }));
  res.json(myApps);
});

// EMPLOYER: view applicants for a job
app.get('/jobs/:id/applicants', auth, role('employer'), (req, res) => {
  const job = jobs.find(j => j.id === parseInt(req.params.id));
  if (!job) return res.status(404).json({ error: 'Not found' });
  if (job.postedBy !== req.user.id) return res.status(403).json({ error: 'Not your job' });
  const apps = applications.filter(a => a.jobId === job.id).map(a => ({ ...a, applicant: users.find(u => u.id === a.userId)?.name }));
  res.json({ job: job.title, applicants: apps });
});

// Update application status (employer)
app.patch('/applications/:id', auth, role('employer'), (req, res) => {
  const app = applications.find(a => a.id === parseInt(req.params.id));
  if (!app) return res.status(404).json({ error: 'Not found' });
  const job = jobs.find(j => j.id === app.jobId);
  if (job.postedBy !== req.user.id) return res.status(403).json({ error: 'Forbidden' });
  if (req.body.status) app.status = req.body.status;
  res.json(app);
});

app.listen(3000, () => console.log('Job Board :3000'));
module.exports = app;

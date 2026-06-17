// Course Platform — Courses, lessons, enrollment, progress tracking, completion.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const courses = []; const lessons = []; const enrollments = []; const progress = [];
let courseId = 1, lessonId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }
function role(r) { return (req, res, next) => req.user.role === r ? next() : res.status(403).json({ error: 'Forbidden' }); }

app.post('/auth/register', async (req, res) => {
  const { name, email, password, role: r } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), role: r === 'instructor' ? 'instructor' : 'student' };
  users.push(user);
  res.status(201).json({ user: { id: user.id, name, email, role: user.role }, token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '24h' }) });
});

// COURSES (instructor only to create)
app.post('/courses', auth, role('instructor'), (req, res) => {
  const { title, description, category, price } = req.body;
  if (!title) return res.status(400).json({ error: 'Title required' });
  const course = { id: courseId++, instructorId: req.user.id, title, description: description || '', category: category || 'General', price: price || 0, published: false, enrolledCount: 0, createdAt: new Date().toISOString() };
  courses.push(course);
  res.status(201).json(course);
});

app.get('/courses', (req, res) => {
  let result = courses.filter(c => c.published);
  if (req.query.category) result = result.filter(c => c.category === req.query.category);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(c => c.title.toLowerCase().includes(q) || c.description.toLowerCase().includes(q)); }
  if (req.query.free === 'true') result = result.filter(c => c.price === 0);
  result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 20;
  const enriched = result.slice((page - 1) * limit, page * limit).map(c => ({ ...c, instructor: users.find(u => u.id === c.instructorId)?.name, lessonCount: lessons.filter(l => l.courseId === c.id).length }));
  res.json({ total: result.length, page, data: enriched });
});

app.get('/courses/:id', (req, res) => {
  const course = courses.find(c => c.id === parseInt(req.params.id) && c.published);
  if (!course) return res.status(404).json({ error: 'Not found' });
  const courseLessons = lessons.filter(l => l.courseId === course.id).sort((a, b) => a.order - b.order);
  res.json({ ...course, instructor: users.find(u => u.id === course.instructorId)?.name, lessons: courseLessons, lessonCount: courseLessons.length });
});

// LESSONS (instructor only)
app.post('/courses/:id/lessons', auth, role('instructor'), (req, res) => {
  const course = courses.find(c => c.id === parseInt(req.params.id));
  if (!course || course.instructorId !== req.user.id) return res.status(404).json({ error: 'Not found or unauthorized' });
  const lesson = { id: lessonId++, courseId: course.id, title: req.body.title, content: req.body.content || '', videoUrl: req.body.videoUrl || '', order: lessons.filter(l => l.courseId === course.id).length + 1, createdAt: new Date().toISOString() };
  lessons.push(lesson);
  res.status(201).json(lesson);
});

// ENROLL
app.post('/courses/:id/enroll', auth, (req, res) => {
  const course = courses.find(c => c.id === parseInt(req.params.id) && c.published);
  if (!course) return res.status(404).json({ error: 'Not found' });
  if (enrollments.find(e => e.courseId === course.id && e.userId === req.user.id)) return res.status(409).json({ error: 'Already enrolled' });
  enrollments.push({ courseId: course.id, userId: req.user.id, enrolledAt: new Date().toISOString() });
  course.enrolledCount++;
  res.status(201).json({ enrolled: true, course: course.title });
});

// PROGRESS (mark lesson complete)
app.post('/lessons/:id/complete', auth, (req, res) => {
  const lesson = lessons.find(l => l.id === parseInt(req.params.id));
  if (!lesson) return res.status(404).json({ error: 'Not found' });
  if (!enrollments.find(e => e.courseId === lesson.courseId && e.userId === req.user.id)) return res.status(403).json({ error: 'Enroll first' });
  const existing = progress.find(p => p.lessonId === lesson.id && p.userId === req.user.id);
  if (existing) return res.status(409).json({ error: 'Already completed' });
  progress.push({ lessonId: lesson.id, courseId: lesson.courseId, userId: req.user.id, completedAt: new Date().toISOString() });
  res.json({ completed: true, lesson: lesson.title });
});

// MY PROGRESS
app.get('/my-courses', auth, (req, res) => {
  const myEnrollments = enrollments.filter(e => e.userId === req.user.id);
  const enriched = myEnrollments.map(e => {
    const course = courses.find(c => c.id === e.courseId);
    if (!course) return null;
    const totalLessons = lessons.filter(l => l.courseId === course.id).length;
    const completed = progress.filter(p => p.courseId === course.id && p.userId === req.user.id).length;
    return { ...e, course: { id: course.id, title: course.title, category: course.category }, progress: { completed, total: totalLessons, percentage: totalLessons ? Math.round((completed / totalLessons) * 100) : 0 } };
  }).filter(Boolean);
  res.json(enriched);
});

app.listen(3000, () => console.log('Course Platform :3000'));
module.exports = app;

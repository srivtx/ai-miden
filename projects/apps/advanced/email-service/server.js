// Email Service — Queue-based, template-rendered, never blocks the request.
const express = require('express');
const nodemailer = require('nodemailer');
const Queue = require('bull');
const handlebars = require('handlebars');
const app = express();
app.use(express.json());

// ---- Email queue (processes emails in background) ----
const emailQueue = new Queue('email', 'redis://localhost:6379');

// ---- Templates ----
const templates = {
  welcome: handlebars.compile(`<h1>Welcome, {{name}}!</h1><p>Thanks for signing up.</p>`),
  reset_password: handlebars.compile(`<h1>Password Reset</h1><p>Click <a href="{{link}}">here</a> to reset. Expires in 15 min.</p>`),
  receipt: handlebars.compile(`<h1>Receipt</h1><p>Amount: ${{amount}}. Order: #{{orderId}}</p>`),
};

// ---- Transport (SMTP — in production: SendGrid, Mailgun, SES) ----
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST || 'smtp.mailtrap.io', // Mailtrap for testing
  port: 587,
  auth: { user: process.env.SMTP_USER || 'test', pass: process.env.SMTP_PASS || 'test' },
});

// ---- Process email jobs ----
emailQueue.process(async (job) => {
  const { to, subject, template, data } = job.data;
  const html = templates[template] ? templates[template](data) : `<p>${data.message || 'No content'}</p>`;

  await transporter.sendMail({
    from: '"My App" <noreply@myapp.com>',
    to, subject, html,
  });

  return { sent: true, to, template };
});

// ---- API: enqueue an email (instant response) ----
app.post('/send-email', async (req, res) => {
  const { to, subject, template, data } = req.body;
  if (!to || !template) return res.status(400).json({ error: 'to and template required' });
  if (!templates[template]) return res.status(400).json({ error: `Unknown template: ${template}. Available: ${Object.keys(templates).join(', ')}` });

  const job = await emailQueue.add({ to, subject: subject || template, template, data: data || {} }, { attempts: 3, backoff: { type: 'exponential', delay: 5000 } });

  res.json({ message: 'Email queued', jobId: job.id });
});

// ---- API: check email status ----
app.get('/email-status/:jobId', async (req, res) => {
  const job = await emailQueue.getJob(req.params.jobId);
  if (!job) return res.status(404).json({ error: 'Job not found' });
  const state = await job.getState();
  res.json({ id: job.id, state, progress: job.progress(), result: job.returnvalue, failed: job.failedReason });
});

app.listen(3000, () => console.log('Email service :3000'));
module.exports = app;

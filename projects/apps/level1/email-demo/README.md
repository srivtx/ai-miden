# Email Demo — Templates, rendering, queue, send tracking

Send emails with templates, variables, and status tracking. Shows: how to use `{{var}}` placeholders, the email queue pattern, and how to handle send failures.

## Endpoints
```
GET  /templates                     # list template names
GET  /templates/:name               # get a template
POST /templates/:name/render        # render a template with vars (preview)
POST /send        { to, template, vars }   # send (or { to, subject, body } for raw)
GET  /emails?status=...             # list sent emails
GET  /emails/:id                    # email details
```

## Try
```bash
# Render a template (preview)
curl -X POST http://localhost:3000/templates/welcome/render \
  -H "Content-Type: application/json" \
  -d '{"app": "MyApp", "name": "Alice"}'
# { subject: "Welcome to MyApp!", body: "Hi Alice,\n\n..." }

# Send an email
curl -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{"to": "alice@example.com", "template": "reset_password", "vars": {"app": "MyApp", "token": "abc123"}}'
# 202 { id: "em_...", status: "queued" }

# Check status
curl http://localhost:3000/emails
# 100ms later: status: "sent"
```

## What this teaches
1. **Templates with variables**: `{{name}}`, `{{app}}`, `{{token}}` placeholders
2. **Template rendering**: simple string replacement, no engine needed
3. **Email queue**: same pattern as background jobs
4. **Status tracking**: queued → sent / failed
5. **5% failure simulation**: shows how to handle send errors
6. **Variable substitution**: render once, send once

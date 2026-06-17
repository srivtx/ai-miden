# 05 — Templates (Notifications)

Reusable notification templates with placeholders like `{{name}}`.

**What's new:**
- `templates` table: name, channel, subject, body, variables
- Pre-seeded templates (welcome, reset_password, etc.)
- Render endpoint: replace placeholders with values

**Why templates?** Same notification gets sent 1000 times. Without templates, you'd repeat the subject and body each time. With templates, you define it once and render it with different variables.

**Why placeholders?** `"Hi Alice, welcome!"` vs `"Hi Bob, welcome!"`. Same template, different variables. Variables: `{{name}}`, `{{app}}`, `{{token}}`.

**The `variables` field:** We extract the variable names from the template. Now the UI knows what to ask the user for.

## Run
```bash
npm install && node server.js
```

```bash
# Render the welcome template
curl -X POST http://localhost:3000/templates/welcome/render -H "Content-Type: application/json" \
  -d '{"app": "MyApp", "name": "Alice"}'
# { channel: "email", subject: "Welcome to MyApp, Alice!", body: "Hi Alice,\n\nWelcome aboard!..." }

# Render password reset
curl -X POST http://localhost:3000/templates/reset_password/render -H "Content-Type: application/json" \
  -d '{"app": "MyApp", "token": "abc123"}'
```

## What we learned
- Template pattern
- Placeholder syntax
- Auto-extract variables
- Reusable across channels (email, push, SMS)

## Next
**06-preferences** — let users choose which notifications they want.

# 02 — SMS (Notifications)

Send SMS. Same pattern as email (queue + status), different validation.

**What's new:**
- Phone number validation (E.164 format: `+15551234567`)
- Different provider (simulated Twilio)
- Same queue + status + retry pattern

**Why E.164?** International format. `+` then country code, then number. Works in any country. Without it, you'd have to figure out the country code from the number — error-prone.

**Why same pattern as email?** Notifications all work the same way: queue, send, track status, retry. The provider is different (Twilio vs SES) but the logic is the same.

## Run
```bash
npm install && node server.js
```

```bash
# Send SMS
curl -X POST http://localhost:3000/sms -H "Content-Type: application/json" \
  -d '{"to": "+15551234567", "message": "Your code is 123456"}'
# 202

# Check status
curl http://localhost:3000/sms/sms_xxx

# Bad phone
curl -X POST http://localhost:3000/sms -H "Content-Type: application/json" \
  -d '{"to": "5551234", "message": "Test"}'
# Status will be "failed" with error: "invalid_phone"
```

## What we learned
- E.164 phone format
- Same queue pattern works for SMS
- Validation per provider
- Provider abstraction (Twilio, SNS, etc.)

## Next
**03-push** — push notifications to mobile. Different again, similar pattern.

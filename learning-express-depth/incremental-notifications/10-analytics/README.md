# 10 — Analytics (Notifications, final stage)

Track delivery, opens, clicks. Per-channel rates.

**What's new:**
- Mark notifications as delivered, opened, clicked
- Per-channel analytics: delivery rate, open rate, click rate

**Why analytics?** "Are our notifications working?" You need data. Delivery rate tells you if emails are bouncing. Open rate tells you if the subject line is good. Click rate tells you if the content is interesting.

**The funnel:** sent → delivered → opened → clicked. Each step loses people. The drop-off tells you where to improve.

## Run
```bash
npm install && node server.js
```

```bash
# Track events
curl -X POST http://localhost:3000/notifications/n_xxx/delivered
curl -X POST http://localhost:3000/notifications/n_xxx/opened
curl -X POST http://localhost:3000/notifications/n_xxx/clicked

# Get analytics
curl http://localhost:3000/analytics/channels
# { channels: [
#   { channel: "email", sent: 100, delivered: 95, opened: 60, clicked: 12, delivery_rate: 95.0, open_rate: 60.0, click_rate: 12.0 }
# ] }
```

## What we learned
- Notification funnel (sent → delivered → opened → clicked)
- Per-channel rates
- Why each metric matters
- How to improve based on data

## 🎉 10 stages complete!

The full notifications system has:
- Email ✓
- SMS ✓
- Push ✓
- In-app ✓
- Templates ✓
- Preferences ✓
- Digest ✓
- Batch ✓
- Priority ✓
- Analytics ✓

This is how SendGrid, Twilio, OneSignal, Firebase Cloud Messaging all work. Same 10 patterns, different code.

## The 10 patterns
1. **Email** — queue + retry
2. **SMS** — phone validation, same queue
3. **Push** — device tokens, multi-device
4. **In-app** — inbox, unread, mark read
5. **Templates** — placeholders, reusable
6. **Preferences** — opt-out per channel
7. **Digest** — group + send
8. **Batch** — bulk insert, broadcast
9. **Priority** — urgent vs batched
10. **Analytics** — delivery, open, click rates

These 10 patterns are the building blocks of every notification system.

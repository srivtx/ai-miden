# 03 — Push (Notifications)

Push notifications to mobile. Register device, send notification.

**What's new:**
- `devices` table: user_id, platform (ios/android), token
- `push_notifications` table: device_id, title, body, data
- Register a device: `POST /devices`
- Send push: `POST /push` (sends to all of a user's devices)

**Why a device token?** Each phone gets a unique token from Apple (APNS) or Google (FCM). We store it. When we want to send a push, we use the token to target that specific device.

**Why send to all devices of a user?** A user has a phone, a tablet, a work phone. They want the notification on all of them. We send to all registered devices.

## Run
```bash
npm install && node server.js
```

```bash
# Register a device
curl -X POST http://localhost:3000/devices -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "platform": "ios", "token": "abc123"}'

# Send a push
curl -X POST http://localhost:3000/push -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "title": "You have a new follower", "body": "Bob started following you"}'
# 202 { sent_to: 1 }
```

## What we learned
- Device registration
- Per-user multi-device
- The push provider pattern (APNS, FCM)
- Always-on background delivery

## Next
**04-in-app** — show notifications inside the app. Inbox pattern.

# 09 — RSS

Generate RSS, Atom, and JSON feeds. Let readers subscribe.

**What's new:**
- `/feed.xml` — RSS 2.0 (the classic)
- `/atom.xml` — Atom (modern alternative)
- `/feed.json` — JSON Feed (newest)
- All three formats serve the same data differently
- XML escaping to prevent injection

**Why feeds?** Readers don't visit your site daily. With a feed, their reader app (Feedly, NetNewsWire) checks for new posts and notifies them. Same idea as a newsletter, but the user controls when they read.

## Run
```bash
npm install && node server.js
```

```bash
# RSS
curl http://localhost:3000/feed.xml
# XML document

# Atom
curl http://localhost:3000/atom.xml

# JSON Feed
curl http://localhost:3000/feed.json
# { version, title, items: [...] }
```

## What this stage teaches
- Generating XML by hand
- Three feed formats (RSS, Atom, JSON Feed)
- XML escaping (security!)
- Content-Type for feeds
- The pattern of "data in multiple formats"

## Next
**10-newsletter** — let readers subscribe by email. Send new posts automatically.

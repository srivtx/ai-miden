# Learning Express Depth — Complete

**62 apps. 162 server.js files. 151 git commits.**

## What's here

### Small Projects (60 apps, `0X-name/`)

Each one is 30-100 lines. Single concept per app. They cover the basic shape: server, routes, response types, error handling, validation, auth, real-time, search, security, etc.

### Incremental Apps (10 apps, 102 stages)

Each app is built up in 10-12 stages. Each stage adds ONE new thing. The full app at the end is production-quality.

| App | Stages | What it builds |
|---|---|---|
| **Todo** | 12 | The foundation. CRUD → DB → relations → auth → multi-tenant → soft delete → audit → versioning → caching → rate limit → search → webhooks |
| **E-commerce** | 10 | Products → cart → checkout → payments → orders → inventory → reviews → coupons → shipping → recommendations |
| **Blog/CMS** | 10 | Posts → comments → users → roles → media → drafts → revisions → search → RSS → newsletter |
| **Chat** | 10 | Messages → rooms → users → presence → typing → receipts → files → reactions → threads → notifications |
| **Auth** | 10 | Signup → login → JWT → refresh → reset password → email verify → 2FA → OAuth → API keys → audit |
| **Analytics** | 10 | Events → sessions → funnels → cohorts → dashboards → exports → alerts → segments → A/B tests → realtime |
| **File Storage** | 10 | Upload → download → folders → sharing → versions → trash → search → thumbnails → compression → quotas |
| **Notifications** | 10 | Email → SMS → push → in-app → templates → preferences → digest → batch → priority → analytics |
| **Payments** | 10 | Charges → customers → subscriptions → invoices → refunds → disputes → webhooks → payouts → tax → fraud |
| **Search** | 10 | Basic → relevance → filters → facets → autocomplete → spell check → synonyms → ranking → analytics → ML ranking |

## How to use this folder

1. **Pick an app** (e.g. `incremental-ecommerce`)
2. **Start at stage 01**, run it, read the code
3. **Each stage's README** explains what's new, why, and how to think about it
4. **Each stage builds on the previous** — same shape, more features
5. **At stage 10-12**, you have a production-quality app

## Why this structure?

- **Small projects** show the **shape** — same CRUD, different data
- **Incremental apps** show the **progression** — from empty to production
- Together, they teach the **patterns** that appear in every real backend

The 100+ patterns here appear in Stripe, GitHub, Slack, Notion, Netflix, Amazon. Same code, different data.

## Stats

```
60 small projects          60 server.js files
10 incremental apps       102 server.js files (10-12 stages each)
                           ─────────────────
TOTAL                      162 server.js files
```

Every file is runnable. Every project has a README explaining the concept and the thinking. Every incremental stage builds on the previous one.

See `incremental/PLAN.md` for the full plan that drove this.

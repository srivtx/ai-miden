# Feature Flags Demo — Rollout %, user targeting, A/B variants, kill switch

Decouple deploy from release. Ship the code, but turn it on for 1% of users. Watch the metrics. Roll up or roll back without redeploying.

## Endpoints
```
GET  /flags                          # list all flags
GET  /flags/evaluate                 # evaluate all flags for current user
POST /admin/flags/:name/override     # force on/off for specific users
POST /admin/flags/:name/rollout      # change rollout percentage

GET  /checkout    # uses new_checkout flag
GET  /pricing     # uses pricing_tier variant (control, discount_10, discount_20)
GET  /search      # uses beta_search flag
```

## Try
```bash
# Same user, different flags
curl -H "X-User-Id: user_1" http://localhost:3000/flags/evaluate
# Some flags on, some off (based on hash(userId + flagName) % 100)

curl -H "X-User-Id: user_2" http://localhost:3000/flags/evaluate
# Different result (different user → different bucket)

# Change rollout to 100%
curl -X POST http://localhost:3000/admin/flags/beta_search/rollout \
  -H "Content-Type: application/json" -d '{"percentage": 100}'

# Override for a specific user
curl -X POST http://localhost:3000/admin/flags/new_checkout/override \
  -H "Content-Type: application/json" -d '{"users": ["user_1"], "value": true}'
```

## What this teaches
1. **Boolean flags**: on/off, default value
2. **Rollout percentage**: gradual rollout to N% of users (deterministic by userId hash)
3. **User targeting**: force on/off for specific users
4. **Variants (A/B/C test)**: weighted random selection from a set
5. **Kill switch**: turn off immediately without a deploy
6. **No deploy required**: change config and it takes effect

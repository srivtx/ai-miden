# Config Demo — Env vars, .env files, feature flags, per-env overrides

The patterns for managing config in a backend service: load from env, support `.env` files, feature flags, environment-specific limits.

## Endpoints
```
GET /config          # show all config (with secrets redacted)
GET /features        # show feature flag state
GET /checkout        # uses FEATURE_NEW_CHECKOUT to pick v1 or v2
GET /search          # uses FEATURE_BETA_SEARCH to pick classic or beta
GET /env             # show which env vars are loaded
```

## What this teaches
1. **12-factor app**: config in environment, not in code
2. **`.env` files**: for local dev, in `.gitignore`
3. **Env var precedence**: process.env > .env file > defaults
4. **Feature flags**: gradual rollout, A/B testing, kill switches
5. **Per-environment config**: dev vs prod vs test
6. **Secret redaction**: don't leak secrets in API responses

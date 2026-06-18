# The Decisions

> *"If it's not tested, it's broken. You just don't know it yet."*

## Decision 1: Vitest and not Jest

**Alternatives**:
- **Jest** — older, more popular, slower
- **Mocha** — older, more flexible
- **AVA** — concurrent
- **Node:test** — built into Node, newer

**Why Vitest: Fast. Modern. Jest-compatible API. Best DX. Active development.

**Trade-off**: Slightly newer. Some plugins are Jest-only.

## Decision 2: supertest and not real HTTP

**Alternative**: Make real HTTP requests with `fetch` or `http`.

**Why supertest: Binds to a random port. Makes the request. No real server. Fast.

**Trade-off**: Doesn't test the full HTTP stack (TLS, reverse proxy). We accept this for unit/integration tests.

## Decision 3: `:memory:` SQLite and not a test file

**Alternative**: Test file (`app.test.db`).

**Why `:memory:`: Fast. No file. Each test file gets a fresh database.

**Trade-off**: Slightly different from production. We accept this.

## Decision 4: Integration tests and not unit tests only

**Alternative**: Unit tests only.

**Why integration: They test the full handler (validation, error wall, database). More value per test.

**Trade-off**: Slower than unit tests. We accept this for the value.

## Decision 5: Reset between tests

**Alternative**: Run tests in parallel with separate DBs.

**Why reset: Simple. Each test starts with a clean database. No interference.

**Trade-off**: Slightly slower (reset is O(n)). We accept this.

## Decision 6: No end-to-end tests (Playwright/Cypress)

**Alternative**: End-to-end tests with Playwright or Cypress.

**Why no: Out of scope. We test the HTTP layer. For full browser tests, you'd add Playwright or Cypress.

**Trade-off**: Can't test the full user flow in a browser. We accept this.

## Decision 7: No load tests

**Alternative**: Load tests with k6 or Artillery.

**Why no: Out of scope. We test correctness, not performance.

**Trade-off**: Can't catch performance regressions. We accept this.

## Decision 8: No mutation tests

**Alternative**: Mutation tests with Stryker.

**Why no: Out of scope. Mutation tests verify that your tests actually catch bugs.

**Trade-off**: Can't verify test quality. We accept this.

## Decision 9: No coverage requirement

**Alternative**: Require 80%+ coverage in CI.

**Why no: Out of scope. Coverage is a useful metric but not the only one.

**Trade-off**: Some code might not be tested. We accept this.

## Decision 10: No E2E in CI (yet)

**Alternative**: Run E2E tests in CI.

**Why no: We don't have E2E tests. When we do, we'd run them in CI.

**Trade-off**: None for now.

---

## What We Did Not Decide

- **End-to-end tests (Playwright/Cypress)** — out of scope
- **Load tests** — out of scope
- **Mutation tests** — out of scope
- **Visual regression** — out of scope
- **Coverage requirement in CI** — out of scope
- **Parallel test execution with separate DBs** — out of scope (current setup is fine)
- **Test database migrations** — we use the same migrations as production
- **Snapshot testing** — out of scope
- **Property-based testing (fast-check)** — out of scope
- **Security tests** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Server Is Tested

For 35 projects, we verified the server works by clicking around. Manual. Slow. Error-prone.

Now the server is tested. Every change runs through the test suite. We catch bugs before they reach production. We can refactor with confidence.

This is the foundation of *test automation*. From here, every project that needs to verify correctness can use these tools. The patterns (Vitest, supertest, separate test DB) are universal.

The next 4 projects will assume tests exist. The path diverges:

- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server is tested. The path continues.

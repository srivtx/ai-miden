# The Problem

> *"If it's not tested, it's broken. You just don't know it yet."*

## Why Manual Testing Is Not Enough

In projects 01-35, we've been running the server and clicking around. We verify it works by using it. That's manual testing.

Manual testing is slow, error-prone, and incomplete:

- **Slow**: a human has to click through every flow
- **Error-prone**: humans miss things
- **Incomplete**: we only test the happy path
- **Forgotten**: after a change, we might not re-test
- **Inconsistent**: different testers test differently

We need **automated tests** that run on every change. If a test fails, the change is rejected. We catch bugs before they reach production.

## What Pain Is This Solving?

Imagine you change one line of code. The line is in a function that's used by 10 handlers. Which handlers break? You don't know. You'd have to click through all 10 flows to find out.

With automated tests, you don't click. You run `npm test`. The tests run in seconds. The output tells you which handlers broke. You fix the bug before merging.

## The Deeper Problem: Test Isolation

Tests must be **isolated**. A test should not depend on the state of other tests. If test A creates a user and test B doesn't, test B shouldn't see that user.

The solution: a **separate test database**. Each test (or test file) gets a fresh database. After the test, the database is reset.

We use `:memory:` SQLite (in-memory database). Each test file gets a fresh database. The tests don't interfere with each other.

## What This Project Will Solve

This project will:

1. Add `vitest` and `supertest` as dev dependencies
2. Set up a separate test database (`:memory:` SQLite)
3. Write unit tests for individual functions
4. Write integration tests for handlers (signup, login, posts, etc.)
5. Run all tests with `npm test`

By the end, we have an automated test suite. Every change runs through it. We catch bugs before they reach production.

## What This Project Will *Not* Solve

- **End-to-end tests** (browser, full user flow) — we use supertest (HTTP-level). For full browser tests, use Playwright or Cypress.
- **Load tests** — we test correctness, not performance. For load, use k6 or Artillery.
- **Security tests** — out of scope. Use OWASP ZAP or similar.
- **Mutation testing** — out of scope. Use Stryker.
- **Visual regression** — out of scope.

## The Question This Project Answers

> *"How do I verify the server works correctly on every change?"*

If you can answer: "use Vitest + supertest, a separate test database, isolation between tests, run on every commit," you are ready for project 37.

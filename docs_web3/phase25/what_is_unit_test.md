# What Is a Unit Test?

## Why it exists (THE PROBLEM)

Blockchain transactions cost money and are irreversible.

If a bug exists in a program instruction, it will be exploited on mainnet before developers notice, potentially draining treasuries and destroying user trust.

Manual testing is too slow, inconsistent, and incomplete to catch edge cases in arithmetic, authorization, and state transitions before deployment.

Automated unit tests run on every code change and provide immediate feedback to developers.

## Definition

A unit test is an automated test that verifies a single function or small module in isolation by providing known inputs and asserting expected outputs.

It runs quickly without network dependencies and catches regressions immediately when code changes, providing a safety net for continuous development.

## Real-life analogy

Imagine assembling a car engine.

Before installing it in the vehicle, engineers test each piston, valve, and gear in isolation on a bench rig.

They verify that the piston compresses to exactly the right volume, the valve opens at the correct pressure, and the gear turns smoothly under load.

Unit tests are those bench rigs for software.

They exercise each piece of logic independently so that when the whole engine runs, every component has already proven it works correctly under controlled conditions.

## Tiny numeric example

Consider a deposit function with these unit tests:

| Test Name | Input | Expected Result | Purpose |
|-----------|-------|-----------------|---------|
| deposit_normal | 100 | balance = 100 | Happy path works |
| deposit_zero | 0 | error | Rejects invalid input |
| deposit_max | u64::MAX - 1 | balance = MAX - 1 | Boundary near limit |
| deposit_overflow | u64::MAX + 1 | error | Overflow prevented |

Each test runs in under 10 milliseconds and gives immediate feedback on whether the logic is correct.

Fast feedback loops encourage developers to test more often and catch bugs earlier.

A robust unit test suite is a prerequisite for confident refactoring and feature addition.

Developers should write tests before or alongside the code they are testing.

## Common confusion

- "Unit tests are too simple to catch real bugs."
  They catch the majority of logic errors, off-by-one mistakes, and boundary violations before integration.

- "I can test everything manually."
  Manual testing is inconsistent, forgets edge cases, and cannot be automated in CI pipelines or run by other developers.

- "Unit tests prove the program is secure."
  They prove logic correctness but not security against all adversarial conditions.
  Fuzzing and audits are also needed.

- "Unit tests must use the real blockchain."
  Solana unit tests run in a local BankClient or ProgramTest environment without RPC calls or network latency.

- "Writing tests takes too much time."
  Tests save far more time by preventing costly mainnet bugs and debugging sessions that can last weeks.

- "If the code compiles, it works."
  Rust's type system catches many errors, but logic bugs, arithmetic mistakes, and missing constraints still require tests.

- "Unit tests are only for Rust programs."
  TypeScript APIs, client libraries, and off-chain services also benefit enormously from unit test coverage.

## Where it appears in our code

- `src_web3/phase25/escrow_test.rs`
  Contains unit tests for deposit, withdrawal, and initialization in isolation with mocked state.

- `src_web3/phase25/test_runner.ts`
  Express API that discovers and reports unit test results as part of a continuous integration workflow.

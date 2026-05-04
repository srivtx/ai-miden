# What Is an Integration Test?

## Why it exists (THE PROBLEM)

Unit tests verify individual components, but real programs involve multiple instructions, cross-program invocations, and interactions between many accounts.

A program can pass every unit test and still fail when instructions are composed into realistic user workflows.

Account lifecycles and state interactions are more complex than any single function can reveal.

Integration tests surface bugs that only appear when multiple components interact in realistic ways.

## Definition

An integration test is an automated test that verifies multiple components or instructions working together as a complete system.

It exercises realistic user scenarios such as depositing, listing, buying, and withdrawing in sequence to ensure the entire workflow behaves correctly and maintains consistency.

## Real-life analogy

Imagine testing a car by only checking the engine on a bench.

That tells you the engine runs, but not whether it connects properly to the transmission, whether the brakes stop the wheels, or whether the steering actually turns the car.

Integration testing is taking the assembled car to a test track, accelerating, braking, and cornering to verify that every subsystem works together as designed.

Software integration tests do the same by running full user journeys across multiple program instructions.

## Tiny numeric example

Consider a marketplace integration test sequence:

| Step | Instruction | Accounts Involved | Expected State |
|------|-------------|-------------------|----------------|
| 1 | Initialize escrow | Payer, escrow, mint | Escrow created with 0 balance |
| 2 | Deposit 50 SOL | User, vault, token account | Vault holds 50, user balance -50 |
| 3 | List NFT | Seller, escrow, listing | NFT in escrow, listing active |
| 4 | Buy NFT | Buyer, seller, vault, listing | Payment transferred, NFT to buyer |
| 5 | Withdraw proceeds | Seller, vault, token account | Seller receives 47.5 SOL after fees |

This five-step workflow validates atomicity, fee logic, and state transitions across instructions in a single test.

If any step fails, the entire test fails, ensuring no partial success is accepted.

This atomicity mirrors the on-chain behavior that users will experience.

Integration tests are the closest thing to real user journeys before deployment.

## Common confusion

- "Integration tests replace unit tests."
  They complement each other.
  Unit tests catch logic fast, integration tests catch interaction bugs between modules.

- "Integration tests are just big unit tests."
  Integration tests use real or simulated program environments with actual account creation and CPI.

- "I need a live devnet for integration tests."
  Solana integration tests run in ProgramTest or local validators without network latency or cost.

- "Integration tests are too slow to run often."
  Local test validators complete in seconds and should run on every commit to catch regressions early.

- "If unit tests pass, integration tests are redundant."
  Cross-program invocation bugs, account ordering issues, and PDA derivation errors often only appear in integration tests.

- "Integration tests must test the UI."
  UI testing is end-to-end.
  Integration tests focus on program instructions and state without front-end code.

- "Integration tests cannot test failure paths."
  Well-designed integration tests deliberately trigger insufficient balance, unauthorized access, and overflow to verify error handling.

## Where it appears in our code

- `src_web3/phase25/escrow_test.rs`
  Contains integration tests that initialize, deposit, list, buy, and withdraw in a single test function.

- `src_web3/phase25/test_runner.ts`
  Express API that runs integration test suites and reports pass/fail for complete workflows.

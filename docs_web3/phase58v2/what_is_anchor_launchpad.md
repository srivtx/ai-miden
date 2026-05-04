# What Is an Anchor Launchpad

## The Problem

Building a token sale launchpad on Solana requires handling account validation, ownership checks, and cross-program invocations manually in raw Rust. This is error-prone and time-consuming. A single missing ownership check can drain a program's treasury. Anchor provides a declarative framework that auto-generates these safety checks, letting developers focus on business logic like tiered allocations and vesting schedules.

## Definition

An Anchor Launchpad is a token sale platform built using the Anchor framework on Solana. It uses Anchor's macro-driven account validation, IDL generation, and CPI helpers to create secure programs for registering projects, enforcing whitelist tiers, capping individual allocations, and managing token distributions.

## How It Works (6 Steps)

1. **Define Accounts**: The developer writes Rust structs with `#[account]` and `#[derive(Accounts)]` macros. Anchor generates deserialization, ownership, and signer verification automatically.

2. **Register Project**: The admin calls a `register_project` instruction. Anchor creates a project account on-chain with parameters like token mint, soft cap, hard cap, start time, and end time.

3. **Set Tiers**: The admin configures whitelist tiers with minimum and maximum allocation amounts per wallet. Anchor validates that the admin is the project authority before storing tier data.

4. **Participate**: A user calls `participate` with their payment tokens. Anchor checks the project is active, the user is whitelisted, the amount is within tier bounds, and the total raised does not exceed the hard cap. It then transfers payment tokens to the project's vault.

5. **Claim Tokens**: After the sale ends and vesting begins, a user calls `claim`. Anchor verifies the vesting schedule: cliff period elapsed, linear unlock accrued, and total claimed does not exceed the user's allocation. It transfers project tokens from the vault to the user.

6. **Admin Withdraw**: After the sale succeeds, the admin withdraws payment tokens from the vault. Anchor enforces that the soft cap was reached and that only the authority can access the funds.

## Real-Life Analogy

Imagine a concert ticket sale. The venue (Anchor) provides the infrastructure: seats (accounts), security (validation), and ticket counters (transactions). The event organizer (admin) sets the rules: VIP sections (tiers), maximum tickets per person (allocation caps), and entry times (sale windows). Attendees (users) buy tickets within those rules. The venue ensures no one sneaks in without a ticket and no one buys more than their limit. Anchor does the same for token sales on Solana.

## Tiny Numeric Example With Actual Anchor Program Flow

Consider a project with these parameters:

- Soft cap: 10,000 USDC
- Hard cap: 100,000 USDC
- Tier 1 (Whitelist): min 100 USDC, max 1,000 USDC
- Tier 2 (Public): min 50 USDC, max 500 USDC
- Token price: 1 USDC = 10 project tokens
- Vesting: 3-month cliff, then linear over 12 months

User A is in Tier 1 and sends 500 USDC. Anchor validates:

1. Project account exists and sale is open.
2. User A is in Tier 1 whitelist.
3. 500 USDC is between 100 and 1,000.
4. Total raised (before this) is 45,000 USDC. Adding 500 does not exceed 100,000.

Anchor transfers 500 USDC from User A to the project vault. It records User A's allocation as 5,000 project tokens.

After 3 months, User A claims. Anchor calculates: 3 months cliff passed, linear unlock begins. At 6 months, 25% unlocked = 1,250 tokens. Anchor transfers 1,250 tokens from the vault to User A's token account.

## Common Confusion

- Does Anchor replace Solana programs? No. Anchor is a framework that sits on top of Solana's runtime. You still write Rust, but Anchor generates boilerplate.

- Does Anchor store data automatically? No. You must define account structs and explicitly initialize them with `#[account(init)]`. Anchor only validates what you declare.

- Is Anchor only for TypeScript clients? No. Anchor generates an IDL that any language can use. TypeScript is the most common client, but Python and Rust clients also exist.

- Does Anchor prevent all bugs? No. Anchor checks ownership and signers, but business logic bugs like incorrect price calculations or missing hard cap checks are still the developer's responsibility.

- Can Anchor interact with non-Anchor programs? Yes. Anchor supports Cross-Program Invocations (CPI) to any Solana program, including the SPL Token program and Jupiter's swap program.

- Does Anchor cost more in rent? No. Anchor accounts pay the same rent as raw Solana accounts. Anchor adds a small discriminator byte prefix to accounts, which is negligible.

## Key Properties

1. **Declarative Validation**: Constraints like `has_one = authority` and `constraint = project.start_time < now` are enforced by Anchor at the runtime level.

2. **IDL Generation**: Anchor automatically produces a JSON Interface Definition Language (IDL) file that describes every instruction, account, and type. Client code is generated from this IDL.

3. **CPI Abstraction**: Calling another program (like SPL Token Transfer) requires only a few lines of Anchor code instead of manual instruction building.

4. **Account Discriminators**: Anchor prepends an 8-byte hash to every account. This prevents account type confusion attacks where one account type is passed in place of another.

5. **Test Suite Integration**: Anchor comes with a built-in test runner using Mocha and Chai. It can spin up a local validator, deploy programs, and run end-to-end tests in TypeScript.

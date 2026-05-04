# Phase 58v2 Architecture: Step-by-Step Build

This document describes how to build the launchpad from an empty directory to a deployed, testable system. Each step includes the WHY behind the decision.

## Step 1: Initialize Anchor Project

Run `anchor init launchpad` to create the Anchor workspace. This generates the directory structure, `Anchor.toml`, and a sample program.

**WHY**: Anchor enforces a standardized workspace layout. Starting from `anchor init` ensures the build system, test runner, and IDL generator all work out of the box. Without this structure, you would manually configure Rust crates, Solana CLI paths, and TypeScript bindings, which is error-prone for beginners and wastes time for production teams.

**Commands**:

```bash
anchor init launchpad
cd launchpad
anchor build
```

## Step 2: Design Project Account With Tiered Whitelist

Define the `Project` account struct with fields for authority, token mint, treasury, soft cap, hard cap, start time, end time, and a list of `Tier` structs. Each `Tier` contains a name, minimum allocation, maximum allocation, and a list of whitelisted wallets.

**WHY**: A single `Project` account is cheaper to fetch than multiple accounts. Tiers are embedded because they are read together during participation. Using a whitelist per tier instead of a global list allows differentiated access (e.g., early contributors get higher caps). Without tiers, a single whale could register multiple wallets and bypass caps more easily.

**Key Design Decision**: Store whitelisted wallets as a `Vec<Pubkey>` inside each tier. Anchor has a maximum account size limit, so for very large whitelists, you would use a Merkle tree. For this phase, a direct list is sufficient for up to 1,000 wallets.

## Step 3: Implement Participation With Allocation Caps

Write the `participate` instruction. It takes the project account, user token account, project treasury token account, and token program. The instruction checks:

- Current time is between `start_time` and `end_time`.
- User's wallet is in a tier whitelist.
- Amount is between tier min and max.
- Total raised plus amount does not exceed `hard_cap`.

It then transfers the payment tokens via SPL Token CPI and records the user's participation in a `UserParticipation` account.

**WHY**: On-chain validation prevents front-running and bypassing rules. Storing participation in a separate `UserParticipation` account per user allows parallel writes (no lock contention on the main `Project` account). Without allocation caps, a single transaction could fill the hard cap and exclude all other users.

**Key Design Decision**: The `UserParticipation` account is a PDA (Program Derived Address) seeded by the project pubkey and user wallet. This guarantees uniqueness and prevents duplicate participation records.

## Step 4: Add Jupiter Swap for Payment Routing

In the Express API, when a user wants to pay in a non-USDC token, the server calls Jupiter's `/quote` API to get a swap route from the input token to USDC. It then calls Jupiter's `/swap` API to build a transaction. The API combines the Jupiter swap instruction with the launchpad `participate` instruction into a single transaction.

**WHY**: Users hold diverse token portfolios. Requiring USDC-only payments creates friction and reduces participation. Jupiter finds the best price across all Solana DEXes, so users get a fair rate. Combining swap and participate into one transaction ensures atomicity: if the swap fails, the user does not accidentally participate with a different amount.

**Key Design Decision**: The swap is executed client-side (or API-side) before or alongside the participate instruction. The launchpad program itself only accepts the output token (USDC) to keep the Rust code simple and auditable.

## Step 5: Build Vesting With Anchor

Create a separate `vesting` program with a `VestingSchedule` account. Fields include: beneficiary, token mint, total amount, cliff time, end time, total claimed, and created at. The `claim` instruction calculates unlocked amount as:

- If now < cliff: 0
- If now >= end: total amount
- Else: total amount * (now - cliff) / (end - cliff)

Subtract `total_claimed` to get the claimable amount. Transfer via SPL CPI. Update `total_claimed`.

**WHY**: Separating vesting into its own program keeps the launchpad program small and focused. A small program is easier to audit and cheaper to deploy. The linear unlock formula prevents cliff dumping and aligns long-term incentives. Without on-chain vesting, the project team could manually release tokens arbitrarily, breaking trust.

**Key Design Decision**: The vesting account is owned by the vesting program, but the tokens are held in an associated token account owned by a PDA. This PDA signs the transfer instruction via CPI.

## Step 6: Add Refund Logic With Soft Cap Check

Implement a `refund` instruction in the launchpad program. After `end_time`, if `total_raised < soft_cap`, users can call `refund`. The instruction verifies:

- Now > `end_time`.
- `total_raised < soft_cap`.
- The caller has a `UserParticipation` account.

It transfers the full payment amount from the treasury back to the user's token account and closes the `UserParticipation` account to reclaim rent.

**WHY**: A soft cap protects users from funding projects that fail to attract minimum interest. If only 10% of the soft cap is raised, the project likely lacks market validation. Refunding preserves capital for users. Closing the participation account reclaims rent, which is good UX.

**Key Design Decision**: Refunds are permissionless. Any user can call refund for their own participation. The project authority cannot block refunds if the soft cap is missed.

## Step 7: Build TypeScript Client

Write `launchpad_api.ts`, an Express server that acts as a TypeScript client to the Anchor programs. It loads the IDL, creates an Anchor Provider with a payer wallet, and exposes REST endpoints. Each endpoint constructs the appropriate Anchor instruction, adds recent blockhash and fee payer, signs, and submits to the RPC.

**WHY**: A REST API lowers the barrier for frontend developers. They can call familiar HTTP endpoints instead of learning Solana transaction construction. The API also handles Jupiter swap composition, which is complex to do purely in a browser. However, the API is stateless: all state lives on-chain, so the API can be replaced or replicated without data loss.

**Key Design Decision**: The API holds a payer keypair for transaction fees but never holds user funds. User wallets sign their own transactions. The API can optionally be configured as a relayer (paying fees) or require users to sign via a connected wallet.

## Step 8: Test on Devnet

Deploy both programs to devnet. Create a test project with a test token mint. Whitelist a few wallets. Simulate participation, oversubscription, vesting claims, refunds, and admin withdrawals. Verify on Solana Explorer that accounts are created, tokens are transferred, and vesting schedules are enforced.

**WHY**: Devnet is the production-like environment for Solana. It uses real consensus, real transaction fees (in devnet SOL), and real account rent. Testing on devnet catches RPC latency issues, blockhash expiration, and account size limits that local tests might miss. It is the final gate before mainnet deployment.

**Key Design Decision**: Use `anchor deploy --provider.cluster devnet` and fund the deployer wallet with devnet SOL from the faucet. Write integration tests in TypeScript that run against devnet RPC. Keep a separate `.env` file for devnet and mainnet RPC URLs.

## Technology Stack

| Layer | Technology | Role |
|-------|------------|------|
| Smart Contract | Rust + Anchor | On-chain program logic and account validation. |
| Token Standard | SPL Token | Payment and project token transfers. |
| Liquidity | Jupiter Aggregator | Swap any token to USDC for launchpad payments. |
| API Server | TypeScript + Express | REST interface for frontend clients. |
| Client Library | @coral-xyz/anchor | TypeScript bindings to Anchor programs. |
| RPC | Solana Devnet / Mainnet | Blockchain network for transaction submission. |
| Wallet | Phantom / Solflare | User key management and transaction signing. |

## Deployment Checklist

1. [ ] Run `anchor build` with zero warnings.
2. [ ] Run `anchor test` on local validator with 100% pass rate.
3. [ ] Fund deployer wallet with devnet SOL.
4. [ ] Run `anchor deploy --provider.cluster devnet`.
5. [ ] Record deployed program IDs in `Anchor.toml` and `.env`.
6. [ ] Run `launchpad_api.ts` against devnet and test all endpoints.
7. [ ] Verify transactions on Solana Explorer (devnet).
8. [ ] Document mainnet migration steps (switch RPC, fund with real SOL, redeploy).

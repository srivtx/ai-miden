# Phase 55v2 Architecture: Step-by-Step Build from Scratch

This document walks through building the Phase 55v2 yield farm from an empty directory to a deployed devnet protocol. Each step explains why specific decisions are made.

## Step 1: Initialize Anchor Project

**What you do:**

Install Anchor CLI and run `anchor init farm`. This creates a workspace with `Anchor.toml`, `Cargo.toml`, and a starter program.

**Why:**

Anchor provides boilerplate for account validation, instruction serialization, and CPI helpers that would require hundreds of lines of raw Rust. Without Anchor, you would manually write Borsh serializers, verify account ownership in every instruction, and construct CPI account metas by hand. Anchor's `#[derive(Accounts)]` macro enforces constraints at compile time, preventing entire classes of exploits like missing signer checks or unchecked account owners.

**Configuration:**

Set `solana_version` in `Anchor.toml` to the latest stable release. Set `cluster = "devnet"` for testing. Add `spl-token-2022` to dependencies because the default Anchor template only includes standard SPL token support.

## Step 2: Create Farm Pool with Reward-Per-Share Accumulator

**What you do:**

Define the `Pool` account struct with fields: `reward_per_share: u128`, `total_staked: u64`, `reward_rate: u64`, `last_update_time: i64`, `authority: Pubkey`, `stake_mint: Pubkey`, `reward_mint: Pubkey`, `stake_vault: Pubkey`, `reward_vault: Pubkey`.

Define the `UserInfo` account struct with fields: `staked_amount: u64`, `reward_debt: u128`, `owner: Pubkey`, `pool: Pubkey`.

Implement `create_pool` instruction that initializes these accounts with `reward_per_share = 0` and `total_staked = 0`.

**Why:**

The reward-per-share accumulator is the mathematical core of any scalable yield farm. Without it, you would need to iterate through all users on every reward deposit, which exceeds Solana's compute budget with more than a few dozen users. The accumulator pattern makes pool updates O(1) regardless of user count.

Using u128 for `reward_per_share` and `reward_debt` is necessary because the formula involves dividing total rewards by total staked tokens, then multiplying by individual stake amounts. With u64, intermediate values overflow when pools have millions of tokens and high reward rates. The 1e18 precision factor ensures rounding errors remain sub-atomic.

Separating `stake_mint` and `reward_mint` allows the farm to accept one token (e.g., USDC) as stake and emit a different token (e.g., a governance token) as rewards. This is the standard pattern for liquidity mining programs.

## Step 3: Implement Stake/Unstake with Real SPL Token Transfers

**What you do:**

Implement `stake` instruction that: (a) updates the pool's reward-per-share accumulator, (b) updates the user's reward debt, (c) increments `total_staked`, (d) performs a CPI `transfer_checked` from the user's token account to the farm's stake vault.

Implement `unstake` instruction that: (a) updates the pool accumulator, (b) calculates pending rewards and transfers them via CPI, (c) decrements `total_staked`, (d) performs a CPI `transfer_checked` from the farm's stake vault back to the user's token account.

**Why:**

Real token transfers are non-negotiable for production. A yield farm that only updates counters without moving tokens is not a yield farm; it is a database. Students must learn CPI because every DeFi protocol on Solana interacts with the token program through CPI. The stake vault must be a Program Derived Address (PDA) so the program can sign for outgoing transfers during unstake. Without a PDA vault, the program has no authority to move tokens out of an account.

Using `transfer_checked` instead of `transfer` validates token decimals, preventing decimal mismatch attacks where a malicious mint claims 6 decimals but actually uses 9. This is a real exploit vector that has occurred on Solana mainnet.

Updating the reward accumulator before changing stake amounts is critical. If you update `total_staked` before calculating reward increases, the new stake dilutes rewards that should have been distributed based on the old total. This ordering bug would cause users to receive incorrect reward amounts.

## Step 4: Add Reward Distribution with Actual CPI Transfers

**What you do:**

Implement a `deposit_rewards` instruction that transfers reward tokens from the funder's account to the farm's reward vault via CPI, then updates `reward_per_share` based on the deposited amount and time elapsed.

Implement `claim` instruction that calculates pending rewards using `(user.stake * pool.reward_per_share) - user.reward_debt`, then performs a CPI transfer from the reward vault to the user's reward token account.

**Why:**

Reward deposits must be real transfers. A common educational mistake is to increment a `total_rewards` counter without transferring tokens. This breaks when users try to claim because the reward vault has no balance. Real transfers ensure the invariant `reward_vault_balance >= sum(pending_rewards)` always holds.

The `deposit_rewards` instruction updates `reward_per_share` using the formula `(deposited_amount * PRECISION) / total_staked`. This is the moment when rewards become "earned" by stakers. Before this call, deposited tokens are just sitting in the vault. After this call, the accumulator increases and every user's proportional share is locked in mathematically.

Claim instructions must be idempotent. If a user claims twice in the same block, the second claim must return zero because `reward_debt` was updated to the current `reward_per_share` during the first claim. This prevents double-spending of rewards.

## Step 5: Build Auto-Compounder Service

**What you do:**

Create a standalone TypeScript service (`compounder.ts`) that connects to the network, fetches all `UserInfo` accounts for a pool, calculates pending rewards, filters users where pending rewards exceed a threshold, builds `compound` transactions, and submits them.

The `compound` instruction in the farm program claims pending rewards and immediately stakes them in a single atomic transaction.

**Why:**

Auto-compounding is not a luxury in DeFi; it is infrastructure. Users who do not compound leave 30-50% of potential APY on the table due to simple versus compound interest. A protocol that provides auto-compounding retains more total value locked (TVL) because users do not need to withdraw to manually optimize returns.

The service must be off-chain because on-chain programs cannot schedule future transactions or pay for compute with their own balance without an external trigger. Solana programs are reactive (they run when called), not proactive.

Economic filtering is essential. If the bot compounds $0.50 of rewards but pays $0.10 in transaction fees, the user loses 20% to gas. The threshold must be configurable per pool based on reward rate, token price, and network congestion.

## Step 6: Add Boost NFT with Multiplier

**What you do:**

Create a separate `boost` program with a `BoostNft` account containing `multiplier_bps: u16` (e.g., 20000 for 2x). Mint NFTs through this program. In the farm program, add a `boost_nft` optional account to `stake` and `claim`. If provided, verify the NFT is owned by the user and was minted by the boost program, then apply the multiplier to reward calculations.

**Why:**

Separating boost logic into its own program follows Solana's composability model. The farm program does not need to know how NFTs are minted, what metadata they contain, or what their supply cap is. It only needs to verify the NFT exists and read its multiplier. This allows the NFT collection to evolve independently (e.g., adding new tiers) without upgrading the farm program.

Using basis points (1/100 of a percent) for multipliers avoids floating point. A 2.5x boost is 25000 bps. All math remains in integer operations, which are deterministic and safe on-chain.

Verifying NFT ownership on every claim prevents users from borrowing an NFT to claim boosted rewards, then returning it. The check must happen at claim time, not just at stake time, because ownership can change between transactions.

## Step 7: Test on Devnet

**What you do:**

Write integration tests using `anchor test` that: create a pool, mint test tokens, stake tokens, verify vault balance increased, wait for time to pass (or use `warp_to_timestamp` in tests), deposit rewards, claim rewards, verify user balance changed, unstake, verify vault balance decreased, and test boost NFT multiplier.

Run `anchor build` to compile. Run `anchor deploy` to devnet. Run `anchor test --provider.cluster devnet` to execute tests against the deployed program.

**Why:**

Testing on devnet validates the entire stack: program deployment, account creation, token minting, CPI calls, and PDA derivation. Local tests use a validator with unlimited compute and instant time travel. Devnet has real network latency, real compute budgets, and real rent costs. A program that passes local tests but fails on devnet usually has a compute unit issue or a rent exemption miscalculation.

Integration tests must verify token balances, not just program state. A test that checks `user_info.staked_amount == 1000` does not prove the tokens were transferred. You must query the token account balance before and after to confirm real movement.

The `deploy.sh` script automates building, verifying the IDL matches the deployed program, and setting up the devnet environment. Automation prevents human error in deployment (e.g., deploying to the wrong cluster or using an outdated binary).

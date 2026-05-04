# Phase 57: Architecture — Step-by-Step Build from Scratch

This document explains the construction of the complete prediction market system from an empty directory to a working deployment. Each step includes the rationale (WHY) behind the design decision.

---

## Step 1: Design Market and Outcome Accounts

**What we do**: Define the on-chain data structures that represent a prediction market and its outcomes.

**Implementation details**:
- Create a `Market` account that stores the market creator, the question string, the collateral mint (for example, USDC), the expiration timestamp, the resolution state (Unresolved, Resolving, Resolved), the winning outcome index, and the AMM pool state.
- Create an `Outcome` account (or embedded array) that stores the outcome name, the associated token mint for outcome shares, and the total supply of shares.
- Use Program Derived Addresses (PDAs) for deterministic account addresses so clients can derive them from seeds (for example, `["market", creator_pubkey, market_id"]`).

**WHY**:
- We need a `Market` account to hold global state because every instruction (buy, sell, resolve) must read and update shared parameters (like resolution status and collateral reserves).
- We store the collateral mint to ensure that only one type of token backs the shares, preventing confusion and simplifying collateral accounting.
- We embed expiration timestamps so the oracle program can reject early resolutions and so the market can enter a default state if the oracle never reports.
- We use PDAs because they allow permissionless clients to pre-compute account addresses without relying on a central registry, and they guarantee that no external signer can forge a market account.
- We keep the outcome data on-chain (rather than off-chain) because the smart contract must know which mint corresponds to which outcome in order to mint, burn, and settle shares correctly.

---

## Step 2: Implement Share Minting (YES/NO)

**What we do**: Write the instruction that creates a market and mints the initial pair of outcome shares.

**Implementation details**:
- The `create_market` instruction initializes the `Market` account, creates two SPL token mints (YES and NO), and mints an initial supply of shares to a temporary escrow account owned by the market program.
- The creator deposits collateral into the market's collateral vault.
- The number of YES shares minted equals the number of NO shares minted, and both equal the collateral deposited (for example, 100 USDC yields 100 YES and 100 NO shares).

**WHY**:
- We mint equal pairs of YES and NO shares because the shares are complementary: one YES plus one NO is always redeemable for exactly 1 unit of collateral. This invariant guarantees that the market is fully collateralized at all times.
- We create separate mints for each outcome so that shares are distinguishable, fungible within their own outcome, and tradeable on standard SPL token infrastructure.
- We escrow the initial shares in a program-owned account rather than sending them to the creator so that the AMM pool can control the initial liquidity and the creator cannot dump shares unfairly before the market opens.
- We require collateral deposit at creation so the contract always has sufficient assets to back every share in circulation; there is no fractional reserve risk.

---

## Step 3: Build AMM for Share Trading

**What we do**: Implement an automated market maker that prices shares continuously based on a constant-product curve.

**Implementation details**:
- The AMM maintains reserves of collateral (USDC), YES shares, and NO shares.
- For a binary market, we model the pool as two separate constant-product pairs: collateral vs YES, and collateral vs NO. Alternatively, we use a unified three-token constant-product pool `x * y * z = k`.
- The `buy` instruction transfers collateral from the trader to the pool, calculates the shares to mint using the constant-product formula, deducts a trading fee, and transfers the shares to the trader.
- The `sell` instruction burns the trader's shares, calculates the collateral to return using the constant-product formula, deducts a trading fee, and transfers collateral back.

**WHY**:
- We choose a constant-product AMM because it is battle-tested (Uniswap, Serum AMMs), requires no external price oracle to operate, and provides infinite liquidity within the price bounds of zero to one.
- We apply a trading fee because it compensates liquidity providers for the risk of impermanent loss and prevents infinite wash-trading that would drain the pool without adding information.
- We use the constant-product formula `x * y = k` because it ensures that large trades move the price more than small trades, which accurately reflects the market's sensitivity to new information and prevents price manipulation through small orders.
- We deduct fees before updating the pool reserves so that the fee revenue accrues directly to liquidity providers by increasing the value of the underlying reserves.

---

## Step 4: Add Oracle Resolution

**What we do**: Integrate the oracle program so that only trusted, timely, and verifiable outcomes can trigger settlement.

**Implementation details**:
- The `resolve` instruction on the market program invokes the oracle program via Cross-Program Invocation (CPI).
- The oracle program verifies that the signer is a registered oracle, that the market has expired (or the event has concluded), and that the signed attestation matches the market ID and outcome.
- The oracle program sets the market's outcome on its own state account, which the market program reads.
- The market program updates its `resolution_state` to `Resolved` and records the winning outcome index.

**WHY**:
- We separate oracle logic into its own program because resolution is a critical security boundary. Isolating it limits the attack surface: a bug in the trading logic cannot compromise the oracle's trusted key list, and vice versa.
- We use CPI because it allows the market program to atomically verify the oracle's decision and update its own state in a single transaction, preventing race conditions where the market resolves to one outcome but a trader tries to claim against another.
- We enforce expiration checks in the oracle program (not just the market program) so that even if the market program is upgraded or buggy, the oracle cannot be tricked into resolving early.
- We require a signed attestation rather than a simple pubkey check so that the resolution payload is non-repudiable and can be audited by third parties who replay the transaction.

---

## Step 5: Implement Automated Settlement

**What we do**: Allow winning shareholders to redeem their shares for collateral after resolution.

**Implementation details**:
- The `claim` instruction checks that the market is in the `Resolved` state, verifies that the trader is burning shares of the winning outcome, and transfers 1 unit of collateral per share from the market vault to the trader.
- The instruction burns the shares permanently so they cannot be double-claimed.
- If any collateral remains after all claims (for example, due to unclaimed losing shares or rounding), it is sent to a protocol treasury or returned to the market creator after a timeout.

**WHY**:
- We require burning shares because a share is a claim on collateral; once redeemed, the claim must be destroyed to prevent the same share from being redeemed twice. This is the on-chain equivalent of tearing up a winning lottery ticket.
- We pay exactly 1 unit of collateral per winning share because the market was fully collateralized at creation. This one-to-one redemption is the fundamental promise that makes the share valuable.
- We automate settlement through a permissionless `claim` instruction so that traders do not need to trust the market creator to send funds manually. The smart contract acts as the neutral settlement agent.
- We handle dust remaining in the vault because blockchain arithmetic involves integer division. A small treasury account or creator refund prevents collateral from being locked forever due to rounding errors.

---

## Step 6: Add Liquidity Provision

**What we do**: Enable users to deposit collateral into the AMM pool and earn LP tokens representing their share of the pool.

**Implementation details**:
- The `add_liquidity` instruction accepts collateral from the provider, mints LP tokens proportional to the provider's contribution relative to the total pool value, and updates the AMM reserves.
- The `remove_liquidity` instruction burns LP tokens and returns a proportional mix of collateral, YES shares, and NO shares from the pool reserves.
- Fees accrued from trading increase the total value of the pool, so LP tokens appreciate over time even if the provider never removes liquidity.

**WHY**:
- We mint LP tokens because they represent a fungible, transferable claim on the pool. Without LP tokens, tracking each provider's share would require complex accounting and would prevent providers from exiting partially or transferring their position.
- We require proportional collateral deposits (both sides of the market) when adding liquidity because the AMM's pricing formula depends on the ratio of reserves. An unbalanced deposit would instantly shift the price and disadvantage existing traders.
- We return a mix of assets on removal (rather than only collateral) because the pool itself holds a mix. Converting everything to collateral at removal would require an internal swap, which would create unexpected price impact and gas costs for the withdrawing LP.
- We let fees auto-compound in the pool (rather than distributing them manually) because it is gas-efficient and mathematically elegant: the pool's total value grows, so each LP token is worth more, and providers realize gains when they withdraw.

---

## Step 7: Test Resolution and Payout Flows

**What we do**: Write integration tests that exercise the entire lifecycle of a market from creation through resolution to final payout.

**Implementation details**:
- Test 1: Create a market, add liquidity, buy YES shares, resolve to YES, claim winnings, assert correct collateral balance.
- Test 2: Create a market, buy both sides, resolve to NO, assert that YES holders receive nothing and NO holders receive collateral.
- Test 3: Attempt to resolve before expiration and verify that the transaction fails.
- Test 4: Dispute a resolution during the dispute window and verify that the outcome remains in the Resolving state until the window closes.
- Test 5: Add and remove liquidity, assert that the LP token value increases after trades due to fee accrual.

**WHY**:
- We test the full lifecycle because prediction markets have many interacting state machines (market state, oracle state, token balances). Unit tests of individual instructions are insufficient to catch bugs that arise from state transitions.
- We test both outcome directions (YES and NO) because the settlement logic is symmetric but not identical; a bug that only affects one path would be hidden if we only tested the other.
- We test negative cases (early resolution, disputes) because the most expensive failures in smart contracts are not missing features but unauthorized state changes. A market that resolves early could be exploited to steal collateral.
- We test liquidity provider returns because the economic viability of the market depends on LPs being willing to participate. If fees do not accrue correctly, the market will have no liquidity and will fail as a product.

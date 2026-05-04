# What Is Fair Sale Mechanics

## The Problem

Whales with large capital can dominate token sales by buying the majority of supply in seconds, leaving retail users with nothing. This creates centralization and dumps the token price immediately after launch. Fair sale mechanics use allocation caps, tiered whitelists, and proportional distributions to give all participants a meaningful chance to acquire tokens.

## Definition

Fair Sale Mechanics are rules and algorithms designed to prevent whale manipulation in token sales. They include per-wallet allocation limits, tiered access based on community participation, and proportional refund systems when demand exceeds supply. The goal is a broad, decentralized token holder base.

## How It Works (6 Steps)

1. **Whitelist Verification**: Before the sale, users register and prove they are real community members (e.g., Discord activity, wallet age, or staking history). Only whitelisted wallets can participate.

2. **Tier Assignment**: Whitelisted users are assigned to tiers. Tier 1 might be core contributors with higher allocation limits. Tier 2 might be active community members with moderate limits. Tier 3 might be the public with the lowest limits.

3. **Allocation Caps**: Each tier has a hard minimum and maximum. A Tier 2 user must send at least 50 USDC and cannot exceed 500 USDC. This prevents a single wallet from buying 50% of the supply.

4. **Proportional Distribution**: If total demand exceeds the hard cap, the smart contract calculates a ratio. If users collectively oversubscribe by 2x, every participant receives half their intended allocation and is refunded the remainder.

5. **Anti-Bot Measures**: Flash loan attacks and bot sweeps are mitigated by requiring a warm-up period. For example, a wallet must have held a minimum balance of the payment token for 24 hours before the sale starts.

6. **Refund on Failure**: If the soft cap is not reached by the end time, the smart contract allows participants to withdraw their full payment. No tokens are distributed, and the sale is canceled.

## Real-Life Analogy

Imagine a limited-edition sneaker drop. Without fair mechanics, scalpers with bots buy all the shoes in seconds and resell them at 10x the price. With fair mechanics, the store requires a loyalty membership (whitelist), limits each member to one pair (allocation cap), and runs a raffle if demand exceeds stock (proportional distribution). Genuine fans get a fair shot, and the secondary market is healthier.

## Tiny Numeric Example With Actual Oversubscription Logic

A project sells 1,000,000 tokens at 0.10 USDC each, hard cap = 100,000 USDC.

- Tier 1 (100 users): max 1,000 USDC each = 100,000 USDC potential
- Tier 2 (500 users): max 500 USDC each = 250,000 USDC potential
- Tier 3 (2,000 users): max 100 USDC each = 200,000 USDC potential

At sale end, commitments total 180,000 USDC. This exceeds the 100,000 USDC hard cap.

The contract calculates a ratio: 100,000 / 180,000 = 0.5555...

- Tier 1 user who committed 1,000 USDC receives 555.55 USDC worth of tokens and a 444.45 USDC refund.
- Tier 2 user who committed 500 USDC receives 277.77 USDC worth of tokens and a 222.23 USDC refund.
- Tier 3 user who committed 100 USDC receives 55.55 USDC worth of tokens and a 44.45 USDC refund.

Total distributed tokens = 1,000,000. Total refunds = 80,000 USDC. No whale can exceed their tier limit.

## Common Confusion

- Do fair mechanics guarantee everyone gets tokens? No. If demand is extremely high and your tier limit is low, you may still receive a small amount or be fully refunded if the sale is canceled.

- Do allocation caps hurt the project's fundraising? No. While a single whale might have brought in 50,000 USDC, ten community members bringing 5,000 USDC each achieves the same cap with better distribution.

- Are fair sales completely bot-proof? No. Bots can still register multiple wallets. Sybil resistance requires off-chain identity verification or proof-of-humanity mechanisms in addition to on-chain caps.

- Does proportional distribution mean I get less than I paid? No. You receive tokens proportional to your commitment relative to total demand. The remainder is refunded in the payment token.

- Can the team change tiers after the sale starts? No. In a properly designed Anchor program, tier configuration is immutable after the sale begins, enforced by the smart contract.

- Is a whitelist the same as KYC? No. A whitelist is typically a curated list of wallet addresses. KYC involves identity verification with government documents. Fair sales usually use whitelists, not KYC.

## Key Properties

1. **Sybil Resistance**: Tiered whitelists make it economically irrational for a whale to split their capital across thousands of wallets if each wallet has a low cap.

2. **Transparency**: All rules (caps, ratios, start and end times) are encoded in the smart contract and visible on-chain before the sale begins.

3. **Proportional Fairness**: Oversubscription formulas treat every participant equally. No wallet gets priority based on transaction speed or gas fees.

4. **Immutable Rules**: Once deployed, the smart contract enforces the mechanics. The project team cannot retroactively increase caps or extend the sale.

5. **Refund Guarantee**: If the project fails to meet its soft cap, participants retain the right to withdraw their original payment without penalty.

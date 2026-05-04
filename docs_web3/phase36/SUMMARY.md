# Phase 36 Summary: Subscription Payments

## Overview

Phase 36 introduces the mechanics of continuous and recurring value exchange on a blockchain. Because blockchains cannot pull funds automatically like a traditional bank, developers must build smart contracts that model time-based releases. We explored subscriptions, recurring payments, and payment streams as three complementary patterns for automated billing.

## Key Concepts Recap

A subscription payment is an ongoing authorization that lets a merchant claim funds at regular intervals. A recurring payment is a scheduled transfer that repeats until cancellation or fund exhaustion. A payment stream is a linear release of a lump sum over time, allowing the recipient to claim continuously earned funds. All three patterns rely on time or block-based logic, pre-funded escrows, and explicit cancellation rights.

## Code Deliverables

The TypeScript API in `src_web3/phase36/subscription_api.ts` exposes endpoints to create subscriptions, claim periodic payments, initialize payment streams, and cancel active agreements. It simulates escrow balances, computes accrued amounts based on timestamps, and enforces access control so only the payer or payee can modify their own agreements.

## Relationships Between Concepts

Subscriptions are the user-facing concept: "pay 10 USDC per month for storage." Recurring payments are the mechanical implementation: a contract that releases 10 USDC every 30 days. Payment streams are the continuous generalization: instead of releasing monthly chunks, funds flow like water at a constant rate. A subscription can be backed by a stream, and a recurring payment can be viewed as a stream with discrete claim windows.

## Practical Takeaways

Always allow cancellation. Users who feel trapped will avoid your service entirely. Compute accrued amounts using block timestamps or slot numbers, but account for clock drift on Solana. Store agreement terms immutably on-chain so neither party can retroactively alter the rate or duration. Test edge cases such as zero-balance escrows, mid-stream cancellation, and duplicate claims.

## Conclusion

Phases 36 through 40 advance the Web3 curriculum into economic primitives: automated billing, time-locked token releases, decentralized identity, novel voting mechanisms, and cross-chain communication. Subscription payments are the foundation of this module because they teach how to model time and trust in a state machine that has no native concept of calendars or recurring debits.

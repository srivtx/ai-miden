# What Is a Subscription Payment

## Why It Exists

Traditional one-time payments do not fit services that provide ongoing value. A user who wants access to a streaming library, a software license, or a premium API cannot be expected to manually send money every month. Subscription payments automate recurring billing, ensuring that merchants receive predictable revenue and consumers retain uninterrupted access. In Web3, this is harder because blockchains do not pull funds from wallets automatically; users must pre-authorize or deploy smart contracts that release tokens on a schedule.

## Definition

A subscription payment is a financial arrangement where a consumer grants a merchant periodic access to funds in exchange for continuous service. On-chain implementations typically use time-locked escrows, streaming payments, or pre-authorized allowances that a merchant can claim at fixed intervals.

## Real-Life Analogy

Imagine a gym membership. You sign a contract that allows the gym to charge your credit card on the first of every month. You do not need to swipe your card each time you want to enter. The gym knows the payment is coming, and you know your access will not be interrupted. A blockchain subscription works the same way, except the "contract" is a program that releases tokens automatically and the "card" is your wallet balance.

## Tiny Numeric Example

A user subscribes to a decentralized storage provider for 10 USDC per month.

| Month | User Balance Before | Released to Provider | User Balance After | Status |
|-------|--------------------:|---------------------:|-------------------:|--------|
| 1 | 100 USDC | 10 USDC | 90 USDC | Active |
| 2 | 90 USDC | 10 USDC | 80 USDC | Active |
| 3 | 80 USDC | 10 USDC | 70 USDC | Active |
| 4 | 70 USDC | 0 USDC | 70 USDC | Canceled by user |

The user prepaid into an escrow and the provider claimed 10 USDC at the start of each month. When the user canceled after month three, the remaining 70 USDC stayed in their wallet and the provider stopped service.

## Common Confusion

- A subscription is not a loan; the provider does not lend money to the user, they simply claim pre-authorized funds.
- Canceling a subscription does not reverse past payments; already released tokens belong to the merchant.
- A blockchain subscription is not invisible; each claim creates an on-chain transaction with fees.
- Pre-authorizing a large allowance is not the same as paying; the merchant can only claim what the contract permits.
- Subscriptions do not require KYC; they use wallet addresses instead of bank accounts, which is both a feature and a compliance challenge.
- Failed claims do not automatically cancel service; the provider must check balance and act accordingly.
- Subscriptions on different chains are independent; a Solana subscription does not entitle access to an Ethereum service.

## Key Properties

## Where It Appears in Our Code

The subscription API in `src_web3/phase36/subscription_api.ts` models a time-based payment stream where users deposit funds, merchants claim at intervals, and either party can cancel to stop future releases.

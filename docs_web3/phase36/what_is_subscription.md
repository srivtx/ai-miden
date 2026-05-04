# What Is a Subscription Payment

## The Problem

Traditional one-time payments work well when you buy a physical object that you can take home immediately. But most modern services do not work that way. A music streaming platform delivers value every single day. A cloud storage provider keeps your files accessible around the clock. A software license gives you continuous access to tools and updates. If users had to manually send money every time they wanted another month of service, three things would go wrong. First, users would forget to pay and lose access at the worst possible moment. Second, service providers would have unpredictable revenue, making it impossible to hire staff or plan improvements. Third, the constant friction of manual billing would drive users away to competitors who offer smoother experiences. Subscription payments exist to automate this relationship so that value flows continuously in both directions.

In traditional finance, subscriptions are easy because banks and credit card companies can pull money from accounts automatically. You sign a paper or digital agreement once, and the merchant charges you on a schedule. Blockchains do not work this way. A blockchain cannot reach into your wallet and take tokens without your explicit approval every single time. This means Web3 subscriptions require clever workarounds such as pre-funded escrows, streaming payment contracts, or token allowances that merchants can claim at intervals. Building these systems is harder than swiping a credit card, but the benefit is that no bank can freeze your subscription or deny you service based on your location.

## Definition

A subscription payment is a financial arrangement in which a consumer grants a merchant permission to claim funds at regular intervals in exchange for uninterrupted access to a service. In Web3, this arrangement is typically enforced by a smart contract that holds the consumer's tokens in escrow or manages an allowance, releasing a fixed amount to the merchant when each billing period elapses.

## How It Works (Step-by-Step)

1. **Setup and Deposit.** The user connects their wallet to a subscription smart contract and deposits a lump sum of tokens or approves a spending allowance. This step is like handing a prepaid card to the merchant, except the card is a program running on a blockchain. The contract records the start time, the billing interval, and the amount per period.

2. **Time Tracking.** The contract tracks the passage of time using block timestamps or a fixed interval counter. Unlike a calendar app that sends reminders, the blockchain itself becomes the clock. Every time someone interacts with the contract, it checks how many billing periods have passed since the last claim.

3. **Merchant Claim.** When a billing period ends, the merchant calls a claim function on the contract. The contract calculates the exact amount owed based on elapsed periods, verifies that the user's balance or escrow still has enough funds, and transfers the tokens to the merchant. If the merchant forgets to claim, the tokens simply remain available for the next claim; the user is not charged extra.

4. **User Cancellation.** At any point, the user can call a cancel function to stop future claims. The contract stops the time tracking and returns any unclaimed funds in the escrow to the user. Already claimed tokens stay with the merchant because they correspond to service already delivered.

5. **Renewal or Top-Up.** If the user wants to continue after the initial deposit runs out, they can send more tokens to the contract. The subscription resumes without requiring a new agreement or new wallet connection. This is like adding credit to a prepaid phone plan.

## Real-Life Analogy

Imagine you join a gym. On the first day, you fill out a membership form and give the front desk permission to charge your credit card on the first of every month. You do not need to swipe your card each time you walk through the door. The gym knows the payment is coming, and you know your access will not be interrupted as long as your card has funds. If you decide to quit, you call the gym and cancel. They stop charging you, but they do not refund the months you already used. A blockchain subscription works exactly the same way, except the membership form is a smart contract, the credit card is your wallet balance, and the gym claims tokens instead of charging a card.

## Tiny Numeric Example

A user subscribes to a decentralized storage provider for 10 USDC per month. They deposit 100 USDC into a subscription escrow.

| Month | User Balance Before | Released to Provider | User Balance After | Status |
|-------|--------------------:|---------------------:|-------------------:|--------|
| 1 | 100 USDC | 10 USDC | 90 USDC | Active |
| 2 | 90 USDC | 10 USDC | 80 USDC | Active |
| 3 | 80 USDC | 10 USDC | 70 USDC | Active |
| 4 | 70 USDC | 0 USDC | 70 USDC | Canceled by user |

At the start of each month, the provider claims 10 USDC from the escrow. By month four, the user decides they no longer need the service and cancels. The remaining 70 USDC returns to their wallet, and the provider stops delivering storage. The provider keeps the 30 USDC already claimed because it corresponds to three months of service rendered.

## Common Confusion

- **A subscription is a loan where the provider lends money to the user.** No. The provider never lends anything. The user pre-authorizes or pre-deposits their own funds, and the provider claims what is already there.

- **Canceling a subscription reverses past payments.** No. Already released tokens belong to the merchant as payment for service already delivered. Cancellation only stops future releases.

- **A blockchain subscription is invisible and free.** No. Each claim creates an on-chain transaction that requires gas fees. The merchant or the user must pay those fees depending on how the contract is written.

- **Pre-authorizing a large allowance is the same as paying upfront.** No. An allowance is only a permission. The merchant can only claim what the contract permits per interval, and the user can revoke the allowance at any time.

- **Subscriptions require KYC and a bank account.** No. Blockchain subscriptions use wallet addresses instead of bank accounts. This is a feature for privacy but also creates compliance challenges in regulated industries.

- **Failed claims automatically cancel the subscription.** No. If the user's wallet is empty when the merchant tries to claim, the contract typically skips that period. The provider must explicitly check balances and decide whether to pause or terminate service.

## Key Properties

- **Automated but Pull-Based.** The user must pre-authorize funds because blockchains cannot pull money without consent. The merchant initiates each claim.
- **Transparent Scheduling.** All terms are encoded in a public smart contract. Anyone can verify the billing interval, amount, and cancellation rules.
- **Non-Reversible Claims.** Once tokens are claimed for a completed period, they cannot be clawed back unless the contract includes an explicit refund mechanism.
- **Cancellable by Either Party.** Most contracts allow the user to cancel, and some allow the merchant to terminate if the user runs out of funds.
- **Chain-Specific.** A subscription on Solana does not entitle access to an Ethereum service. Each chain requires its own contract.

## Where It Appears in Our Code

The subscription API in `src_web3/phase36/subscription_api.ts` models a time-based payment stream where users deposit funds, merchants claim at intervals, and either party can cancel to stop future releases.

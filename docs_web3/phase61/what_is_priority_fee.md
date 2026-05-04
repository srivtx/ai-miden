# What is Priority Fee?

## The Problem

When the Solana network is congested, the leader includes transactions in a block based on total fee potential. If your transaction pays only the base fee (5,000 lamports), it sits in the queue while higher-paying transactions get landed. The result: your swap fails, your NFT mint misses the window, or your user sees a spinning loader for 30 seconds before a timeout.

## Definition

A priority fee is an additional payment, specified in micro-lamports per compute unit, that you attach to a Solana transaction to signal to the block leader that your transaction should be scheduled earlier in the block. It is purely economic: higher fee equals higher inclusion probability.

## How It Works

1. **Compute unit budget**: You set a maximum compute unit limit for your transaction using the `ComputeBudgetProgram.setComputeUnitLimit` instruction.
2. **Fee estimation**: You query the network (or Helius) for the current fee distribution to determine what fee level lands in the next few blocks.
3. **Priority fee instruction**: You add `ComputeBudgetProgram.setComputeUnitPrice({ microLamports })` to your transaction instructions.
4. **Fee calculation**: Total priority fee = compute units consumed * micro-lamports per compute unit. The base fee of 5,000 lamports is still charged separately.
5. **Leader scheduling**: The block leader orders transactions by total fee potential (base + priority) within the constraints of the block compute limit.
6. **Refund behavior**: If your transaction consumes fewer compute units than the limit you set, you are only charged for actual usage; there is no partial refund mechanism, only accurate metering.

## Real-life analogy

Think of a congested highway toll booth. The base fee is the standard toll everyone pays. The priority fee is an express-lane surcharge. Pay it and you skip the queue; refuse and you wait with everyone else.

## Tiny numeric example

You send a token transfer that consumes 3,000 compute units. You set a priority fee of 10,000 micro-lamports per compute unit.

- Base fee: 5,000 lamports = 0.000005 SOL
- Priority fee: 3,000 CUs * 10,000 micro-lamports = 30,000,000 micro-lamports = 0.03 SOL
- Total fee: 0.030005 SOL

If the network is uncongested and you set 0 micro-lamports, you still pay only the base fee. But during a popular NFT drop, that 0.03 SOL might be the difference between landing in block N or block N+10.

## Common confusion

- No. Priority fees are not bribes to validators. They are protocol-level fees that go to the leader as part of normal block rewards.
- No. A higher priority fee does not increase your compute unit limit. You still cannot exceed the 1.4 million CU per-transaction cap.
- No. Priority fees are not refundable if your transaction fails. Failed transactions still consume compute and still pay fees.
- No. Setting `setComputeUnitPrice` without `setComputeUnitLimit` works, but the default limit may over-estimate your usage and cause you to overpay relative to need.
- No. Priority fees are not the same as JITO tips. JITO tips go to the Jito relayer; priority fees go to the Solana block leader.
- No. You cannot set a priority fee after signing. It must be an instruction in the transaction before you sign and send.

## Key properties

1. **Micro-lamport granularity**: Priced per compute unit in units of 0.000001 lamport.
2. **Leader-driven inclusion**: The current block leader orders transactions by total economic value.
3. **Non-refundable**: Paid whether the transaction succeeds or fails.
4. **Composable with base fee**: Added on top of the mandatory 5,000 lamport base fee.
5. **Estimatable**: APIs like Helius `getPriorityFeeEstimate` expose market-driven fee distributions.

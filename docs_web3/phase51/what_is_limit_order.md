# What Is a Limit Order?

## The Problem

In a standard AMM swap, you accept whatever price the pool offers at the exact moment you submit the transaction. If the market is volatile, you might get a much worse price than you expected. This is called slippage, and it can be severe during high-volume events. Traders often want to say: "I will buy Token A, but only if the price drops to X." Without limit orders, the only way to achieve this on-chain is to watch the blockchain manually and submit a swap at the exact right moment, which is impractical and expensive.

## Definition

A limit order is an instruction to buy or sell an asset at a specific price or better. In the context of a decentralized exchange, an on-chain limit order is a recorded intent that sits in a smart contract or order book until the market price crosses the specified threshold, at which point it becomes eligible for execution by a keeper, solver, or the trader themselves.

## How It Works (6 Steps)

1. **Deposit Collateral**: The trader locks the tokens they intend to sell into the limit order program. This proves they have the funds and prevents empty promises.
2. **Define the Price**: The trader specifies the exact limit price and the amount they want to buy or sell. For example: "Sell 100 USDC for Token A at a price of 2.0 USDC per Token A."
3. **Store the Order**: The program records the order in an on-chain account, often sorted by price and time in an order book data structure.
4. **Monitor the Market**: Either the trader, a bot, or a decentralized keeper network watches the AMM pool price or an oracle feed.
5. **Trigger Execution**: When the pool price crosses the limit price, the keeper submits a transaction to execute the order. The program transfers the sold tokens to the market and the bought tokens back to the trader.
6. **Clean Up**: The executed order is removed from the book. If the trader cancels before execution, the original tokens are refunded.

## Real-life Analogy

Imagine you want to buy a vintage watch, but you refuse to pay more than $500. You tell a trusted shopkeeper: "If anyone brings in this watch and asks $500 or less, buy it for me immediately. I am leaving the money with you." The shopkeeper holds your cash. Days later, a seller arrives asking $480. The shopkeeper completes the deal on your behalf. You did not have to stand in the shop every day.

## Tiny Numeric Example

- Token A is currently trading at 3.00 USDC.
- You place a limit order: "Buy 10 Token A at 2.50 USDC each."
- You lock 25.00 USDC in the order contract.
- The market dips. The AMM pool price hits 2.48 USDC.
- A keeper sees this and triggers your order.
- The contract sends your 25.00 USDC to the liquidity pool.
- You receive 10 Token A.
- If the price never hits 2.50, your 25.00 USDC remains locked until you cancel.

## Common Confusion

- **No.** A limit order is not guaranteed to execute. If the market never reaches your price, it remains open indefinitely or until cancelled.
- **No.** It does not execute instantly at the current market price. That is a market order.
- **No.** You cannot place a limit order without depositing the tokens first. The program must hold the collateral.
- **No.** Execution does not happen automatically by magic. It requires an external party (you, a bot, or a keeper) to submit the trigger transaction and pay the gas fee.
- **No.** It is not the same as a stop-loss. A stop-loss triggers to prevent further losses, usually on the downside; a limit order triggers to capture a desired entry or exit price.
- **No.** On-chain limit orders do not require a centralized exchange. They are fully decentralized if the execution logic lives in a smart contract.

## Key Properties

1. **Price Certainty**: The trader knows the exact worst-case price they will accept, eliminating slippage surprises.
2. **Capital Lockup**: Funds are reserved in the contract, so they cannot be used elsewhere until the order executes or is cancelled.
3. **Keeper Dependency**: Execution relies on an external observer to submit the transaction when conditions are met.
4. **Gas Efficiency**: Orders can be batched or executed in groups to amortize transaction costs across many traders.
5. **Composable**: Limit order protocols can be combined with other DeFi primitives, such as using filled orders as collateral in lending protocols.

## Where It Appears

- dYdX (on-chain order book with limit orders)
- 1inch Limit Order Protocol
- CoW Protocol (intent-based trading with limit prices)
- Serum / OpenBook on Solana
- Uniswap v3 range orders (a form of limit order using concentrated liquidity positions)

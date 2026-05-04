# What Is Slippage Protection

## Why It Exists

Prices in automated market makers move continuously as reserves shift, meaning the quoted price at submission time may differ from the execution price by the time the transaction confirms. Slippage protection allows traders to specify the worst price they are willing to accept, automatically reverting the transaction if market movement exceeds their tolerance. Without this guard, users are fully exposed to MEV bots and ordinary volatility.

## Definition

Slippage protection is a smart contract constraint that cancels a trade if the executed exchange rate deviates from the quoted rate by more than a user-defined percentage. It acts as a circuit breaker against both malicious manipulation and benign market movement.

## Real-Life Analogy

Imagine ordering a custom sofa advertised at one thousand dollars with delivery scheduled for next month. You sign a contract stating that if the manufacturer raises the price above one thousand one hundred dollars before delivery, the order is automatically canceled and your deposit is returned. This clause protects you from price hikes while still allowing normal fluctuations within your tolerance.

## Tiny Numeric Example

A user wants to swap 1,000 USDC for TOKEN_A at a quoted rate of 2.00 TOKEN_A per USDC:

| Scenario | Quoted Output | Slippage Tolerance | Minimum Acceptable | Actual Output | Result |
|----------|--------------|--------------------|--------------------|---------------|--------|
| Normal volatility | 2,000 TOKEN_A | 1% | 1,980 TOKEN_A | 1,990 TOKEN_A | Executes |
| Front run | 2,000 TOKEN_A | 1% | 1,980 TOKEN_A | 1,970 TOKEN_A | Reverts |
| High tolerance | 2,000 TOKEN_A | 5% | 1,900 TOKEN_A | 1,920 TOKEN_A | Executes |

A 1% tolerance blocks the front run, while a 5% tolerance would allow it.

## Common Confusion

- Slippage protection is not a fee; it is a cancellation threshold that costs only the failed transaction gas.
- Zero slippage is not safer; it causes frequent reverts from normal market noise, wasting fees.
- Slippage tolerance does not set the price; the market still determines the exact rate within the accepted band.
- A transaction reverting from slippage is not a bug; it is the protection working as intended.
- Slippage settings are not universal; stable pairs can use 0.1%, while exotic pairs may need 3% or more.
- Slippage protection does not stop all MEV; it limits the extractable value but does not prevent ordering manipulation.
- Deadlines and slippage work together; a deadline prevents stale transactions, while slippage prevents unfair prices.

## Key Properties
## Where It Appears in Our Code

Slippage validation is implemented in `src_web3/phase33/protected_swap/src/lib.rs`, where the `swap` instruction computes the expected output and rejects any result below the user's specified minimum.

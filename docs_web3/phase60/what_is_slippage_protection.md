# What Is Slippage Protection?

## The Problem

In decentralized finance, prices change between the moment a user sees a quote and the moment their transaction is confirmed on-chain. On Solana, this window can be as short as a few hundred milliseconds, but during volatile market conditions or high network congestion, prices can move dramatically. Without protection, a user who expects to receive 100 USDC for their swap might only receive 85 USDC because the liquidity pool shifted while their transaction was pending. This price movement is called slippage. It is caused by other traders executing before you, large orders moving the pool's price curve, or arbitrage bots rebalancing pools. Slippage protection is the mechanism that prevents users from accepting disastrously worse prices than they agreed to.

## Definition

Slippage protection is a safety parameter in a token swap that specifies the maximum acceptable difference between the quoted output amount and the actual executed output amount. It is expressed as a percentage or as basis points (hundredths of a percent). When a swap transaction is built, the minimum acceptable output amount is hardcoded into the on-chain instruction. If the actual market price moves beyond this threshold before the transaction executes, the smart contract automatically rejects the transaction and no tokens are swapped. This gives the user a guaranteed floor on their trade outcome.

## How It Works (6 Steps)

**Step 1: User Sets Tolerance.** The user or application specifies a slippage tolerance when requesting a quote. Common values are 0.5% (50 basis points) for stable pairs and 1% to 3% (100 to 300 basis points) for volatile or low-liquidity tokens. This tolerance reflects the user's risk appetite and the expected volatility of the pair.

**Step 2: Quote Computes Minimum Output.** The quoting engine takes the estimated output amount and reduces it by the slippage percentage. For example, if the quote is 100 USDC and slippage is 1%, the minimum output becomes 99 USDC. This floor value is returned in the `otherAmountThreshold` field of the Jupiter quote response.

**Step 3: Transaction Embeds Threshold.** When the swap transaction is built, the minimum output amount is encoded directly into the smart contract instruction as an immutable parameter. It is part of the transaction data that gets signed by the user. Neither the user nor any third party can alter this value after signing without invalidating the signature.

**Step 4: Transaction is Submitted.** The signed transaction is broadcast to the Solana network. It enters the leader's transaction queue and waits for inclusion in a block. During this waiting period, other transactions may execute and change pool states.

**Step 5: On-Chain Validation.** When the transaction is processed by the Solana runtime, the swap instruction executes. At the final step of the swap, the contract compares the actual output amount against the embedded minimum threshold. If actual output is greater than or equal to the threshold, the swap succeeds. If actual output is below the threshold, the instruction returns an error and the entire transaction reverts.

**Step 6: User Receives Feedback.** If the transaction succeeds, the user receives at least the minimum output. If it fails due to slippage, the user receives an error message indicating that the price moved too far. The user can then retry with a higher slippage tolerance or wait for market conditions to stabilize. No tokens changed hands in the failed case.

## Real-life Analogy

Imagine you are buying a house. The seller lists it for $500,000. You make an offer, but the seller says there are other buyers and the price might change before your offer is reviewed. You want the house, but you refuse to pay more than $510,000 no matter what. You write this limit into your signed purchase contract: if the seller tries to raise the price above $510,000, the contract is automatically void and your deposit is returned. Slippage protection is exactly this limit order behavior. You agree to a trade, but only within a predefined price boundary. If the market moves against you beyond that boundary, the deal is off.

## Tiny Numeric Example With Actual Jupiter Quote Response

Suppose you want to swap 50 SOL for USDC with 0.5% slippage tolerance. You call Jupiter:

```
GET https://quote-api.jup.ag/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=50000000000&slippageBps=50
```

Response:

```json
{
  "inputMint": "So11111111111111111111111111111111111111112",
  "inAmount": "50000000000",
  "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "outAmount": "714178000000",
  "otherAmountThreshold": "710807110000",
  "swapMode": "ExactIn",
  "slippageBps": 50,
  "platformFee": null,
  "priceImpactPct": "0.0156",
  "routePlan": [
    {
      "swapInfo": {
        "ammKey": "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYo2Y",
        "label": "Orca",
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "inAmount": "50000000000",
        "outAmount": "714178000000",
        "feeAmount": "12500000",
        "feeMint": "So11111111111111111111111111111111111111112"
      },
      "percent": 100
    }
  ],
  "contextSlot": 245678923,
  "timeTaken": 0.003421
}
```

**Interpretation:**
- Input: 50,000,000,000 lamports = 50 SOL.
- Expected output: 714,178,000,000 base units = 714,178 USDC.
- Minimum output (slippage floor): 710,807.11 USDC.
- Slippage calculation: 714,178 - (714,178 * 0.005) = 710,607.11. The API rounds conservatively.
- If the pool shifts and the actual output drops to 709,000 USDC, the transaction fails and reverts. The user loses only the transaction fee, not their SOL.

## Common Confusion (6 Bullets With "No.")

- **Does slippage protection mean the user always gets exactly the quoted amount?** No. Slippage protection only guarantees a minimum floor. The user may receive more than the quote if prices improve, and they may receive less than the quote but still above the floor. Only amounts below the floor are rejected.

- **Is a higher slippage tolerance always better?** No. A higher tolerance increases the chance of transaction success but also increases the risk of receiving a significantly worse price. In volatile markets, a 5% tolerance might allow a sandwich attacker to extract value from the trade. The optimal tolerance balances execution certainty against price risk.

- **Does slippage protection prevent all forms of price manipulation?** No. Slippage protection specifically prevents the executed price from falling below a threshold. It does not prevent front-running, sandwich attacks, or other MEV strategies that might still occur within the tolerated range. Additional protections like priority fees and private mempool routing are needed for full MEV defense.

- **Is slippage the same as the price impact displayed in the quote?** No. Price impact is the estimated change in pool price caused by the user's own trade. Slippage is the maximum acceptable deviation from the quoted output due to external market movement. Price impact is deterministic based on the trade size. Slippage is probabilistic based on market conditions.

- **If a transaction fails due to slippage, does the user lose their tokens?** No. Because Solana transactions are atomic, a failed swap instruction causes the entire transaction to revert. No token transfers occur. The user retains their original input tokens. They only lose the small transaction fee paid to validators.

- **Can slippage protection be bypassed by a malicious smart contract?** No. The minimum output is embedded in the signed transaction data. A malicious contract cannot alter a signed transaction without breaking the cryptographic signature. The Solana runtime verifies signatures before executing instructions, making post-signing modification impossible.

## Key Properties (5)

1. **Immutable Floor.** Once a transaction is signed, the minimum output is cryptographically locked. This immutability is what makes slippage protection trustworthy. Users can verify the floor directly in the transaction data before signing.

2. **User-Defined Risk Bound.** The slippage tolerance is chosen by the user, not imposed by the protocol. This gives users control over their risk-reward tradeoff. Conservative traders use low tolerances. Urgent traders accept higher tolerances for faster execution.

3. **Atomic Reversion.** Failed slippage checks trigger a full transaction revert. This is a fundamental property of Solana's transaction model. Users are never left in a partial state where some swaps succeeded and others failed.

4. **Basis Point Precision.** Slippage is configured in basis points (hundredths of a percent) rather than whole percentages. This fine-grained control allows precise calibration. A 0.25% tolerance (25 bps) is common for stablecoin swaps where price stability is high.

5. **Composability With Other Protections.** Slippage protection works alongside priority fees, deadline parameters, and MEV-resistant routing. It is one layer in a defense-in-depth strategy. No single protection is sufficient, but together they create a robust safety net for on-chain trading.

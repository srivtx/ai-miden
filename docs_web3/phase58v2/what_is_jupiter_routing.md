# What Is Jupiter Routing

## The Problem

Users want to pay in any token. A launchpad should not force every buyer to hold USDC. Someone might have SOL, BONK, or RAY in their wallet and still want to participate in a token sale. Without a routing engine, the project team would need to manually list every payment token and maintain liquidity pairs for each one. Jupiter solves this by automatically finding the best swap route from any input token to the target payment token.

## Definition

Jupiter Routing is a Solana liquidity aggregation protocol that finds the optimal path for swapping one token to another across all decentralized exchanges (DEXes) and automated market makers (AMMs) on Solana. It splits orders across multiple pools to minimize slippage and maximize output.

## How It Works (6 Steps)

1. **Get Quote**: The client sends the input mint, output mint, and amount to Jupiter's `/quote` API. Jupiter scans all connected DEX pools to find the best execution path.

2. **Check Slippage**: The quote returns the expected output amount and the price impact. The client defines a maximum slippage tolerance (e.g., 0.5%). If price impact exceeds tolerance, the transaction is rejected before submission.

3. **Build Transaction**: The client sends the quote response to Jupiter's `/swap` API. Jupiter constructs a Solana transaction containing all necessary swap instructions across Raydium, Orca, or other DEX pools.

4. **Sign**: The wallet signs the constructed transaction. The signers include the user's wallet and potentially a fee payer if the project covers transaction costs.

5. **Submit**: The signed transaction is sent to a Solana RPC node. The node validates the transaction and forwards it to the leader for inclusion in a block.

6. **Confirm**: The client polls for confirmation or uses a WebSocket subscription. Once the transaction is finalized, the output tokens are in the user's or project's token account.

## Real-Life Analogy

Imagine you want to buy a house in a foreign country. The seller only accepts Euros, but you hold Japanese Yen. Instead of manually finding a bank that does Yen-to-Euro conversion, you use a global currency aggregator. It finds the best rate by routing your Yen through USD and then to Euros, possibly splitting the order across multiple exchanges to get the best price. Jupiter does exactly this for tokens on Solana.

## Tiny Numeric Example With Actual Jupiter API Response

Suppose a user wants to pay 1,000 USDC for a project token, but they only hold SOL. Jupiter quote request:

```
GET https://quote-api.jup.ag/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=5000000000&slippageBps=50
```

Response:

```json
{
  "inputMint": "So11111111111111111111111111111111111111112",
  "inAmount": "5000000000",
  "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "outAmount": "987654321",
  "otherAmountThreshold": "982212304",
  "swapMode": "ExactIn",
  "slippageBps": 50,
  "platformFee": null,
  "priceImpactPct": "0.0023",
  "routePlan": [
    {
      "swapInfo": {
        "ammKey": "58oQ7x7t7...",
        "label": "Raydium",
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "inAmount": "5000000000",
        "outAmount": "987654321",
        "feeAmount": "1250000",
        "feeMint": "So11111111111111111111111111111111111111112"
      },
      "percent": 100
    }
  ],
  "contextSlot": 234567890,
  "timeTaken": 0.0234
}
```

The user pays 5 SOL and receives approximately 987.65 USDC after routing through Raydium. The price impact is 0.23%, well within the 0.5% slippage tolerance.

## Common Confusion

- Does Jupiter hold my tokens during the swap? No. Jupiter is a routing engine. It builds instructions that execute atomically on-chain. Your tokens never leave your wallet until the swap executes.

- Is Jupiter a DEX itself? No. Jupiter aggregates liquidity from existing DEXes like Raydium, Orca, and Meteora. It does not maintain its own liquidity pools.

- Do I need to approve Jupiter to spend my tokens? No. Solana uses an account-based model with associated token accounts. You sign a transaction that includes a delegate or direct transfer instruction.

- Will Jupiter always use a single route? No. Jupiter may split your order across multiple DEXes and pools if that yields a better output amount.

- Does Jupiter guarantee the quoted amount? No. Slippage tolerance protects you, but if market conditions change between quoting and execution, you may receive the minimum threshold amount or the transaction fails.

- Is Jupiter free to use? No. While Jupiter does not charge protocol fees, the underlying DEXes charge trading fees, and Solana charges transaction fees.

## Key Properties

1. **Atomic Execution**: The entire swap either succeeds or fails. There is no partial execution state.

2. **Best Price Discovery**: Jupiter compares routes across all major Solana DEXes to find the optimal output.

3. **Composable**: Jupiter swaps can be composed with other instructions in a single transaction, such as a launchpad participation instruction.

4. **Permissionless**: Anyone can query the Jupiter API and build swap transactions without authentication or KYC.

5. **Low Latency**: Quote responses are typically returned in under 50 milliseconds, enabling real-time user interfaces.

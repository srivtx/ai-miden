# Phase 60 Architecture: Integrating Jupiter From Scratch

This document provides a step-by-step guide to integrating the Jupiter liquidity aggregator into a Solana application from an empty directory to a fully functional quoting and swapping system. Each step explains not only what to build, but why the component exists and how it fits into the larger system.

---

## Step 1: Get Jupiter API Key

### What to Build

Visit the Jupiter developer portal and obtain an API key for production use. For devnet and low-volume testing, Jupiter's public API endpoints do not require authentication, but production applications should use a dedicated key for rate limit increases and stability guarantees. Store the API key in an environment variable named `JUPITER_API_KEY`. Create a `.env` file in the project root and add the key there. Load the environment variable at runtime using a library such as `dotenv` or by exporting it in the shell before starting the application.

### Why This Step Matters

The Jupiter API is a hosted service with rate limits. Without an API key, your application shares the public rate limit pool with all other unauthenticated users. During high-traffic periods, this can lead to rejected requests and failed swaps. An API key assigns your application a dedicated quota and gives the Jupiter team visibility into your usage patterns, which enables them to provide support and prevent abuse.

Storing the key in an environment variable rather than hardcoding it in source code is a security best practice. API keys are secrets. If you commit a key to version control, it becomes visible to anyone with repository access and may be scraped by automated bots. Environment variables keep secrets out of code. They also allow different keys for different environments: a development key for local testing, a staging key for pre-production, and a production key for live traffic.

### Key Design Decision

Use a `.env` file for local development and inject the key through your deployment platform's secret management system for production. Never log the API key, even in debug output. If the key is accidentally exposed, rotate it immediately through the Jupiter developer portal.

---

## Step 2: Fetch Quote for Swap

### What to Build

Implement a function that makes an HTTP GET request to `https://quote-api.jup.ag/v6/quote`. The function should accept parameters for `inputMint`, `outputMint`, `amount`, and `slippageBps`. Construct the query string by URL-encoding these parameters. Use a robust HTTP client such as `axios` or the native `fetch` API. Parse the JSON response into a typed object. Validate that the response contains the expected fields: `inputMint`, `outputMint`, `outAmount`, `otherAmountThreshold`, `priceImpactPct`, and `routePlan`. Return the parsed quote object to the caller.

### Why This Step Matters

The quote endpoint is the entry point to Jupiter's routing engine. It is where off-chain optimization happens. By fetching a quote before building a transaction, your application knows exactly how many output tokens the user can expect, what the price impact will be, and which pools will be used. This transparency is essential for user trust. No one will sign a transaction blind.

The quote is also a safety checkpoint. If the quote shows an unexpectedly low output or an extremely high price impact, your application can warn the user before they commit to the swap. This prevents accidental losses from trading illiquid pairs or accepting terrible rates.

### Key Design Decision

Always validate the quote response structure before using it. Jupiter's API is stable but not static. New fields may be added, and edge cases may return partial responses. Validation ensures that your application fails gracefully with a clear error message rather than crashing with an undefined property access.

---

## Step 3: Build Swap Transaction

### What to Build

Implement a function that accepts a quote response object and a user public key. Make an HTTP POST request to `https://quote-api.jup.ag/v6/swap` with a JSON body containing `quoteResponse` and `userPublicKey`. Parse the JSON response to extract the `swapTransaction` field, which contains a base64-encoded serialized transaction. Decode the base64 string into a buffer. Deserialize the buffer into a Solana `VersionedTransaction` or `Transaction` object using `@solana/web3.js`. Return the deserialized transaction to the caller.

### Why This Step Matters

Jupiter does not return raw instructions for you to assemble manually. Instead, it returns a fully serialized transaction. This is a deliberate design choice. The transaction contains complex routing logic, intermediate token account management, and safety checks that would be extremely error-prone to reconstruct client-side. By receiving a pre-built transaction, your application benefits from Jupiter's expertise and avoids bugs in instruction ordering or account derivation.

The `userPublicKey` parameter is critical because Jupiter needs to know which wallet will sign the transaction. This allows Jupiter to derive the correct associated token accounts for the user and to set the fee payer. Without the correct public key, the transaction would reference the wrong accounts and fail on-chain.

### Key Design Decision

Do not attempt to modify the instructions inside the serialized transaction. Jupiter's transaction is carefully constructed to maintain atomicity and correctness. Manual modification risks breaking the route logic or invalidating the slippage protection. If you need to add instructions, append them before or after the Jupiter instructions within the same transaction, or use address lookup tables appropriately.

---

## Step 4: Add Priority Fees

### What to Build

After receiving the serialized swap transaction from Jupiter, add a priority fee instruction before signing. Use `@solana/web3.js` to create a `ComputeBudgetProgram.setComputeUnitPrice` instruction with a micro-lamport price per compute unit. Choose a fee level based on network congestion: a low fee for normal conditions, a medium fee for moderate congestion, and a high fee for urgent execution. Append this instruction to the transaction's instruction list. If the transaction is a `VersionedTransaction`, create a new message with the priority fee instruction included and rebuild the transaction.

### Why This Step Matters

Solana uses a priority fee mechanism to allow transactions to compete for inclusion during high congestion. Without a priority fee, your swap transaction may sit in the queue for seconds or even minutes. In volatile markets, this delay can cause the quoted price to expire and the swap to fail. A priority fee increases the probability that your transaction lands in the next block, reducing slippage risk and improving user experience.

The priority fee is paid in addition to the base transaction fee, but the amount is typically small. The value of a successful swap landing quickly far exceeds the cost of a few thousand micro-lamports. For time-sensitive trades, such as arbitrage or liquidations, priority fees are not optional; they are essential.

### Key Design Decision

Make the priority fee configurable rather than hardcoded. Network conditions change constantly. A fee that works today may be inadequate tomorrow. Allow users or administrators to set the fee level through an environment variable or API parameter. Log the chosen fee level so that you can analyze the correlation between fee and confirmation time.

---

## Step 5: Sign and Submit

### What to Build

Load the user's private key from a secure source, such as an environment variable for testing or a hardware wallet for production. Sign the transaction using the keypair. Connect to the Solana devnet cluster using a reliable RPC endpoint. Submit the signed transaction with `sendAndConfirmTransaction` or `sendTransaction` followed by polling for confirmation. If using `sendTransaction`, implement a confirmation loop that retries with exponential backoff until the transaction is confirmed or a timeout is reached. Log the transaction signature for debugging and audit purposes.

### Why This Step Matters

Signing is the cryptographic act of authorization. It proves that the owner of the wallet consents to the transaction. Without a valid signature, the Solana runtime will reject the transaction immediately. The security of the signing process is paramount. In production, private keys must never touch application memory if possible. Use wallet adapters, hardware wallets, or key management services.

Submission is where the transaction enters the network. A single RPC call may fail due to network issues, rate limiting, or validator overload. Implementing retry logic with exponential backoff makes your integration resilient. Without it, a transient network blip would cause a swap failure and a poor user experience.

### Key Design Decision

Use `sendAndConfirmTransaction` for simplicity in scripts, but use `sendTransaction` with custom polling in production APIs. The built-in confirmation logic may not handle all edge cases, such as transaction preflight failures or blockhash expiration. Custom polling gives you full control over timeouts, retries, and error handling.

---

## Step 6: Confirm and Handle Errors

### What to Build

Implement comprehensive error handling for the entire swap flow. Handle HTTP errors from the Jupiter API, including 429 (rate limit), 400 (bad request), and 500 (server error). Handle Solana RPC errors, including blockhash not found, simulation failures, and confirmation timeouts. Handle on-chain program errors, including slippage exceeded, insufficient liquidity, and invalid route. For each error category, return a clear, actionable error message to the user or client. Log the full error details, including the transaction signature, the quote response, and the RPC endpoint, for debugging.

### Why This Step Matters

Error handling is where good integrations separate themselves from broken ones. Users will encounter errors. The question is whether your application helps them recover or leaves them confused. A generic "transaction failed" message is useless. A message like "Slippage exceeded: the price moved 2.1% but your tolerance was 0.5%. Try again with 1.0% slippage or wait for volatility to decrease" empowers the user to take action.

Logging is equally important. When a swap fails in production, you need enough context to diagnose the issue. Was it a Jupiter API problem? Was it a network congestion problem? Was it a user error? Without detailed logs, you are guessing. With detailed logs, you can fix the root cause.

### Key Design Decision

Structure your error handling as a pipeline. Each stage of the swap flow has its own error type. If an error occurs, the pipeline short-circuits and returns the error immediately. This prevents cascading failures and makes debugging easier. Use typed errors rather than strings so that downstream code can programmatically decide how to respond.

---

## Integration Checklist

After completing all six steps, verify that the system behaves as a cohesive whole:

1. A user can request a quote for any supported token pair and receive a valid route plan.
2. The quote includes a slippage floor that protects the user from adverse price movement.
3. The swap transaction is built by Jupiter and returned as a serialized base64 string.
4. A priority fee is added to the transaction to improve confirmation speed.
5. The transaction is signed by the user's keypair and submitted to devnet.
6. Successful swaps return the transaction signature and the actual output amount.
7. Failed swaps return clear error messages with actionable guidance.
8. All API calls and transactions are logged for audit and debugging.

This architecture produces a robust Jupiter integration that fetches optimal prices, protects users from slippage, and executes reliably on Solana.

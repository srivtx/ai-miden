# Phase 61 Architecture: Production Infrastructure

This document maps the exact steps to take a Solana application from devnet demo to mainnet production, with the reasoning behind each step.

---

## Step 1: Set up Helius RPC

**What to do:**
Create a Helius account at https://helius.xyz, generate an API key, and replace your default RPC URL (`https://api.mainnet-beta.solana.com`) with `https://mainnet.helius-rpc.com/?api-key=YOUR_KEY`.

**Why:**
The default public RPC is rate-limited to roughly 100 requests per 10 seconds, has no archival data, drops connections under load, and provides no debugging information. Helius provides staked nodes with higher network priority, enhanced APIs, and observability. Without this step, your production app will timeout during high-traffic events.

**Implementation notes:**
- Store the API key in an environment variable, never commit it.
- Use the same URL for both HTTP RPC and webhook configuration.
- Test failover by temporarily blocking the URL in your firewall to ensure graceful degradation.

---

## Step 2: Implement priority fee calculation

**What to do:**
Before every transaction submission, call the Helius `getPriorityFeeEstimate` endpoint. Parse the returned fee levels (min, low, medium, high, veryHigh) and select one based on your use case. Add a `ComputeBudgetProgram.setComputeUnitPrice` instruction to your transaction with the selected value.

**Why:**
Without a priority fee, your transaction competes on equal footing with every other base-fee transaction. During congestion, leaders prioritize transactions by total fee. If you are running a time-sensitive operation (swap, mint, liquidation), missing the block window costs more than the priority fee itself. Dynamic estimation prevents overpaying in quiet periods and underpaying during spikes.

**Implementation notes:**
- Cache fee estimates for 5-10 seconds to avoid excessive RPC calls.
- Log the selected fee level and actual landing slot for post-hoc analysis.
- Set a maximum fee cap to prevent runaway costs during extreme congestion.

---

## Step 3: Create Address Lookup Table

**What to do:**
Identify the set of accounts your application repeatedly references in transactions. Use `AddressLookupTableProgram.createLookupTable` to allocate a lookup table account, then use `AddressLookupTableProgram.extendLookupTable` to populate it with those addresses. Store the resulting table address in your application configuration.

**Why:**
Complex DeFi transactions reference 20-40 accounts. A legacy transaction cannot fit more than roughly 25-30 account addresses within the 1,232-byte limit. Without LUTs, you must split operations into multiple transactions, which introduces atomicity risk and poor UX. LUTs compress 32-byte addresses into 1-byte indices, enabling up to 64 accounts in a single versioned transaction.

**Implementation notes:**
- Create separate LUTs for different transaction types (e.g., swaps vs. staking) to keep tables small and relevant.
- Extend tables in batches of 30 addresses to stay within transaction size limits.
- Record the creation slot; tables are not usable until the slot after creation.

---

## Step 4: Build versioned transaction

**What to do:**
Instead of `Transaction`, use `VersionedTransaction`. Compile your instructions with `MessageV0.compile`, passing your LUT addresses in the `addressLookupTableAccounts` parameter. Sign the compiled message with the required signers.

**Why:**
Legacy `Transaction` does not support lookup tables. `VersionedTransaction` with `MessageV0` is the only format that can reference LUTs. This is the transaction format the Solana runtime expects when you want to leverage address compression. Using legacy transactions after creating LUTs is a common integration bug that wastes the setup work.

**Implementation notes:**
- Ensure all accounts referenced via LUT are actually present in the table; missing entries cause simulation failures.
- Versioned transactions still require the fee payer signature and any program-required signatures.
- The transaction structure is different from legacy; do not mix `Transaction.add()` with `VersionedTransaction`.

---

## Step 5: Simulate before sending

**What to do:**
Call `connection.simulateTransaction(versionedTx)` before `connection.sendTransaction`. Inspect the `value.err` and `value.logs` fields. Only proceed to send if simulation returns no error.

**Why:**
Failed transactions on mainnet still cost fees. Simulation is a dry-run executed by the RPC node against the current bank state. It catches program logic errors, missing accounts, instruction data mismatches, and compute budget overruns before you pay. In production, sending without simulation is financial malpractice.

**Implementation notes:**
- Simulation uses the same compute budget as the real transaction; if you set CU limits, include them before simulating.
- Some RPCs (including Helius) support `replaceRecentBlockhash` in simulation to avoid blockhash expiration during high latency.
- Log simulation results for debugging; they contain the exact program error codes.

---

## Step 6: Monitor with webhooks

**What to do:**
Configure a Helius webhook pointing to your HTTPS endpoint. Subscribe to account changes, transaction events, or NFT events relevant to your application. Implement an Express route at the webhook URL to receive and process the JSON payloads.

**Why:**
Polling `getSignatureStatuses` or `getAccountInfo` in a loop wastes RPC quota and introduces latency. Webhooks push events to you in real time, within seconds of confirmation. For production applications tracking user deposits, order fills, or liquidation events, polling is too slow and too expensive. Webhooks also provide a complete transaction context that you would otherwise need multiple RPC calls to reconstruct.

**Implementation notes:**
- Verify webhook authenticity using the Helius webhook signature header.
- Respond with HTTP 200 immediately to avoid retries; process the payload asynchronously.
- Store webhook payloads in a queue (Redis, SQS) if your processing logic is slower than the delivery rate.
- Handle duplicate deliveries gracefully by tracking processed signatures.

---

## Integration Flow

```
[User Request]
     |
     v
[Helius RPC] --(1)--> [Get Priority Fee Estimate]
     |
     v
[Create/Load LUT] --(2)--> [Compress Addresses]
     |
     v
[Build Versioned Tx] --(3)--> [Add Priority Fee + LUT refs]
     |
     v
[Simulate Tx] --(4)--> [Check for errors]
     |
     v
[Send Tx] --(5)--> [Monitor via Webhook]
     |
     v
[Update UI / Database]
```

This architecture separates a devnet demo from a mainnet production application by addressing reliability, cost control, and observability.

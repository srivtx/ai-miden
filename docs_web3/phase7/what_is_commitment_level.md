## What Is a Commitment Level?

**The Problem:**
When you query the blockchain or submit a transaction, how do you know the data is final?
A validator could show you a block that later gets discarded.
You need a way to specify how much finality you require before trusting the response.
Different use cases need different guarantees.
A game update might accept processed, while a million-dollar settlement demands finalized.

**Definition:**
A **commitment level** is a setting that tells the RPC node how finalized a block must be before returning data.
Solana provides three commitment levels: processed, confirmed, and finalized.
Higher commitment means stronger guarantees but slightly higher latency.

**Commitment levels:**
- **Processed** — The transaction or block has been processed by the current node.
  No cluster consensus yet. Fastest but least certain.
- **Confirmed** — The block has been voted on by a superminority of the cluster.
  Very unlikely to be rolled back. Good balance of speed and certainty.
- **Finalized** — The block has reached maximum cluster lockout.
  Theoretically impossible to roll back. Slowest but most certain.

**Real-life analogy:**
A commitment level is like the stages of confirming a hotel reservation.
"Processed" is when the front desk clerk says "I wrote it in my notebook."
The reservation exists on one clerk's desk, but if the power goes out, it might be lost.
"Confirmed" is when the clerk enters it into the hotel's central system and the manager acknowledges it.
It is very unlikely to disappear, but a rare system glitch could still erase it.
"Finalized" is when you receive a written confirmation letter with a stamp.
The hotel, the chain headquarters, and your credit card company all have a permanent record.
It is effectively irreversible.
Most travelers are happy with "Confirmed."
Only large corporate events demand "Finalized."

**Tiny numeric example:**
```
Scenario: You send 1 SOL to Bob and want to check his balance.

| Commitment | Latency | Guarantee | When to use |
|------------|---------|-----------|-------------|
| processed  | ~400ms  | Node saw it | Real-time UI updates |
| confirmed  | ~5-10s  | Superminority voted | Standard transfers |
| finalized  | ~12-15s | Maximum lockout | Large settlements |

At slot 123,456,789:
  - processed balance: 6 SOL (includes your transfer)
  - confirmed balance: 5.5 SOL (transfer in a confirmed block)
  - finalized balance: 5 SOL (transfer not yet finalized)

As time passes, all three converge to 6 SOL.
```

**Common confusion:**
- **"Processed means the transaction is done."**
  No. Processed means the local node has seen it, but the cluster may not have agreed yet.
  The block could still be forked away.
- **"Confirmed is always safe enough."**
  For almost all applications, yes.
  But for extremely high-value settlements, use finalized.
- **"Finalized is instant."**
  No. Finalized takes approximately 12 to 15 seconds on Solana mainnet under normal conditions.
- **"I can skip specifying commitment."**
  Most client libraries default to finalized, which is slower.
  For better performance, explicitly choose the right level.
- **"Commitment levels affect transaction submission."**
  They affect how the node waits for confirmation after submission.
  The transaction itself is broadcast immediately regardless of commitment.
- **"Different RPC nodes show different confirmed states."**
  They should not. Confirmed means a superminority of the cluster has voted.
  Honest nodes should agree.
- **"Commitment only applies to reads."**
  No. It also applies to sendTransaction.
  The node will wait until the specified commitment level is reached before returning.
- **"Processed is useless."**
  Not at all. It is perfect for real-time UI updates where you want instant feedback and can tolerate rare rollbacks.
- **"I should always use finalized to be safe."**
  That makes your app unnecessarily slow.
  Use the lowest commitment that meets your risk tolerance.

**Where it appears in our code:**
`src_web3/phase7/rpc_client_demo.rs` — Uses CommitmentConfig::confirmed() when constructing the RPC client to balance speed and certainty.
`src_web3/phase7/block_explorer_api.ts` — Express API allows clients to specify a commitment level as a query parameter for every endpoint.

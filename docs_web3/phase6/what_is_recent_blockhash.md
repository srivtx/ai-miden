## What Is a Recent Blockhash?

**The Problem:**
Without a time limit, a malicious actor could capture your signed transaction and replay it days later.
How do you prevent old transactions from being executed repeatedly?
You need a mechanism that makes every transaction valid only for a short window of time.
This ensures that signatures cannot be reused indefinitely.
This is critical for security because a stolen or intercepted transaction could otherwise drain a wallet repeatedly.

**Definition:**
A **recent blockhash** is a hash of a recently produced block that you include in your transaction.
It acts as a timestamp and a nonce.
Validators only accept transactions whose blockhash is recent (typically within the last 90 seconds to 2 minutes).
Once the blockhash expires, the transaction becomes invalid and cannot be replayed.
This expiration mechanism is a core part of Solana's replay protection strategy.

**How it works:**
1. You fetch the latest blockhash from an RPC node before building your transaction
2. You embed the blockhash in the transaction message
3. You sign the entire message, which includes the blockhash
4. Validators check that the blockhash is recent before processing
5. After expiration, the same signature cannot be reused

**Real-life analogy:**
A recent blockhash is like a dated coupon at a grocery store.
The coupon says "Valid until May 4, 2026."
The cashier (validator) checks the date before accepting it.
If you try to use the same coupon next year, it is rejected.
The date is not just printed on the coupon — it is part of the coupon's design.
Trying to change the date would invalidate the signature.
Similarly, the blockhash is baked into the transaction, and changing it would break the cryptographic signature.
The coupon is only good for one use during the valid window.
Once expired, it becomes a worthless piece of paper.

**Tiny numeric example:**
```
Blockhash lifecycle:
  - Slot 123,456,789 is produced at 12:00:00 UTC
  - Its hash is: 5Km7vG8aB2cD3eF4...
  - You fetch this blockhash at 12:00:15 UTC
  - You build and sign your transaction by 12:00:20 UTC
  - Validators accept it until ~12:02:00 UTC (90-150 second window)
  - At 12:03:00 UTC, the blockhash is too old; the transaction is rejected
```

If the transaction fails for another reason (e.g., insufficient funds), you CANNOT simply resubmit it.
You must fetch a NEW blockhash and re-sign.

| Step | Time | Action |
|------|------|--------|
| 1 | 12:00:00 | Block produced, hash H1 generated |
| 2 | 12:00:15 | Client fetches H1 |
| 3 | 12:00:20 | Transaction signed with H1 |
| 4 | 12:00:25 | Transaction submitted and processed |
| 5 | 12:03:00 | H1 expired; resubmission rejected |

**Common confusion:**
- **"A blockhash is a block number."**
  No. A blockhash is a cryptographic hash of the block contents.
  The slot number is the sequential block number.
- **"I can reuse a blockhash forever."**
  No. Blockhashes expire after approximately 90 to 150 slots (about 90 seconds).
  After that, validators reject transactions using that blockhash.
- **"If my transaction fails, I can just send it again."**
  No. If the failure occurs after the blockhash expires, you must fetch a new blockhash and create a new signature.
  The old signed bytes are dead.
- **"Blockhashes prevent all replay attacks."**
  They prevent replay after expiration, but within the validity window, a transaction could theoretically be replayed if it is not yet confirmed.
- **"I should cache blockhashes for performance."**
  Only for a few seconds.
  Caching a blockhash for too long causes transaction rejection when you finally submit.
- **"Multiple transactions can share the same blockhash."**
  Yes. A blockhash is valid for many transactions during its window.
  It is not a unique nonce per transaction.
- **"Blockhashes are guaranteed to be unique."**
  They are unique per block, but blocks are produced every 400ms, so new blockhashes appear rapidly.
- **"Blockhashes are only used for transfers."**
  No. Every transaction on Solana, including program invocations and account creations, requires a recent blockhash.
- **"I can omit the blockhash if I am in a hurry."**
  No. A transaction without a valid recent blockhash is rejected immediately by the runtime.

**Where it appears in our code:**
`src_web3/phase6/first_transaction.rs` — Fetches get_latest_blockhash() and embeds it in the transaction before signing.
`src_web3/phase6/transaction_api.ts` — Express API fetches a fresh blockhash for every transaction request to ensure validity.

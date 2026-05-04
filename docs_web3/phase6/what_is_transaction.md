## What Is a Transaction?

**The Problem:**
You want to move SOL from your wallet to someone else's.
How do you construct a message that the blockchain understands, sign it to prove ownership, and submit it for processing?
Without a transaction, your intent to transfer value has no formal representation that validators can execute.
Every action on Solana must be wrapped in a transaction.
The blockchain does not understand intentions; it only understands signed, structured messages that follow a strict protocol.
This is why learning to build and send transactions is the foundational skill of Solana development.

**Definition:**
A **transaction** on Solana is a signed message containing one or more instructions, a list of accounts, a recent blockhash, and signatures from authorized signers.
It is the atomic unit of work on the blockchain.
All instructions inside a transaction either succeed together or fail together.
No partial state changes are ever committed.
This atomicity is a fundamental guarantee that makes blockchain state predictable and secure.
When you submit a transaction, you are asking the entire validator network to agree on a specific set of state changes.

**Anatomy of a transaction:**
- **Instructions** — What to do (transfer, create account, call program)
- **Accounts** — Which accounts are involved and how they are accessed
- **Recent blockhash** — A timestamp-like value preventing replay attacks
- **Signers** — Cryptographic signatures proving authorization
- **Fee Payer** — The account that pays the transaction fee

**Real-life analogy:**
A Solana transaction is like a multi-part legal document that multiple parties sign in front of a notary.
The instructions are the clauses inside the document: "Transfer 5 SOL to Bob" and "Record a memo."
The accounts are the parties involved — Alice, Bob, and the bank.
The recent blockhash is the date stamp that prevents someone from photocopying and reusing an old document next month.
The signatures are the notarized signatures of the parties.
A single transaction can contain multiple instructions, like a contract with multiple clauses.
All clauses execute atomically — either all succeed or all fail.
If Alice has 3 SOL but tries to transfer 5, the entire document is voided.
The memo is NOT logged, and no partial state changes persist.
The notary (validator) checks every signature and every clause before approving the document.
Once approved, the document is filed permanently in the public record where anyone can inspect it.
This ensures transparency and prevents any party from later claiming the document said something different.

**Tiny numeric example:**
```
Transaction:
  - Recent Blockhash: 5Km7... (from slot 123,456,789)
  - Signatures: [Alice's signature, Bob's signature]
  - Fee Payer: Alice
  - Instructions:
    1. Transfer 5 SOL from Alice to Bob
       - Program: System Program (11111111111111111111111111111111)
       - Accounts: [Alice (signer, writable), Bob (writable)]
       - Data: 5,000,000,000 lamports
    2. Log a memo
       - Program: Memo Program
       - Accounts: [Alice (signer)]
       - Data: "Payment for coffee"
  - Fee: ~0.000005 SOL (5,000 lamports)
```

If Alice has 3 SOL, instruction 1 fails due to insufficient funds.
Because transactions are atomic, instruction 2 also fails.
The memo is NOT logged.
No state changes persist.
This protects Bob from receiving an inconsistent state where the memo exists but the payment does not.

| Component | Size Limit | Purpose |
|-----------|-----------|---------|
| Signatures | Up to 12 | Prove authorization for mutating accounts |
| Accounts | Up to 64 | Tell the runtime which accounts are involved |
| Instructions | Limited by size | The actual operations to execute |
| Total size | 1232 bytes | Hard limit for network packet size |

**Common confusion:**
- **"A transaction is an instruction."**
  No. A transaction is a container that holds one or more instructions.
  Multiple instructions can be batched into a single transaction to execute atomically.
- **"Transactions are instant."**
  They are fast (400-600ms on Solana) but not instant.
  They must be processed by a leader validator, voted on by the cluster, and confirmed.
- **"Transaction fees are high."**
  On Solana, fees are ~0.000005 SOL ($0.0001).
  This is approximately 100,000 times cheaper than Ethereum mainnet fees.
- **"Failed transactions still cost fees."**
  Yes. Even if a transaction fails, it consumed computation resources and network bandwidth, so the fee is still charged.
- **"I can send a transaction without signing."**
  No. Any instruction that modifies an account requires the account owner's signature.
  Unsigned transactions are rejected immediately.
- **"Transactions can have unlimited instructions."**
  No. The transaction size is limited to 1232 bytes, which constrains the number of accounts, instructions, and signatures you can include.
- **"A transaction can partially succeed."**
  No. Transactions are atomic.
  Either every instruction succeeds and state changes are committed, or the entire transaction fails and no state changes occur.
- **"The fee payer must be a signer."**
  Yes. The fee payer signs to prove they authorize the deduction of lamports for network fees.
- **"Transactions are encrypted."**
  No. Transactions are signed but not encrypted.
  Anyone can inspect the instructions, accounts, and data on the blockchain.
- **"I can reuse a transaction signature."**
  No. Each signature is unique to the specific message, blockhash, and signer combination.

**Where it appears in our code:**
`src_web3/phase6/first_transaction.rs` — Constructs, signs, and sends a transfer transaction on devnet.
`src_web3/phase6/transaction_api.ts` — Express API endpoint that creates, signs, sends, and monitors transactions.

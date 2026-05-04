## What Is an RPC Node?

**The Problem:**
The blockchain stores every account balance, every transaction, and every program in a distributed ledger.
Your application cannot read this data directly from the network because it does not participate in consensus.
How do you ask questions like "What is Alice's balance?" or "What happened in transaction XYZ?"
You need a bridge between your application and the blockchain state that is fast, reliable, and easy to query.
Without this bridge, your app would be blind to everything happening on-chain.

**Definition:**
An **RPC (Remote Procedure Call) node** is a server that runs the blockchain validator software and exposes an HTTP API for clients to query on-chain data and submit transactions.
It is the primary interface between developers and the Solana network.
RPC nodes answer questions about state and forward write requests to the network.
They do not participate in consensus unless they are also validators.

**What an RPC node does:**
- Reads account balances, data, and metadata
- Returns transaction history and block contents
- Submits signed transactions to the network
- Provides cluster information such as slot, epoch, and supply
- Simulates transactions before they are sent

**Real-life analogy:**
An RPC node is like a librarian at a massive library where every book ever written represents a transaction or account state.
The library has billions of books organized across countless shelves.
You cannot enter the stacks yourself because you do not know the filing system.
Instead, you ask the librarian specific questions: "What is the balance of account ABC?"
The librarian looks up the card catalog and returns the answer.
"Show me the receipt for transaction XYZ."
The librarian retrieves the exact page.
"What is the current time?"
The librarian checks the clock.
The librarian (RPC node) knows the entire library and can answer questions in milliseconds because they have already indexed the data.

**Tiny numeric example:**
```rust
let client = RpcClient::new("https://api.devnet.solana.com");

// Question 1: What is Alice's balance?
let balance = client.get_balance(&alice_pubkey)?;
// Answer: 5_000_000_000 lamports (5 SOL)

// Question 2: What is the latest block?
let slot = client.get_slot()?;
// Answer: 123_456_789

// Question 3: What happened in this transaction?
let tx = client.get_transaction(&signature, UiTransactionEncoding::Json)?;
// Answer: Full transaction details including instructions, accounts, and logs

// Question 4: How much SOL exists?
let supply = client.get_supply()?;
// Answer: Total, circulating, and non-circulating supply
```

**Common confusion:**
- **"RPC nodes store the blockchain."**
  They do store it, but so do all validators.
  RPC nodes are optimized for querying, not for consensus voting.
- **"I need to run my own RPC node."**
  No. You can use public RPC endpoints like api.devnet.solana.com for free.
  Paid services like QuickNode, Alchemy, or Helius are available for production.
- **"RPC calls are free."**
  Public endpoints are free but rate-limited.
  Paid services charge per request.
  Heavy applications can spend hundreds of dollars per month on RPC.
- **"All RPC nodes are equal."**
  No. Some are faster, some retain more history, and some support additional features like transaction simulation.
- **"RPC calls are instant."**
  They are fast (~100ms) but not instant.
  The node must look up data from disk or memory, serialize it, and send it over the network.
- **"An RPC node can sign transactions for me."**
  No. RPC nodes only submit pre-signed transactions.
  Your private keys never leave your machine.
- **"I only need one RPC endpoint."**
  For production, you should use multiple endpoints or a load balancer to avoid downtime if one provider fails.
- **"RPC nodes validate transactions."**
  They forward transactions to the leader validator, but they do not participate in consensus themselves unless they are also validators.
- **"RPC nodes can censor my transactions."**
  A malicious RPC node could refuse to forward your transaction.
  This is why you should use multiple providers.

**Where it appears in our code:**
`src_web3/phase7/rpc_client_demo.rs` — A Rust client that queries balances, account info, slot, supply, and blockhash from devnet.
`src_web3/phase7/block_explorer_api.ts` — Express API that wraps RPC calls with caching and exposes them as REST endpoints.

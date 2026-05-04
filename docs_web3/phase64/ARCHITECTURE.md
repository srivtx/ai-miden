# Phase 64 Architecture: ZK Compression with Light Protocol

This guide walks through building a compressed token application step by step.

## Step 1: Install Light Protocol SDK

Install the Light Protocol packages and Solana dependencies.

```
npm install @lightprotocol/stateless.js @lightprotocol/compressed-token
npm install @solana/web3.js
npm install -D typescript ts-node @types/node
```

Why: The Light Protocol SDK provides the `Rpc` client for compressed state queries, the `CompressedTokenProgram` for token instructions, and the prover integration for ZK proof generation.

## Step 2: Create Compressed Token Mint

Use `CompressedTokenProgram.createMint` to initialize a new compressed token.

```typescript
import { createRpc } from "@lightprotocol/stateless.js";
import { CompressedTokenProgram } from "@lightprotocol/compressed-token";
import { Keypair } from "@solana/web3.js";

const rpc = createRpc("https://devnet.helius-rpc.com/?api-key=YOUR_API_KEY");
const payer = Keypair.generate();

const { mint } = await CompressedTokenProgram.createMint(
  rpc,
  payer,
  payer.publicKey,
  9
);
```

Why: Creating a compressed mint initializes the Merkle tree that will hold all future token balances for this mint. Without this step, there is no tree to append leaves to.

## Step 3: Mint Compressed Tokens

Mint tokens directly into a recipient's compressed balance.

```typescript
const recipient = new PublicKey("...");
const amount = 1_000_000_000n;

await CompressedTokenProgram.mintTo(
  rpc,
  payer,
  mint,
  recipient,
  payer.publicKey,
  amount
);
```

Why: Standard SPL minting creates an on-chain token account and pays rent. Compressed minting appends a leaf to the shared Merkle tree, costing a fraction of the rent while preserving the same balance semantics.

## Step 4: Transfer with ZK Proof

Fetch a validity proof and submit a compressed transfer.

```typescript
const senderAccounts = await rpc.getCompressedTokenAccountsByOwner(sender);
const proof = await rpc.getValidityProof(senderAccounts.items.map(i => i.hash));

await CompressedTokenProgram.transfer(
  rpc,
  payer,
  mint,
  amount,
  recipient,
  proof
);
```

Why: Transfers must prove the sender owns a valid leaf without loading every leaf on-chain. The ZK proof guarantees the spend is legitimate, and the on-chain verifier updates the root atomically.

## Step 5: Verify On-Chain

Inspect the transaction on a Solana explorer using the signature returned by the transfer.

Why: On-chain verification is the security anchor. Even though proofs are generated off-chain, the Light Protocol verifier program enforces that only valid proofs can update the Merkle root, preventing double-spends and forgeries.

## Step 6: Decompress If Needed

If the token needs to interact with a standard DeFi protocol, decompress it into a normal SPL token account.

```typescript
await CompressedTokenProgram.decompress(
  rpc,
  payer,
  mint,
  amount,
  recipientStandardTokenAccount
);
```

Why: Many existing Solana programs expect standard SPL token accounts. Decompression creates a normal account from a compressed leaf so the token can be deposited into AMMs, lending pools, or staking contracts that have not yet adopted compressed state.

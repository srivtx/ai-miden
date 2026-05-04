# Phase 56v2 Architecture

## Step 1: Design Bridge State with Nonce Tracking

**Why:** Replay attacks are the most common bridge vulnerability after signature forgery. If the bridge does not track unique operation identifiers, an attacker can copy a previous successful proof and submit it again to mint free tokens. A monotonically increasing nonce ensures every lock, mint, burn, and release is unique. The bridge state PDA stores this nonce, the vault bump, the authority, the threshold, and the wrapped mint address. By centralizing configuration in one deterministic account, every instruction can validate itself against a single source of truth.

**Implementation:**
- Define `BridgeState` with fields: `authority`, `original_mint`, `vault_bump`, `state_bump`, `guardian_threshold`, `nonce`, `wrapped_mint`.
- Derive the state PDA from the static seed `b"bridge_state"`.
- Every lock and burn increments `nonce` and uses the pre-increment value as the seed for a record PDA.

## Step 2: Implement Lock with Vault PDA

**Why:** A bridge must hold user deposits in an account it controls but that is also transparent and auditable. A Program Derived Address (PDA) is the standard Solana pattern for this because the program can sign for it via CPI without holding a private key. The vault is a token account whose authority is the bridge state PDA. When a user locks tokens, the program performs an SPL `Transfer` CPI from the user's account into the vault, then writes a `LockRecord` that captures the depositor, amount, and nonce.

**Implementation:**
- Initialize a vault token account with `token::authority = bridge_state` and seeds `b"vault" + bridge_state.key`.
- In `lock_tokens`, invoke `token::transfer` to move original tokens into the vault.
- Create a `LockRecord` PDA seeded by the current nonce to create an immutable receipt of the deposit.

## Step 3: Add Ed25519 Signature Verification (REAL, Not Stubbed)

**Why:** The entire security model collapses if the on-chain verifier accepts fake signatures. Phase 56 used `assert!(true)` which is indistinguishable from having no verification at all. Real verification means the program mathematically checks that the signature bytes were produced by the private key corresponding to the stored public key. We use `ed25519-dalek` because it is a production-audited Rust library that compiles to BPF and implements the exact Twisted Edwards curve equations required.

**Implementation:**
- Import `ed25519_dalek::{PublicKey, Signature, Verifier}`.
- For each submitted signature, parse the guardian's stored 32-byte pubkey into `PublicKey::from_bytes`.
- Parse the 64-byte signature into `Signature::from_bytes`.
- Call `pk.verify(&message_hash, &sig)` and abort with a typed Anchor error on failure.

## Step 4: Build Guardian Registry with Stake

**Why:** Anonymous validation is sybil-vulnerable. By requiring guardians to deposit tokens into a programmatic vault, we create an economic cost for misbehavior. The registry is a separate program to keep concerns isolated: the bridge program focuses on token custody and verification, while the guardian program focuses on identity, stake, and penalties. Separation also allows the guardian logic to be audited and upgraded independently.

**Implementation:**
- Define `GuardianRegistry` as a PDA with a `Vec<GuardianInfo>`.
- Each `GuardianInfo` stores `solana_pubkey`, `ed25519_pubkey`, `stake_amount`, and `is_active`.
- Implement `register_guardian` to append a new entry.
- Implement `stake` to transfer SPL tokens into a `stake_vault` PDA and credit the guardian's balance.

## Step 5: Implement Threshold Verification

**Why:** A single compromised guardian should not be able to mint or release tokens. A threshold (M-of-N) distributes trust. The bridge program must count valid signatures only from guardians who are both cryptographically verified and currently active in the registry. This two-layer check prevents stale signatures from removed guardians and prevents a single key from controlling the bridge.

**Implementation:**
- Read `guardian_threshold` from `BridgeState`.
- Loop through submitted signatures and indices.
- For each index, check that the guardian exists and `is_active == true`.
- Run Ed25519 verification and increment `valid_count` only on success.
- After the loop, `require!(valid_count >= threshold)`.

## Step 6: Add Mint/Burn Wrapped Tokens

**Why:** Wrapped tokens represent the original asset on the destination chain. They must be minted 1:1 with locked deposits and burned 1:1 when the user wants to redeem the original asset. The wrapped mint authority must be the bridge state PDA so that no external wallet can inflate supply. Burning wrapped tokens creates a `BurnRecord` that serves as the proof required to release original tokens from the vault.

**Implementation:**
- In `verify_and_mint_wrapped`, after threshold verification, invoke `token::mint_to` via CPI with the bridge state PDA as signer.
- In `burn_wrapped`, invoke `token::burn` via CPI with the user as signer.
- Create a `BurnRecord` PDA seeded by nonce to prevent double-release.

## Step 7: Build Relayer Service

**Why:** Users and guardians cannot be expected to manually watch the blockchain and submit transactions at the exact moment a lock occurs. A relayer automates this operational burden. Because the relayer only delivers pre-signed proofs, it does not need to be trusted with funds or mint authority. Multiple relayers can run in parallel for redundancy, and if all relayers fail, a user can still collect guardian signatures and call the API directly.

**Implementation:**
- Poll the bridge state nonce every 5 seconds.
- For each new nonce, fetch the `LockRecord`.
- Reconstruct the message hash from `user + amount + nonce`.
- Sign the hash with available guardian Ed25519 keys using `tweetnacl`.
- Submit `verify_and_mint_wrapped` via Anchor with signatures and indices.
- Advance the local cursor after confirmation.

## Step 8: Test Full Round-Trip on Devnet

**Why:** Localnet testing proves the logic compiles and the state machines work, but devnet testing proves the program interacts correctly with real RPC latency, real account rent, and real blockhash expiration. A full round-trip means lock -> mint -> burn -> release, verifying that tokens move correctly, nonces increment, signatures verify, and the vault balance stays consistent.

**Implementation:**
- Deploy both programs to devnet using `anchor deploy`.
- Airdrop devnet SOL to the authority and test users.
- Create original and wrapped mints, initialize bridge and guardian registries.
- Register two guardians, have them stake tokens.
- Lock original tokens, observe the relayer mint wrapped tokens.
- Burn wrapped tokens, submit guardian signatures, release original tokens.
- Verify vault balance is zero after full round-trip and all records are marked `is_released = true`.

# Phase 56v2 Summary

## Project Overview
Phase 56v2 is a production-hardened cross-chain bridge built on Solana using the Anchor framework. It replaces the stubbed signature checks of Phase 56 with real Ed25519 verification, introduces an economic guardian registry with stake and slash mechanics, and operates a standalone relayer that monitors lock events and submits threshold proofs automatically.

## Architecture Diagram

```
User Layer
  |
  |  POST /lock, /burn
  v
+-----------------+
|   Express API   |  port 3065
|  (bridge_api.ts)|
+-----------------+
  |
  |  Anchor Provider + Wallet
  v
+-----------------+
|  Bridge Program |  Real SPL transfers to vault PDA
|  (bridge/lib.rs)|  Real Ed25519 verify via ed25519-dalek
+-----------------+
  ^
  |  Guardian Registry PDA
  v
+-----------------+
| Guardian Program|  Stake, register, slash
| (guardian/lib.rs|
+-----------------+
  ^
  |  Poll + Sign + Submit
  v
+-----------------+
|    Relayer      |  Monitors LockEvent logs
|   (relayer.ts)  |  Signs with guardian Ed25519 keys
+-----------------+
```

## Comparison to Phase 56

### What Changed
- Signature verification changed from `assert!(true)` stub to real `ed25519_dalek::PublicKey::verify` calls.
- Guardian identities changed from hardcoded addresses to a dynamic registry with on-chain stake tracking.
- Mint authorization changed from a single trusted key to a configurable M-of-N threshold verified inside the program.
- Event detection changed from manual API calls to an automated polling relayer.
- Token custody changed from an implied account to an explicit vault PDA owned by the bridge state.

### Why Changed
- Stubbed signatures are exploitable. Any attacker can call the mint instruction directly and drain the vault.
- Hardcoded authorities are brittle. Adding or removing guardians requires a program redeployment.
- Manual relaying does not scale. Real bridges require automated services that respond to events within seconds.
- Missing economic stakes remove accountability. Guardians with nothing to lose have no incentive to behave honestly.

### How Changed
- The `verify_and_mint_wrapped` instruction now loops over signatures, parses each with `ed25519_dalek`, and increments a counter only on mathematical verification success.
- A separate `guardian` program stores `GuardianInfo` structs with `ed25519_pubkey`, `stake_amount`, and `is_active` fields.
- The bridge program deserializes the guardian registry account to enforce that signers are active and staked before counting their votes.
- `bridge_api.ts` constructs real transactions using `@coral-xyz/anchor` and returns signatures for client tracking.
- `relayer.ts` polls the bridge state nonce, fetches lock records, computes SHA-256 digests, signs with `tweetnacl`, and submits `verify_and_mint_wrapped` transactions.

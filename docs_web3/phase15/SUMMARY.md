Phase 15: Multi-Signature Program Recap
========================================

This phase covered distributed control and collective authorization on Solana.

What we learned
---------------
- **Multi-Signature (multisig)** is a program that requires multiple distinct
  approvals before executing an instruction. It eliminates single points of
  failure and enables secure treasury management.
- **Threshold** is the minimum number of signers that must approve a proposal
  for it to execute. It defines the balance between security and operational
  flexibility.
- **Signer Set** is the on-chain list of authorized public keys. Only
  signatures from addresses in this set count toward the threshold.

Why it matters
--------------
Every serious project, DAO, and treasury needs multisig security. A single
compromised key should never be able to drain a treasury or alter critical
configuration. Multisig programs distribute trust across multiple individuals
or devices and create an auditable, on-chain record of every approval.

Code we built
-------------
- `src_web3/phase15/multisig/src/lib.rs` — Rust program that stores a signer
  set and threshold, tracks approvals per proposal, and executes instructions
  only when the threshold is met.
- `src_web3/phase15/multisig/Cargo.toml` — Dependencies for the multisig program.
- `src_web3/phase15/multisig_api.ts` — TypeScript Express API that exposes
  endpoints to create a multisig, submit proposals, record approvals, and
  execute approved instructions.

Key patterns
------------
- Store the signer set and threshold in a dedicated config account.
- Track each proposal's approval count independently to prevent replay attacks.
- Validate every approver against the stored signer set before incrementing
  the approval count.
- Only execute the target instruction after the approval count reaches the
  threshold.
- Consider adding time locks or cancellation logic so stale proposals do not
  execute unexpectedly after a long delay.

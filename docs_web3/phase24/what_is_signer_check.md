# What Is a Signer Check?

## Why it exists (THE PROBLEM)

Many blockchain operations should only be performed by specific authorized parties, such as the owner of a token account or the administrator of a protocol.

Without verifying that the correct private key signed the transaction, anyone could invoke privileged instructions to steal funds, update configurations, drain treasuries, or hijack user accounts.

Signer checks are the first and most important line of defense in access control.

## Definition

A signer check is a validation step that confirms a specific account in the transaction has signed the transaction, proving that the private key holder authorized the instruction.

It is the on-chain equivalent of a notarized signature on a legal contract.

## Real-life analogy

Imagine transferring ownership of a house.

The deed office requires the seller to physically appear, show government-issued identification, and sign the transfer papers in front of a notary.

A signer check is that notary verification.

The blockchain requires cryptographic proof that the owner approved the action.

Without it, someone could submit a forged deed and steal the property by claiming the owner agreed, destroying the integrity of the entire property system.

## Tiny numeric example

Consider a wallet recovery instruction with two possible paths:

| Path | Signer Checked? | Result |
|------|----------------|--------|
| Owner signs | Yes | Recovery proceeds legitimately |
| Random address signs | No (vulnerable) | Attacker takes control of wallet |
| Random address signs | Yes (secure) | Transaction rejected before execution |

A single missing signer check can compromise the entire protocol and every user who interacts with it.

Every sensitive instruction must begin by asking who authorized this action.

Without a clear answer, the instruction should abort immediately with a descriptive error.

This defensive posture protects both users and the protocol from accidental and malicious misuse.

Signer checks are non-negotiable in any production smart contract.

Skipping them is equivalent to leaving the vault door unlocked.

## Common confusion

- "Any signer is good enough."
  The specific required signer must be validated, not just any account in the transaction that happens to have signed.

- "Signer checks are automatic."
  Raw Solana programs must manually inspect AccountMeta::is_signer.
  Anchor helps with the Signer type but developers must still use it correctly.

- "PDAs cannot be signers."
  PDAs can sign via CPI using program seeds, which is a powerful but complex pattern requiring careful validation.

- "Signer checks replace account validation."
  Signer checks prove authorization but do not verify account ownership, data contents, or relationships.

- "Multiple signers are always safer."
  Multisig improves security but increases complexity and the risk of stale or lost keys preventing legitimate access.

- "Signer checks are only for privileged instructions."
  Every instruction that modifies state should verify the appropriate signer to prevent unauthorized changes.

- "A Signer<'info> annotation is enough."
  You must also verify the signer is the correct entity, not just that some entity signed.

## Where it appears in our code

- `src_web3/phase24/vulnerable_program.rs`
  Fails to verify that the owner signed before transferring tokens out of an account, allowing theft.

- `src_web3/phase24/secure_program.rs`
  Uses the Anchor Signer type and explicit require! checks to enforce proper authorization on every sensitive instruction.

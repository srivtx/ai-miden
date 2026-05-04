Why it exists
-------------
A threshold without knowing who counts is meaningless. The problem is that
without an explicit list of authorized signers, anyone could claim to be a
valid approver. The Signer Set is the on-chain registry of public keys that
are permitted to vote on multisig proposals. It is the foundation of identity
and authorization for the multisig.

Definition
----------
A Signer Set is the list of public keys stored in a multisig program that
defines which addresses are eligible to approve transactions. Only signatures
from keys in this set count toward the threshold.

Real-life analogy
-----------------
Imagine a private club with a roster of members. At the door, a bouncer checks
every guest's name against the roster. If your name is on the list, you can
enter and vote on club matters. If your name is not on the list, the bouncer
turns you away no matter how loudly you demand entry. The roster is updated
only by a vote of existing members. The signer set is that club roster. The
multisig program checks every transaction approver against the stored set.
If the signer is not in the set, their approval does not count.

Tiny numeric example
--------------------
A multisig config account stores the following signer set:
- Signer 1: `Alice111...`
- Signer 2: `Bob222...`
- Signer 3: `Carol333...`
- Signer 4: `Dave444...`
- Signer 5: `Eve555...`
A proposal is submitted with signatures from:
- `Alice111...` (valid, in set)
- `Bob222...` (valid, in set)
- `Mallory999...` (invalid, not in set)
The program counts exactly two valid approvals. If the threshold is 3, the
proposal is not executed. If `Carol333...` also approves, the count becomes
3 and execution proceeds. `Mallory999...` never counts, no matter how many
times they sign.

Common confusion
----------------
- The signer set is not the same as a wallet's address book. The address book
  is off-chain and optional. The signer set is on-chain and enforced by code.
- Signers can be removed from the set, but removal usually requires meeting
  the current threshold. This prevents a single signer from kicking out others.
- A signer's key can be a regular wallet or another program address. Program
  signers enable DAOs and automated agents to participate in multisig approval.
- The signer set does not store private keys. It only stores public keys.
  Private keys remain with the individual signers.
- Duplicate public keys in the signer set are usually meaningless. Most
  programs deduplicate or reject duplicates during initialization.
- Changing the signer set size may require resizing the config account, which
  can be complex. Some programs allocate a fixed maximum number of signers.
- The signer set is typically immutable except through the multisig's own
  governance process. An admin key cannot usually bypass the set.

Where it appears in our code
----------------------------
`src_web3/phase15/multisig/src/lib.rs` — stores the signer set in the multisig
config and iterates over it to validate approvers.

Signer set governance
---------------------
The signer set is not static. Members may leave, new members may join, and
compromised keys must be revoked. Most multisig programs allow the existing
signer set to vote on membership changes. Because the program itself enforces
the threshold, a malicious member cannot unilaterally add allies or remove
rivals. Some advanced implementations use on-chain identity or reputation
systems to automatically adjust voting weight. When managing a signer set,
keep an off-chain backup of member contact information and verification
procedures to handle lost keys or disputes.

Practical Signer Set checklist
------------------------------
- Review the signer set quarterly for accuracy and necessity.
- Verify new members through out-of-band channels before adding them.
- Remove inactive members promptly to reduce the attack surface.
- Store member public keys in multiple secure locations.
- Document the procedure for handling a compromised signer key.

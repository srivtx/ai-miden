Why it exists
-------------
Requiring a single private key to control valuable assets is dangerous. The
problem is that if one person's key is lost, stolen, or compromised, the funds
are gone forever. Organizations, treasuries, and high-security wallets need a
way to require multiple independent approvals before any transaction executes.
A Multi-Signature (multisig) program solves this by enforcing that a predefined
number of signers must approve an instruction before it can be executed. This
distributes trust and reduces single points of failure.

Definition
----------
A Multi-Signature program is an on-chain smart contract that stores a set of
authorized signers and a threshold number of required approvals. It only
executes an instruction after the threshold of distinct signers has approved it.

Real-life analogy
-----------------
Imagine a corporate bank account that requires two out of three executives to
sign any check over ten thousand dollars. The bank keeps a list of the three
authorized executives. When someone submits a check, the bank verifies that at
least two different executives signed it. One executive alone cannot drain the
account. If one executive loses their signing pen, the other two can still
operate the account. If a malicious employee forges one signature, the bank
rejects the check because only one valid signature is present. A Solana multisig
program is that bank rulebook encoded on-chain. It stores the list of signers,
counts approvals, and only releases funds when the threshold is met.

Tiny numeric example
--------------------
A DAO sets up a treasury multisig with five members and a threshold of three.
Members: Alice, Bob, Carol, Dave, Eve.
The multisig stores the signer set and threshold in a config account.
A proposal is created to send 10,000 USDC to a contractor.
- Alice approves. Current approvals: 1 (insufficient)
- Bob approves. Current approvals: 2 (insufficient)
- Carol approves. Current approvals: 3 (threshold met)
The multisig program now executes the transfer CPI.
If only Alice and Bob approve and the others abstain, the transfer never
executes and the USDC remains in the treasury.

Common confusion
----------------
- A multisig is not a group chat or voting system. It is an on-chain program
  that enforces signature counting and execution.
- The threshold can be changed, but usually only by the existing multisig
  itself. This prevents an attacker from lowering the threshold unilaterally.
- Multisig approvals are recorded on-chain. Once a signer approves, their
  approval is public and cannot be revoked in most simple implementations.
- A 1-of-1 multisig is functionally identical to a regular wallet. The
  security benefit only appears with N >= 2.
- Multisig signers do not need to be human wallets. They can be other programs
  or hardware devices, enabling automated governance pipelines.
- Losing access to too many signer keys can permanently lock the funds. A
  3-of-3 multisig where two keys are lost is unrecoverable.
- Multisig programs are not the same as the SPL Token multisig feature, which
  is a simpler built-in mechanism. Custom multisig programs offer richer logic.

Where it appears in our code
----------------------------
`src_web3/phase15/multisig/src/lib.rs` — implements signer set storage,
approval tracking, threshold enforcement, and conditional execution.

Multisig deployment patterns
----------------------------
Real-world deployments often use a factory pattern to create multisig
instances. A factory program stores a template configuration and clones it
for each new multisig, reducing deployment costs and ensuring consistency.
Some projects deploy a single global multisig program and use separate state
accounts per treasury. Others embed multisig logic directly into their main
program to avoid external dependencies. The choice depends on upgradeability
needs, audit scope, and composability requirements.

Practical Multisig checklist
----------------------------
- Choose a threshold that balances security and operational continuity.
- Distribute signer keys across different devices, locations, and people.
- Document the recovery plan if signers are lost or compromised.
- Test the full lifecycle: create, propose, approve, execute, and upgrade.
- Consider time delays between approval and execution for sensitive actions.

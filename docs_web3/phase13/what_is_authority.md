Why it exists
-------------
On-chain programs need a clear way to decide who can change state, move funds,
or update configuration. The problem is that without a defined authority,
anyone could call privileged instructions like emergency pause, fee changes,
or fund withdrawal. Authority is the on-chain identity that the program checks
before executing sensitive operations. It is the root of trust and control.

Definition
----------
Authority is a designated public key or PDA that a program checks as a signer
or owner before allowing privileged instructions to execute.

Real-life analogy
-----------------
Think of a building's master key system. Every employee has a key that opens
the front door. Only the facilities manager has the master key that opens the
server room, electrical panel, and safe. The locks physically check whether the
key has the right grooves. If you try to open the server room with a regular
office key, the lock rejects you. In a Solana program, the authority is the
master key holder. The program checks whether the transaction signer matches
the stored authority public key. If not, the instruction fails immediately.

Tiny numeric example
--------------------
A vault program stores its authority in a config account:
- Config account data bytes 0-31: authority public key
- A malicious user sends an instruction to change the withdrawal fee to 100%.
- The program reads bytes 0-31 and compares them to the instruction signers.
- The malicious user's key does not match. The program returns an error.
- Later, the legitimate authority sends the same instruction and signs.
- The keys match. The program updates the fee.
This single comparison protects the entire program from unauthorized changes.

Common confusion
----------------
- Authority is not the same as ownership. A user owns their token account, but
  a program authority controls program configuration. They operate at different
  layers.
- Setting authority to None is a common way to make a program immutable. Once
  removed, no one can change settings, which is useful for decentralization.
- A program can have multiple authorities for different functions. One key may
  control fees, while another controls emergency pause.
- Authority checks happen inside the program logic. The runtime does not
  automatically enforce authority; the developer must write the check.
- PDAs can be authorities. A program can store a PDA as the authority and then
  use `invoke_signed` to authorize actions that only the program should trigger.
- Transferring authority usually requires a two-step process: propose and accept.
  This prevents accidentally sending authority to a wrong or dead address.
- Authority is not a role stored on-chain by the runtime. It is a convention
  where programs store a public key in an account and compare it to signers.

Where it appears in our code
----------------------------
`src_web3/phase13/vault/src/lib.rs` — stores an authority in the vault config
and validates it before processing administrative instructions.

Authority patterns in practice
------------------------------
Many programs implement a two-step authority transfer to prevent accidental
loss of control. The current authority proposes a new authority by writing
the new public key into a pending field. The proposed authority then must
send a separate accept instruction to finalize the transfer. This prevents
sending authority to an invalid address or a key that no one controls. Some
programs also implement role-based authorities, where different addresses
control different functions such as fee adjustment, emergency pause, and
fund recovery. Role separation reduces the blast radius if one key is
compromised.

Practical Authority checklist
-----------------------------
- Use two-step transfer for critical authority changes.
- Consider role-based authorities for complex programs.
- Document all authority addresses and their intended powers.
- Test authority rejection paths to ensure unauthorized access is blocked.
- Plan for authority recovery in case the primary key is lost.
- Rotate authority keys periodically as part of security hygiene.
- Publish authority addresses in public documentation for transparency.
- Require multisig approval for critical authority operations when possible.
- Freeze authority state during audits to prevent unexpected changes.

Why it exists
-------------
Standard CPI with `invoke` works only when the original transaction signer
has signed for the accounts being used. The problem arises when a Program
Derived Address (PDA) needs to act as a signer in a CPI call. PDAs have no
private key, so they cannot produce a cryptographic signature. Yet many
programs need PDAs to own token accounts, authorize transfers, or call other
programs on behalf of the program logic. `invoke_signed` solves this by
allowing the calling program to cryptographically prove that it "owns" the
PDA, thus granting the PDA temporary signing authority during the CPI.

Definition
----------
`invoke_signed` is a Solana runtime function that performs a CPI while
allowing the calling program to sign on behalf of one or more Program
Derived Addresses by providing the seeds used to generate those addresses.

Real-life analogy
-----------------
Think of a corporate bank account that requires two signatures: the CFO and
the company seal. The CFO is a real person who can sign. The company seal is
not a person, but it carries legal authority because the corporation's bylaws
say so. When the CFO brings the seal to the bank, the bank accepts the seal's
authority because the CFO can prove they represent the corporation.
`invoke_signed` is the CFO bringing the seal. The program proves it is the
rightful owner of the PDA by presenting the seeds, and the runtime accepts
the PDA as a signer for the duration of that one CPI call.

Tiny numeric example
--------------------
A program owns a PDA at address `7xK...` derived from seed `["vault", user_id]`.
This PDA holds 500 tokens in an associated token account. The program wants
to transfer 100 tokens to Alice via CPI to the SPL Token program.
- Seeds provided to `invoke_signed`: `[b"vault", user_id.to_le_bytes()]`
- Runtime verifies: `Pubkey::create_program_address(seeds, program_id)`
  matches the PDA in the account list.
- The CPI proceeds with the PDA listed as a signer.
- 100 tokens move from the PDA's token account to Alice's token account.
Without `invoke_signed`, the transfer would fail with "missing required signature"
because the PDA has no private key to sign a standard transaction.

Common confusion
----------------
- `invoke_signed` does not allow a program to sign for arbitrary addresses.
  It only works for PDAs derived from that exact program's ID and seeds.
- The seeds passed to `invoke_signed` must exactly match the seeds used when
  the PDA was originally created. A single wrong byte causes a mismatch failure.
- `invoke_signed` does not expose the program's own program ID as a signer.
  It only elevates specific PDAs to signer status for that CPI context.
- You cannot use `invoke_signed` to sign for a regular wallet address. Regular
  addresses require a real cryptographic signature from their private key.
- The runtime performs the PDA derivation and verification during the CPI call.
  The program does not need to precompute or cache the proof.
- Multiple PDAs can be signed for in a single `invoke_signed` call by providing
  a vector of seed sets. Each seed set corresponds to one PDA that needs signing.
- `invoke_signed` is not a backdoor. It is a carefully restricted mechanism
  that only works for addresses deterministically linked to the caller program.

Where it appears in our code
----------------------------
`src_web3/phase11/cpi_demo/src/lib.rs` — demonstrates `invoke_signed` where
a program signs for its own PDA during a token transfer CPI.

Security considerations for invoke_signed
-----------------------------------------
Because `invoke_signed` grants signing power to PDAs, any bug in seed
derivation can be catastrophic. If a program uses predictable seeds without
sufficient entropy, an attacker may precompute the PDA and interact with it
unexpectedly. Always include unique identifiers such as user public keys,
nonce values, or instruction-specific data in the seed array. Additionally,
programs should verify PDA ownership before performing sensitive operations.
A PDA owned by the correct program but derived with wrong seeds can still
pass basic checks while creating logic vulnerabilities.

Practical invoke_signed checklist
---------------------------------
- Include unique, unpredictable components in seeds.
- Verify PDA ownership before accepting it as authority.
- Use `find_program_address` rather than `create_program_address` when possible.
- Log seed components during development to aid debugging.
- Never expose raw bump seeds to untrusted client code.

Why it exists
-------------
Every instruction in Solana must specify which program will process it. The
problem is that malicious transactions could try to trick a program by
supplying the wrong program ID or by confusing the runtime about which code
should execute. Solana enforces strict program identification so that each
instruction is handled by the exact bytecode that users and developers expect.
Understanding `program_id` is fundamental to writing secure programs that
can verify they are the intended processor and that CPI calls target the
correct programs.

Definition
----------
`program_id` is the public key address that uniquely identifies a deployed
Solana program. It is passed into every instruction handler and is used by
the runtime to load the correct executable bytecode and by programs to
verify ownership of PDAs.

Real-life analogy
-----------------
Think of a `program_id` as the mailing address of a government office. If you
send your passport application to the wrong address, the wrong office might
open it, or it might get lost entirely. Every envelope must have the correct
address to reach the intended department. Similarly, every Solana instruction
must name the correct `program_id` so the runtime delivers it to the right
program. If you send a token transfer instruction to a random program address,
the runtime will reject it because that program does not recognize the
instruction format.

Tiny numeric example
--------------------
Suppose three programs exist on devnet:
1. SPL Token Program: `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`
2. Our Lending Program: `LenD1ng111111111111111111111111111111111111`
3. A Malicious Program: `M4l1c1ouS1111111111111111111111111111111111`
A transaction contains an instruction to transfer 10 tokens. The runtime
looks at the `program_id` field in that instruction. If it points to the SPL
Token Program, the transfer executes. If it points to the malicious program,
the runtime loads the malicious code, which likely fails or does nothing
useful because it does not implement the SPL Token interface. The `program_id`
is the guard that ensures the right code runs.

Common confusion
----------------
- `program_id` is not the address of a user wallet. It is always the address
  of an executable program account on Solana.
- The `program_id` in an instruction does not change based on who sends the
  transaction. It is fixed to the program that should process the instruction.
- Programs cannot change their own `program_id`. It is permanently assigned
  when the program is deployed.
- Two different programs cannot share the same `program_id`. Each deployed
  program has a globally unique address derived from its deployer and a nonce.
- The `program_id` passed to `process_instruction` is not something the caller
  chooses arbitrarily. The runtime sets it based on which program is executing.
- When performing CPI, you must explicitly pass the target program's
  `program_id` in the account list. The runtime will not guess for you.
- Upgradeable programs keep the same `program_id` even when their underlying
  bytecode is replaced. The address is stable; the code behind it can change.

Where it appears in our code
----------------------------
`src_web3/phase11/cpi_demo/src/lib.rs` — uses `program_id` to verify PDA
ownership and to specify the target program in CPI account lists.

Program ID in deployment and upgrades
-------------------------------------
When a program is deployed, its program ID is derived from the deployer's
public key and a nonce. This means the same source code deployed twice will
receive two different program IDs. Developers must carefully manage program
IDs across devnet, testnet, and mainnet environments. Upgradeable programs
maintain the same program ID while their executable data is swapped via a
buffer account. This stability allows frontends and other programs to reference
a consistent address while the underlying logic evolves. However, the upgrade
authority must be secured because it can replace the program bytecode at any
time, potentially introducing malicious behavior.

Practical program_id checklist
------------------------------
- Hardcode program IDs per network in configuration files.
- Verify program IDs in client code before submitting transactions.
- Document upgrade authority policies for audited programs.
- Use deterministic addresses for PDAs to simplify frontend integration.
- Never trust a program ID passed from an untrusted client without validation.

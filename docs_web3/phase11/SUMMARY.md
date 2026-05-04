Phase 11: Cross-Program Invocation (CPI) Recap
==============================================

This phase covered the core mechanism that makes Solana programs composable.

What we learned
---------------
- **Cross-Program Invocation (CPI)** allows one program to call another
  program securely within the same transaction. This is how DeFi protocols
  compose token transfers, oracle updates, and lending logic atomically.
- **`invoke_signed`** enables programs to sign on behalf of Program Derived
  Addresses (PDAs). Because PDAs have no private keys, `invoke_signed` is
  essential for programs to manage token accounts and authorize actions that
  require a signer.
- **`program_id`** is the unique public key address of a deployed program.
  It ensures that instructions are routed to the correct bytecode, and it
  is used to verify that a PDA truly belongs to a specific program.

Why it matters
--------------
Without CPI, every Solana program would be an isolated island. A lending
protocol would need to reimplement token logic. An NFT marketplace would
need to rewrite royalty distribution. CPI makes the ecosystem modular.
Programs specialize in one thing and expose their functionality for others
to use safely and atomically.

Code we built
-------------
- `src_web3/phase11/cpi_demo/src/lib.rs` — Rust program demonstrating CPI
  with `invoke` and `invoke_signed` for PDA-based token transfers.
- `src_web3/phase11/cpi_api.ts` — TypeScript Express API that constructs
  and sends transactions containing CPI instructions.

Key patterns
------------
- Always pass the target program ID and all required accounts in the CPI
  account list.
- Use `invoke_signed` with the exact seeds when a PDA must act as a signer.
- Remember the CPI depth limit of four levels to avoid design errors.
- CPI preserves atomicity. A failure in any nested call reverts everything.

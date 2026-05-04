Phase 14: Escrow Program Recap
==============================

This phase covered trustless exchange mechanisms that protect both sides of a trade.

What we learned
---------------
- **Escrow** is a temporary custody contract that holds both parties' assets
  until agreed conditions are met. It protects against non-delivery and enables
  safe peer-to-peer trading without a trusted intermediary.
- **Atomic Swap** bundles multiple transfers into a single transaction that
  either fully succeeds or fully reverts. It eliminates the risk of partial
  execution and ensures no party is left holding an unfavorable position.
- **Trade Matching** is the algorithmic pairing of compatible buy and sell
  orders based on price, quantity, and validity rules. It automates the
  discovery and execution of trades in a marketplace.

Why it matters
--------------
Every exchange, marketplace, and OTC desk depends on escrow and matching logic.
Without these primitives, trading would revert to slow, risky manual settlement.
Understanding how to build atomic, condition-gated transfers is essential for
any financial application on Solana.

Code we built
-------------
- `src_web3/phase14/escrow/src/lib.rs` — Rust program that handles two-party
  deposits, confirmation, cancellation, and atomic release of tokens.
- `src_web3/phase14/escrow/Cargo.toml` — Dependencies for the escrow program.
- `src_web3/phase14/escrow_api.ts` — TypeScript Express API that exposes
  endpoints for creating escrows, depositing, confirming, canceling, and
  releasing matched trades.

Key patterns
------------
- Always include an expiration or cancellation mechanism so funds cannot be
  locked indefinitely if one party disappears.
- Track each party's deposit independently in the escrow state account.
- Use CPI to the SPL Token program for releases; never manipulate balances
  manually in the escrow program.
- Combine deposit instructions into a single transaction when possible to
  approach atomic behavior, or use explicit state transitions for async escrows.
- Validate that both sides of a match satisfy the price and quantity rules
  before executing the release.

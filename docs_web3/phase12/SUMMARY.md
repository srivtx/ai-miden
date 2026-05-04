Phase 12: SPL Tokens Recap
==========================

This phase covered the token layer that powers every DeFi application on Solana.

What we learned
---------------
- **SPL Token** is Solana's native token standard. It defines a common
  interface for minting, transferring, burning, and freezing tokens so that
  wallets, exchanges, and programs can interact with any token uniformly.
- **Mint** is the canonical account that defines a token type. It tracks
  total supply, decimals, and authorities. Every token account refers back
  to exactly one Mint.
- **Token Account** holds the balance of a specific SPL token for a specific
  owner. Wallets can own many token accounts, one per mint, keeping balances
  isolated and operations parallelizable.
- **Associated Token Account (ATA)** is a token account at a deterministic
  address derived from a wallet and a mint. ATAs eliminate the need for users
  to manage or share multiple addresses.

Why it matters
--------------
Tokens are the basic unit of value in Web3. Stablecoins, governance tokens,
NFTs, and reward points all rely on the SPL Token standard. Understanding
how Mints, Token Accounts, and ATAs interact is essential for building any
application that moves value on Solana.

Code we built
-------------
- `src_web3/phase12/spl_token/src/lib.rs` — Rust program that creates mints,
  initializes token accounts, and performs transfers via SPL Token CPI.
- `src_web3/phase12/spl_token/Cargo.toml` — Dependencies for SPL Token program.
- `src_web3/phase12/token_api.ts` — TypeScript Express API that exposes
  endpoints to create mints, mint tokens, query balances, and transfer tokens.

Key patterns
------------
- Always derive ATAs using the Associated Token Account program when sending
  tokens to users.
- Check token account balances and decimals before displaying amounts to users.
- Use CPI to the SPL Token program instead of reimplementing transfer logic.
- Remember that closing a token account requires a zero balance.

Why it exists
-------------
Solana's native token is SOL, but most DeFi applications need custom tokens
representing stablecoins, governance rights, or in-game assets. The problem is
that every project cannot build its own token standard from scratch without
creating fragmentation, security holes, and incompatible wallets. The SPL Token
program is Solana's standard for fungible and non-fungible tokens. It provides
a shared, audited, and battle-tested implementation so all tokens behave the
same way across exchanges, wallets, and smart contracts.

Definition
----------
SPL Token is Solana's token standard implemented as a single on-chain program.
It defines how tokens are minted, transferred, burned, and stored in token
accounts, ensuring interoperability across the entire Solana ecosystem.

Real-life analogy
-----------------
Imagine every country printed its own money with different sizes, colors, and
security features. Traveling and trading would be chaotic. The SPL Token program
is like the international banking network that says all valid currency must fit
in a standard checking account with standard deposit and withdrawal rules.
Whether you hold US dollars, Japanese yen, or loyalty points, the bank account
works the same way. SPL Token is that standard. Every wallet and exchange knows
exactly how to read balances, send transfers, and verify ownership because they
all speak the same SPL language.

Tiny numeric example
--------------------
Alice wants to create a community token called ALC.
1. Alice creates a Mint account with decimals set to 6.
2. Alice creates a Token Account associated with her wallet to hold ALC.
3. Alice mints 1,000,000 ALC into her token account.
4. Alice sends 250,000 ALC to Bob.
All four steps use the same SPL Token program instructions. The Mint defines
the supply rules. The Token Account holds the balance. The SPL program
processes every transfer. If Alice later mints another 500,000 ALC, the total
supply becomes 1,500,000 and her balance becomes 1,250,000.

Common confusion
----------------
- SPL Token is not a specific cryptocurrency like USDC. It is a standard
  that many tokens including USDC, USDT, and custom project tokens follow.
- SPL Token accounts do not hold SOL. They hold the specific SPL token type
  defined by their associated Mint. A wallet holds SOL; token accounts hold
  SPL tokens.
- You cannot send SPL tokens directly to a wallet address. You must send them
  to a token account owned by that wallet.
- The SPL Token program is upgradeable. New features like confidential
  transfers can be added without changing the token standard itself.
- Burning an SPL token reduces the supply tracked on the Mint account, not
  just the balance on a token account.
- Freezing an SPL token account prevents transfers out of that account. It
  does not destroy the tokens or affect other holders.
- SPL Token and Token-2022 are different programs. Token-2022 is a newer
  version with additional features, but SPL Token remains the most widely
  used standard.

Where it appears in our code
----------------------------
`src_web3/phase12/spl_token/src/lib.rs` — demonstrates creating mints and
managing token accounts using SPL Token program CPI calls.

SPL Token instruction categories
--------------------------------
The SPL Token program supports several instruction families. Mint instructions
include `initialize_mint` and `mint_to`. Account instructions include
`initialize_account`, `close_account`, and `set_authority`. Transfer
instructions include `transfer`, `transfer_checked`, and `approve`. Advanced
features include `freeze_account` and `thaw_account` for compliance use cases.
Understanding these categories helps developers choose the right primitive
instead of reimplementing standard behavior.

Practical SPL Token checklist
-----------------------------
- Always create ATAs using the Associated Token Account program.
- Verify token account mint matches the expected mint before transfers.
- Check account balances in base units, then convert using mint decimals.
- Use `transfer_checked` when working with multiple token types to validate
  mint and decimals on-chain.
- Avoid hardcoding token program IDs; import them from official SDKs.

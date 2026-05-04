Why it exists
-------------
Solana wallets are generic accounts that hold SOL and do not natively track
arbitrary token balances. The problem is that a single wallet might hold dozens
of different SPL tokens. Storing all those balances inside the wallet account
would make the account huge, expensive, and difficult to index. Token accounts
solve this by creating a separate account for each token type owned by a wallet.
This keeps wallet accounts small and allows parallel operations on different
tokens.

Definition
----------
A Token Account is a Solana account owned by the SPL Token program that holds
a balance of exactly one SPL token type, defined by its associated Mint, and
owned by a specific wallet or program.

Real-life analogy
-----------------
Imagine your wallet is your identity card. It proves who you are, but it does
not carry all your money. Instead, you have separate bank accounts: one for
your salary, one for savings, and one for travel expenses. Each account holds
a different type of balance and has its own rules. Your identity card links
them all together because the bank knows they belong to you. A Solana wallet
is like the identity card. Token accounts are the separate bank accounts. Your
wallet may own one token account for USDC, another for a governance token, and
a third for an NFT collection. Each token account holds exactly one currency.

Tiny numeric example
--------------------
Alice owns a wallet at address `AliceWallet...`.
She has three token accounts:
1. Token Account A: Mint = USDC, Balance = 5,000,000 (6 decimals = 5.00 USDC)
2. Token Account B: Mint = ALC, Balance = 1,000,000,000 (9 decimals = 1.0 ALC)
3. Token Account C: Mint = BORED_APE_NFT, Balance = 1 (0 decimals = 1 NFT)
Each account is 165 bytes and holds exactly one balance. If Alice receives
more USDC, only Token Account A changes. If she sends her ALC, only Token
Account B changes. The operations are independent and can happen in parallel.

Common confusion
----------------
- A Token Account is not a wallet. You cannot store SOL in a Token Account.
  It only holds SPL tokens of one specific Mint.
- Each wallet can have multiple token accounts, but only one per Mint unless
  manually created otherwise.
- Token accounts have an associated owner, which is usually a wallet public key.
  Only the owner can authorize transfers from that token account.
- Closing a token account returns its rent lamports to the owner, but only
  if the balance is zero. You cannot close an account that still holds tokens.
- A token account's address is not the same as the wallet owner's address.
  It is a separate public key generated specifically to hold that token balance.
- Delegation allows another address to spend tokens on your behalf up to a
  specified amount. It does not transfer ownership of the account.
- Token accounts can be frozen if the Mint has a freeze authority and chooses
  to freeze that specific account. Frozen accounts cannot send or receive.

Where it appears in our code
----------------------------
`src_web3/phase12/spl_token/src/lib.rs` — demonstrates creating token accounts
and querying their balances via CPI.

Token account lifecycle
-----------------------
A token account begins uninitialized. After creation, it must be initialized
with a mint and owner. It can then receive deposits, authorize transfers,
and delegate spending. When the balance reaches zero and the owner no longer
needs the account, it can be closed, returning the rent lamports to a
destination wallet. Each state transition requires a specific SPL Token
instruction, and skipping steps results in runtime errors. Programs that
manage many user token accounts must be careful to track which accounts exist
to avoid redundant creation instructions.

Practical Token Account checklist
---------------------------------
- Always verify the mint and owner fields match expectations.
- Close unused accounts to reclaim rent and reduce state bloat.
- Use delegation carefully; revoke it when no longer needed.
- Check that an account is initialized before reading its balance.
- Avoid creating duplicate token accounts for the same mint and owner.
- Validate the token program owner field to detect malformed accounts.
- Prefer `getAccount` SDK helpers over manual account parsing for safety.

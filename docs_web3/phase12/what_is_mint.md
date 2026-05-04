Why it exists
-------------
Before any token can exist on Solana, there must be a central record defining
its properties. The problem is that without a single source of truth, anyone
could claim to have created a token, and there would be no way to verify total
supply, decimals, or minting authority. The Mint account solves this by serving
as the canonical registry for a token type. Every SPL token has exactly one
Mint account that controls how the token behaves and tracks how much exists.

Definition
----------
A Mint is a Solana account owned by the SPL Token program that stores metadata
about a token type, including its total supply, number of decimals, mint
authority, and freeze authority.

Real-life analogy
-----------------
Think of a Mint as the central bank that issues a national currency. The bank
decides how many decimal places the currency has (cents, yen, etc.), who is
authorized to print more money, and how much total money exists in circulation.
Every bill in the economy refers back to that central bank for validation. If
someone tries to spend a counterfeit bill, the banking system rejects it because
the serial number does not match the central registry. Similarly, every SPL
token account refers back to its Mint. The SPL Token program checks the Mint
before allowing any creation, transfer, or burn.

Tiny numeric example
--------------------
A project creates a governance token with the following Mint configuration:
- Decimals: 9 (common for DeFi tokens)
- Initial supply: 0 (no tokens exist yet)
- Mint authority: A multisig wallet controlled by the DAO
- Freeze authority: None (tokens cannot be frozen)
After creation, the DAO mints 10,000,000 tokens. The Mint account updates:
- Supply: 10,000,000
If the DAO later burns 1,000,000 tokens, the Mint updates again:
- Supply: 9,000,000
The Mint is the single source of truth for all supply changes.

Common confusion
----------------
- A Mint account does not hold token balances. It only holds metadata. Token
  balances live in Token Accounts.
- There is exactly one Mint account per token type. You cannot have multiple
  Mints for the same token symbol without them being entirely separate tokens.
- Setting mint authority to None makes the token supply fixed forever. No one
  can mint more, which is often done for deflationary or fair-launch tokens.
- Decimals on the Mint determine how balances are displayed, not how they are
  stored. A balance of 1000000 with 6 decimals is displayed as 1.000000.
- Freeze authority can be revoked by setting it to None. Once revoked, tokens
  can never be frozen again.
- The Mint account must be initialized before any token accounts for that mint
  can be created. Attempting to create a token account for an uninitialized
  Mint will fail.
- Creating a Mint requires a rent-exempt balance of lamports. The exact amount
  depends on the account size and current rent rates.

Where it appears in our code
----------------------------
`src_web3/phase12/spl_token/src/lib.rs` — demonstrates initializing a Mint
account with a mint authority and fixed decimals.

Mint authority patterns
-----------------------
Projects use several mint authority strategies depending on their goals. A
fixed supply token sets the mint authority to None after the initial mint,
ensuring no further inflation. A governance-controlled token keeps the mint
authority under a DAO treasury or multisig, allowing inflation only after
community votes. An algorithmic stablecoin may keep the mint authority within
a programmatic vault that mints or burns based on oracle prices. Choosing the
right pattern affects trust, predictability, and regulatory perception.

Practical Mint checklist
------------------------
- Decide early whether the token will have a fixed or inflationary supply.
- Store the mint authority securely; losing it can lock supply permanently.
- Document the mint authority address and any transfer plans.
- Test decimal behavior carefully to avoid off-by-factor-of-ten errors.
- Use `initialize_mint2` when available for cleaner CPI interfaces.
- Verify the mint rent exemption before deployment to prevent creation failure.

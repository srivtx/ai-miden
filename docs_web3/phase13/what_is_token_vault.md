Why it exists
-------------
DeFi applications need secure places to store user tokens without giving any
single administrator unchecked withdrawal power. The problem is that if tokens
sit in a regular wallet, a compromised private key drains everything instantly.
A Token Vault program solves this by creating a programmable escrow where tokens
are held by a program-controlled PDA. Withdrawals can be gated by time locks,
multi-signature requirements, or any custom logic encoded in the program.

Definition
----------
A Token Vault Program is an on-chain program that uses Program Derived Addresses
to custody SPL tokens on behalf of users. It enforces custom withdrawal rules
and only releases tokens when the programmed conditions are met.

Real-life analogy
-----------------
Think of a safety deposit box at a bank. You put your valuables inside, but you
do not carry the key around with you daily. The bank holds the box in a secure
vault. To open it, you must present identification, sign a log, and sometimes
return with a second authorized person. The bank does not own your valuables,
but it enforces the rules around access. A Token Vault program is that bank
vault. Users deposit tokens into a PDA-controlled box. The program enforces
rules like "wait 24 hours" or "require two signatures" before the tokens can
leave. The program never owns the tokens in spirit, but it controls the lock.

Tiny numeric example
--------------------
Alice deposits 1,000 USDC into a vault program.
- Vault PDA address derived from seeds `["vault", alice_wallet, usdc_mint]`
- Deposit transaction: Alice's ATA sends 1,000 USDC to the vault's ATA.
- Vault state account records: owner = Alice, amount = 1,000, unlock_time = now + 86400s
Bob tries to withdraw after 100 seconds. The program rejects because the current
time is less than unlock_time. After 86,400 seconds, Alice calls withdraw.
The program verifies her signature, checks the time, then CPI transfers
1,000 USDC from the vault ATA back to Alice's ATA.

Common confusion
----------------
- A vault does not burn or mint tokens. It only holds existing tokens in a
  program-controlled token account.
- The vault program does not hold SOL in its PDA unless specifically designed
  to do so. It typically holds SPL tokens in ATAs owned by the PDA.
- Vaults are not inherently trustless. Users must trust the program logic, so
  open-source code and audits are critical.
- A compromised vault program could drain all deposited tokens because the
  program signs for the PDA. This is why program security is paramount.
- Vault state and token balances are separate. The state account tracks intent
  and rules; the token account tracks actual SPL balances. They must stay in sync.
- Not all vaults use time locks. Some use role-based access, voting outcomes,
  or oracle conditions to trigger release.
- Closing a vault usually requires withdrawing all tokens first. The program
  will reject a close instruction if any token balance remains.

Where it appears in our code
----------------------------
`src_web3/phase13/vault/src/lib.rs` — implements deposit, time-locked state,
and withdrawal logic using PDA-owned token accounts.

Vault design patterns
---------------------
Vaults can be designed for many purposes beyond simple time locks. Yield
vaults deposit user funds into lending protocols and distribute interest.
Insurance vaults collect premiums and release payouts based on oracle-verified
events. Vesting vaults release tokens gradually according to a schedule.
Each design shares the same core pattern: a PDA owns the token account, and
the program enforces release rules. The key difference is the condition logic
that triggers the CPI transfer. When building a vault, start with the simplest
rule set and add complexity only after the core custody pattern is secure.

Practical Token Vault checklist
-------------------------------
- Derive vault PDAs from user-specific seeds for easy lookup.
- Store all release conditions in a dedicated state account.
- Validate the token account balance matches the state record.
- Include emergency pause or cancellation logic for unexpected scenarios.
- Audit the program thoroughly because it holds user funds.
- Monitor vault balances with automated alerts for unusual activity.
- Document the vault PDA derivation formula for frontend integrations.
- Review vault access logs regularly to detect suspicious patterns.

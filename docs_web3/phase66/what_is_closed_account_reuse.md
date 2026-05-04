# What Is Closed Account Reuse

## The Problem
An attacker can re-initialize or re-use an account that was previously closed because the program failed to invalidate the account discriminator or clear sensitive data during closure. A closed account retains its valid type discriminator, allowing subsequent instructions to treat it as an active account.

## Definition
Closed account reuse occurs when a program transfers the lamports out of an account (effectively closing it) but leaves the account data and Anchor discriminator intact. Because the discriminator still identifies the account as a valid instance of its type, other program instructions may accept and operate on the "closed" account as if it were still active.

## How It Works
1. Identify the close instruction: Find the code that drains an account's lamports.
2. Check program ID whitelist: Ensure the close instruction properly assigns ownership back to the System Program when needed.
3. Validate account ownership: Verify that the account being closed is actually owned by the program.
4. Verify instruction data: Confirm the close instruction does not rely solely on a user-controlled `is_initialized` flag.
5. Restrict permissions: Ensure only the rightful owner or authority can trigger a close.
6. Audit: Search for instructions that accept the same account type without checking whether it was properly closed.

## Real-life analogy
Imagine a hotel room that was vacated and refunded, but the front desk never marks the key card as deactivated. The next day, a guest returns with the old key card and is granted access to the room because the system still sees it as a valid, active reservation.

## Tiny numeric example with exploit payload
A user account holds a balance of 500 tokens. The close instruction returns rent lamports to the owner but leaves the `balance: 500` field in the account data. An attacker passes this "closed" account to a `ClaimAirdrop` instruction that reads the balance to determine reward size. The instruction sees `balance: 500` and issues 500 bonus tokens to the attacker.

## Common confusion
- "Transferring all lamports out effectively destroys the account." No. The account data and discriminator remain until explicitly overwritten or the owner is changed.
- "Setting an `is_initialized` flag to false is sufficient." No. A flag inside account data can be flipped back by re-initialization logic if the discriminator is still valid.
- "Anchor automatically handles account closure." No. Only the `close = signer` constraint or manual discriminator reset properly closes an Anchor account.
- "Zeroing lamports is enough to prevent reuse." No. The account still exists in the ledger with its original data.
- "Only the original owner can pass the closed account." No. Any transaction can reference an existing account by its public key.
- "Closing an account assigns it back to the System Program automatically." No. Ownership remains with the closing program unless explicitly reassigned.

## Key properties
1. The account discriminator must be set to `CLOSED_ACCOUNT_DISCRIMINATOR` or the account must be reassigned to the System Program.
2. Account data should be zeroed out when possible during closure.
3. Relying on an `is_initialized` boolean inside user data is insufficient protection.
4. Proper closure requires both lamport transfer and metadata invalidation.
5. Re-initialization instructions must verify the account is fresh or was properly closed.

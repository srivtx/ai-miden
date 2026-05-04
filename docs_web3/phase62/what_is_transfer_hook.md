# What Is Transfer Hook?

## The Problem
SPL Token cannot execute custom logic when tokens move. A project cannot enforce a blacklist, collect royalties, or require KYC on every transfer without wrapping the token in a separate program. Wrapping breaks composability with wallets and DeFi protocols.

## Definition
Transfer hook is a Token-2022 extension that invokes an external program every time a token is transferred. The hook program receives the sender, recipient, and amount, then decides whether to approve or reject the transfer.

## How It Works
1. **Create mint with transfer hook extension.** The mint is initialized with extra space for the hook configuration.
2. **Deploy hook program.** A developer writes and deploys a program that implements the transfer hook interface.
3. **Configure mint to point to hook program.** The mint stores the program ID of the hook.
4. **Create token accounts.** Users create associated token accounts under the Token-2022 program.
5. **Transfer triggers hook.** When a user calls `transfer`, the Token-2022 program CPIs into the hook program before finalizing the transfer.
6. **Hook program validates or rejects.** If the hook returns an error, the entire transfer reverts atomically.

## Real-life Analogy
Think of a bank wire that requires compliance approval. Every time money leaves the account, a compliance officer checks the sender against a blacklist. If the sender is flagged, the wire is canceled. The officer is the hook program, and the bank is Token-2022.

## Tiny Numeric Example
```rust
pub fn execute_hook(ctx: Context<ExecuteHook>) -> Result<()> {
    let sender = ctx.accounts.sender.key();
    // WHY: Load the sender to check against the blacklist.
    require!(sender != BLACKLIST, ErrorCode::Blacklisted);
    // WHY: Revert if the sender is blacklisted, blocking the transfer.
    Ok(())
    // WHY: Approve the transfer if validation passes.
}
```
If Alice sends 100 tokens and her address matches `BLACKLIST`, the transaction fails with `Blacklisted`.

## Common Confusion
- **No.** Transfer hooks do not make transfers free; they add compute cost.
- **No.** The hook program cannot modify the transfer amount; it can only approve or reject.
- **No.** Transfer hooks are not retroactive; they apply only to mints that enable the extension.
- **No.** Failing a hook does not burn tokens; it reverts the transfer.
- **No.** You cannot skip the hook if it is configured on the mint.
- **No.** Hooks do not execute on account creation; they execute only on transfer instructions.

## Key Properties
1. **Program-driven validation.** Any logic written in Rust or C can run.
2. **Atomic execution.** Hook failure reverts the entire transfer.
3. **Configurable per mint.** Each mint chooses its own hook program.
4. **Extra account support.** The hook can require additional accounts beyond sender and recipient.
5. **Failure reverts transfer.** Tokens never move unless the hook succeeds.

# What Is Reentrancy?

## Why it exists (THE PROBLEM)

Smart contracts often call external programs or transfer tokens before updating their own internal state.

If the external program calls back into the original contract before the state update completes, the original contract may execute based on stale assumptions.

This allows repeated withdrawals, unauthorized actions, or complete drainage of vaults and treasuries.

## Definition

Reentrancy is an attack where an external contract or program recursively calls back into the calling contract before the first invocation finishes.

It exploits incomplete state updates to drain funds or manipulate logic in ways the developer never intended.

Even a single missed state update can cascade into catastrophic fund loss.

## Real-life analogy

Imagine a naive bank teller who hands over cash before deducting the withdrawal from your account.

You ask for $100, receive it, but immediately ask again before the teller updates the ledger.

Because your balance still shows $500, the teller hands over another $100.

You repeat this until the vault is empty.

Reentrancy is that same loophole in code.

The program dispenses value before recording that it already did so, allowing callers to extract more than they are owed by exploiting the gap between action and accounting.

## Tiny numeric example

Consider a vault with 10 SOL and an attacker exploiting reentrancy:

| Call | Vault Balance | Attacker Balance | State Updated? |
|------|--------------|------------------|----------------|
| Initial | 10 SOL | 0 SOL | Yes |
| Withdraw 1 SOL | 9 SOL | 1 SOL | No (reentered) |
| Reenter withdraw | 8 SOL | 2 SOL | No (reentered) |
| Reenter withdraw | 7 SOL | 3 SOL | No (reentered) |
| ... | ... | ... | ... |
| Final | 0 SOL | 10 SOL | Yes (after loop) |

The attacker drained 10 SOL while the vault thought only 1 SOL was requested because the balance was not reduced before each external call.

This simple ordering mistake is one of the most expensive bug categories in blockchain history.

Developers must treat every external call as potentially hostile.

## Common confusion

- "Reentrancy only happens on Ethereum."
  While famous on Ethereum, cross-program invocations on Solana can also create reentrancy-like conditions if state is not updated before CPI.

- "Reentrancy requires malicious smart contracts."
  Any program that calls back into your program, even accidentally, can trigger reentrancy if your state is not protected by proper ordering.

- "Updating state at the end is always fine."
  The correct pattern is checks-effects-interactions ordering: validate, update state, then interact externally.

- "Reentrancy guards are enough."
  Guards help, but the best defense is updating all state before any external call that could reenter.

- "Solana does not have reentrancy."
  Solana does not have recursive synchronous calls like Ethereum, but indirect reentrancy via CPI and shared account state can still occur.

- "Small programs do not need to worry about reentrancy."
  Even simple vaults or escrow programs can be drained if they transfer before updating balances.

- "Reentrancy always steals all funds."
  Depending on the bug, reentrancy might mint extra tokens, manipulate prices, or corrupt accounting without immediate fund loss.

## Where it appears in our code

- `src_web3/phase24/vulnerable_program.rs`
  Demonstrates a withdrawal function that transfers tokens before updating the user balance, exposing a reentrancy vector.

- `src_web3/phase24/secure_program.rs`
  Shows the same function with state updated before the token transfer, preventing any reentrant call from exploiting stale state.

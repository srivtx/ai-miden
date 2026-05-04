Why it exists
-------------
Even with an escrow, there is a window where one party has deposited and the
other has not. The problem is that if the first depositor changes their mind,
their funds are temporarily locked. An Atomic Swap solves this by making the
entire trade happen in a single transaction where both transfers succeed or
both fail. There is no intermediate state where one party is exposed. This
gives participants confidence that they will either get what they agreed to or
keep what they started with.

Definition
----------
An Atomic Swap is a transaction in which multiple asset transfers are bundled
such that they all execute successfully together, or the entire transaction is
reverted with no partial changes.

Real-life analogy
-----------------
Imagine two people exchanging briefcases in a public square. Instead of handing
briefcases across a table, they place both briefcases into a sealed box with
a special lock. The lock only opens when both parties insert their keys at the
same time. If either person hesitates or walks away, the box remains sealed and
both briefcases stay inside. No one can take the other person's briefcase
without giving up their own. An atomic swap is that sealed box. Both transfers
are locked together, and the blockchain only opens the lock when both sides
are ready.

Tiny numeric example
--------------------
Alice has 500 USDC. Bob has 2 SOL. They agree to swap.
Transaction structure:
- Instruction 1: Transfer 500 USDC from Alice to Bob (SPL Token CPI)
- Instruction 2: Transfer 2 SOL from Bob to Alice (System Program CPI)
The transaction is submitted with signatures from both Alice and Bob.
Solana processes both instructions atomically.
Case A: Both instructions succeed. Alice gets 2 SOL, Bob gets 500 USDC.
Case B: Bob's account has insufficient SOL. Instruction 2 fails. The entire
transaction reverts. Alice keeps her 500 USDC. Bob keeps his remaining SOL.
There is never a case where one transfer succeeds and the other fails.

Common confusion
----------------
- Atomic swaps do not require a middleman or escrow account when both parties
  sign the same transaction. The transaction itself is the trust mechanism.
- Atomicity is guaranteed by the Solana runtime, not by the program logic.
  If any instruction returns an error, the runtime rolls back all changes.
- Atomic swaps require both parties to be online and sign simultaneously. This
  is different from async escrows where one party deposits first and waits.
- Cross-chain atomic swaps use hash-time-locked contracts and are much more
  complex than on-chain atomic swaps. Do not confuse the two.
- An atomic swap transaction can contain many instructions, not just two.
  A multi-party settlement can include dozens of transfers in one atomic bundle.
- The transaction fee is paid by the fee payer, who is usually one of the
  participants. Fee payment does not affect the atomicity of the swap itself.
- Atomic swaps are not reversible after confirmation. Once the block is
  finalized, the transfers are permanent. There is no undo button.

Where it appears in our code
----------------------------
`src_web3/phase14/escrow/src/lib.rs` — demonstrates how deposit instructions
are combined into a single transaction so that both sides commit atomically.

Atomic swap limitations
-----------------------
While atomic swaps eliminate partial execution risk, they require all parties
to sign the same transaction. This means participants must be online
simultaneously and coordinate their signatures. For asynchronous trades where
one party is offline, an escrow with state transitions is more appropriate.
Additionally, atomic swaps are limited to assets on the same ledger unless
combined with hash-time-locked contracts for cross-chain scenarios. On Solana,
atomic swaps are most commonly used for instant token exchanges between known
counterparties or for bundling multiple DeFi operations into a single
composite transaction.

Practical Atomic Swap checklist
-------------------------------
- Ensure all participants can sign within the same transaction lifetime.
- Set a recent blockhash that gives enough time for coordination.
- Verify all token accounts and balances before signing.
- Use simulation to preview the transaction outcome before submission.
- Document the fallback plan if the atomic swap fails or times out.

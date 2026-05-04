Why it exists
-------------
Solana programs run in complete isolation by default. A program cannot simply
open a file or call another program like you would in a normal operating system.
The problem is that many DeFi operations require multiple programs to work
together. For example, a lending protocol must transfer tokens, update prices,
and record debt all in a single transaction. Without a safe way for programs
to call each other, every program would have to reimplement token logic, oracle
feeds, and every other primitive. Cross-Program Invocation (CPI) solves this by
allowing one Solana program to securely invoke another program's instructions.

Definition
----------
Cross-Program Invocation is the mechanism by which a Solana program calls
another Solana program during instruction execution. The runtime verifies
that all account and signer requirements are met before the call proceeds.

Real-life analogy
-----------------
Imagine a mortgage broker processing your home loan. The broker does not hold
the cash, appraise the house, or insure the property themselves. Instead, they
act as a coordinator. They call the bank to release funds, the appraiser to
confirm value, and the insurer to issue coverage. Each party is independent,
but the broker makes coordinated requests on your behalf in a single meeting.
CPI works exactly like this broker. One program orchestrates multiple
specialized programs to complete a complex task atomically.

Tiny numeric example
--------------------
Program A is a lending program. Program B is the SPL Token program.
Alice deposits 100 USDC as collateral and borrows 50 SOL.
The lending program needs to invoke the token program twice:
1. Transfer 100 USDC from Alice to a vault account (CPI call 1)
2. Transfer 50 SOL from a pool account to Alice (CPI call 2)
Both CPI calls happen inside the same transaction. If either fails, the entire
transaction is rolled back. Alice's net position changes by +50 SOL and -100 USDC
or nothing at all. There is no partial execution.

Common confusion
----------------
- CPI is not an external HTTP API call. It is an internal runtime mechanism
  between on-chain programs. The programs never leave the blockchain.
- CPI does not break the atomicity of a transaction. If the called program
  fails, the entire transaction reverts, including any changes made before
  the CPI call.
- CPI is not recursion. Solana limits CPI depth to four levels to prevent
  infinite loops and stack exhaustion.
- The caller program does not inherit the signers of the original transaction
  automatically. Signers must be explicitly passed through the CPI context.
- CPI is not slower than a direct instruction. The runtime optimizes CPI calls
  because they stay within the same transaction processing pipeline.
- You cannot CPI into any arbitrary program unless the account list includes
  the program ID of the target and all accounts it requires.
- CPI calls consume compute units. Deep CPI chains or expensive target programs
  can hit the transaction compute budget limit.

Where it appears in our code
----------------------------
`src_web3/phase11/cpi_demo/src/lib.rs` — demonstrates a program that invokes
another program using `invoke` and `invoke_signed`.

Deeper look at CPI constraints
------------------------------
Developers must respect CPI constraints to avoid transaction failures. The
maximum CPI depth of four means a program can call another program, which can
call another, up to four levels. Exceeding this causes an immediate error.
Compute units are shared across the entire transaction, so a deeply nested CPI
chain may exhaust the budget even if each individual program is efficient.
Additionally, reentrancy is forbidden. A program cannot call itself directly
or indirectly through a chain of CPIs. These constraints are intentional;
they prevent infinite loops, stack overflow, and complex attack surfaces that
could destabilize the network.

Practical CPI checklist
-----------------------
- Include the target program ID in the account list.
- Verify all writable accounts are correctly marked.
- Pass signers explicitly; do not assume inheritance.
- Test CPI depth and compute usage under load.
- Never CPI into an untrusted program without validation.

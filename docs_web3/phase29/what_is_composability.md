# What is Cross-Program Composability?

## Why It Exists

Financial applications are not isolated.
A user might want to deposit tokens into a lending protocol, use the receipt tokens as collateral in a borrowing protocol, and swap the borrowed assets on an AMM.
Without composability, each action requires separate transactions, manual state tracking, and complex user interfaces.
Composability allows programs to call each other atomically within a single transaction.
This unlocks powerful financial primitives that would otherwise be impossible.
It is the foundation of decentralized finance.
Composability is why a single developer can build products that rival traditional banks.

## Definition

Cross-program composability is the ability of smart contracts on Solana to invoke each other directly within the same transaction.
It combines multiple operations into a single atomic execution where either all steps succeed or all revert together.
There are no partial executions in a composed transaction.
It is the Lego set of decentralized finance.
Each program is a brick; composability lets you build castles.
The most innovative DeFi products are simply novel arrangements of existing bricks.

## Real-Life Analogy

Imagine building a house.
Without composability, you would hire a plumber, wait for them to finish, then hire an electrician, wait again, then hire a painter.
Each step is isolated and slow.
Composability is a general contractor who brings the plumber, electrician, and painter onto the same job site.
They work simultaneously, coordinate through the contractor, and if the plumber bursts a pipe, the entire crew stops before the drywall goes up.

Everything happens as one coordinated project, not three separate gigs.
The homeowner signs one contract, not three.
The house is built faster and more safely.
No step proceeds unless all prerequisites are met.
If any trade fails, the entire day is rolled back.

## Tiny Numeric Example

A user has 100 USDC and wants maximum yield.

| Step | Program | Action | Result |
|---|---|---|---|
| 1 | Lending | Deposit 100 USDC | Receive 100 cUSDC |
| 2 | Vault | Stake 100 cUSDC | Receive 95 vault shares |
| 3 | AMM | Swap rewards to USDC | +2 USDC profit |
| 4 | Lending | Deposit 2 USDC | Compound position |

Without composability: 4 transactions, 4 approval clicks, risk of partial execution.
With composability: 1 transaction, 1 signature, all or nothing.
If step 3 fails, steps 1 and 2 automatically revert.
The user is never left in an inconsistent state.
This atomicity is what makes DeFi safe despite its complexity.
Users never need to trust intermediate steps because the blockchain guarantees all-or-nothing execution.

## Common Confusion

- **"Is this just calling multiple contracts?"** It is deeper. The programs share state and accounts within one atomic transaction, not separate sequential calls.
- **"Does composability mean programs know about each other?"** No. Programs remain independent. They communicate through shared accounts and cross-program invocations, not direct coupling.
- **"Is this unique to Solana?"** Ethereum has composability too, but Solana's account model and parallel execution make cross-program calls cheaper and faster.
- **"Can any program call any other program?"** Yes, but the calling program must know the target's instruction format and pass the correct accounts.
- **"Does composability create security risks?"** Yes. A bug in one program can affect composed transactions. Audits and sandboxing are essential.
- **"What if one step in the composition fails?"** The entire transaction reverts. Atomicity ensures partial state changes never occur.
- **"Is composability the same as interoperability?"** Interoperability is a broader term for chains talking to each other. Composability is programs within one chain calling each other.
- **"Do users pay more fees for composability?"** Users pay for the total compute used, but one composed transaction is usually cheaper than multiple separate transactions.
- **"Can I compose with closed-source programs?"** Yes, if you know the instruction format and account layout, which are visible on-chain.

## Key Properties

- **Atomicity:** Ensures all operations in a composed transaction succeed or fail together, eliminating partial state risks.
- **Account Sharing:** Allows multiple programs to read and write the same accounts within a single transaction.
- **Permissionless:** Any developer can compose with any existing protocol without requiring approval or special access.
- **Efficiency:** Bundles multiple operations into one transaction, reducing overall fees and confirmation time.
- **Modularity:** Encourages small, focused programs that can be combined into complex financial workflows.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase29/yield_aggregator.ts` composes staking, lending, and AMM programs into a single REST API that calculates combined yields and simulates multi-step strategies.

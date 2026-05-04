# What is a Program Interface?

## Why It Exists

Composability requires agreement.
If Program A wants to call Program B, it needs to know what instructions Program B accepts, what accounts it expects, and what data format to use.
Without a common interface, every integration becomes a bespoke reverse-engineering project.
Interfaces standardize these contracts so programs can interoperate predictably.
They are the grammar that allows different programs to speak to each other.
Without interfaces, composability would be chaos.

## Definition

A program interface is a defined set of instructions, account requirements, and data schemas that a smart contract exposes.
Other programs and clients can interact with it correctly without knowing its internal implementation.
The interface is the contract between programs.
It defines what is possible without revealing how it works.
It is the API specification for on-chain programs.
Well-designed interfaces enable ecosystems where thousands of applications can interoperate seamlessly.

## Real-Life Analogy

Imagine electrical outlets around the world.
A hair dryer designed for a US outlet will not plug into a UK socket without an adapter, and forcing it could start a fire.
An interface is the international standard that says "this shape, this voltage, this frequency."
When both the outlet and the plug follow the standard, any device works in any compliant socket.
No adapter needed, no sparks, no guessing.

The standard does not care about what is inside the hair dryer, only how it connects to the wall.
The interface enables interoperability across manufacturers.
You can buy any compliant device and know it will work.
This is the power of standards.
A world without standards would require custom adapters for every device.

## Tiny Numeric Example

A lending protocol defines its interface:

| Instruction | Accounts Required | Data Fields |
|---|---|---|
| Deposit | user, token_account, reserve, lending_market | amount: u64 |
| Withdraw | user, token_account, reserve, collateral | amount: u64 |
| Borrow | user, token_account, reserve, obligation | amount: u64 |
| Repay | user, token_account, reserve, obligation | amount: u64 |
| Liquidate | liquidator, obligation, collateral, reserve | repay_amount: u64 |

A yield aggregator calling Deposit only needs to provide these four accounts and one u64.
The interface hides the internal math, oracle lookups, and state updates.
The caller does not need to understand how interest rates are calculated.
It only needs to know which accounts to pass and what amount to specify.
This abstraction is what makes composability scalable.
New programs can integrate with existing ones without any coordination or communication between teams.

## Common Confusion

- **"Is an interface the same as an API?"** Similar concept, but an interface is at the program level on-chain, while an API is usually off-chain over HTTP.
- **"Does the interface expose the program's code?"** No. It exposes the instruction format and account layout, not the implementation logic.
- **"What is an IDL?"** Interface Definition Language. A JSON or file that describes a program's instructions and accounts for client code generation.
- **"Can interfaces change?"** They can, but changes break integrations. Stable interfaces are versioned or extended without removing old fields.
- **"Do I need an interface for my own frontend?"** Your frontend needs to construct transactions correctly. An IDL generated from the interface makes this automatic.
- **"What is CPI?"** Cross-Program Invocation. The Solana mechanism by which one program calls another program's interface instruction.
- **"Are interfaces enforced by the runtime?"** The runtime enforces account ownership and signatures. It does not enforce instruction semantics. That is the program's responsibility.
- **"Can I call a program without its interface?"** Only if you manually construct the correct instruction bytes and account list, which is error-prone.
- **"What happens if I pass the wrong accounts?"** The transaction fails. The runtime checks account types, but the program validates that the right accounts are in the right positions.

## Key Properties

- **Standardization:** Defines a common language so any program or client can interact without bespoke integration work.
- **Encapsulation:** Hides internal implementation details while exposing only the necessary instructions and account layouts.
- **Versioning:** Supports backward-compatible updates so existing integrations continue working as programs evolve.
- **Code Generation:** IDLs automatically produce client libraries in multiple languages from the interface definition.
- **Validation:** Enables compile-time and runtime checks that transactions are constructed correctly before submission.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase29/yield_aggregator.ts` defines `LendingInterface`, `StakingInterface`, and `AMMInterface` types that standardize how the aggregator composes with external protocols.

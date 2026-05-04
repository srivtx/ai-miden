# What Is Parallel Execution?

## Why It Exists

Traditional blockchains process transactions one by one because the global state could change in unpredictable ways if multiple transactions ran simultaneously, creating a sequential bottleneck.
Parallel execution exists to identify which transactions access disjoint parts of state and run them concurrently, multiplying throughput without requiring faster hardware or larger blocks.
Ethereum processes transactions sequentially because every transaction could potentially touch any account.
Solana breaks this assumption by requiring transactions to declare their account accesses upfront.
This declaration allows the runtime to schedule execution safely across multiple cores.
Without this innovation, Solana would be limited to the same throughput as other single-threaded blockchains.

## Definition

Parallel execution is the technique of analyzing transactions before execution to determine which accounts they touch, grouping non-overlapping transactions into batches that can be processed simultaneously across multiple CPU cores, and preserving sequential semantics only for transactions that conflict on shared state.
Solana uses this to achieve tens of thousands of transactions per second.
The runtime uses a multi-threaded scheduler that assigns non-conflicting transactions to different cores.
Conflicting transactions are ordered deterministically to maintain consistency.
The Sea Level runtime is Solana's specific implementation of this concept.
It is named after the elevation where all transactions are treated equally.

## Real-Life Analogy

Imagine a grocery store with ten checkout lanes.
If every customer buys completely different items from different aisles, all ten lanes can operate at full speed simultaneously without any employee intervention.
But if two customers both want the last gallon of milk from the same refrigerator, only one can proceed and the other must wait.
Solana's runtime scans every customer's basket before opening the lanes, grouping customers with no overlapping items into parallel lanes while sequencing those who compete for the same milk.
The store achieves higher throughput not by hiring faster cashiers or building bigger lanes, but by organizing the existing workflow more intelligently.
The head cashier knows exactly which refrigerators each customer needs before they reach the register.
Inventory conflicts are resolved before checkout begins.
This pre-planning is what makes the parallel lanes possible.

## Tiny Numeric Example

Throughput improvement with parallelization:

| Scenario | Sequential TPS | Parallel TPS | Speedup | CPU Cores Used |
|----------|---------------|--------------|---------|----------------|
| 10,000 independent transfers | 500 | 50,000 | 100x | 32 |
| 10,000 conflicting swaps | 500 | 500 | 1x | 1 |
| Mixed workload (80% independent) | 500 | 20,000 | 40x | 16 |

By pre-sorting transactions into non-overlapping groups, Solana achieves superlinear scaling for typical workloads where most transactions touch unrelated accounts.
The scheduler runs on the validator's CPU using SIMD instructions to detect conflicts rapidly before execution begins.
Independent transfers are the sweet spot for Solana's architecture.
DeFi protocols with high contention see less benefit but still outperform sequential execution.
The key insight is that real-world workloads are mostly independent.
Even during peak NFT mints, many transactions touch different accounts.
The scheduler dynamically adapts to workload characteristics in real time.
This adaptability ensures the network maintains high throughput under varying demand patterns.
During quiet periods, all transactions may fit in a single batch.
During busy periods, the scheduler maximizes core utilization by finding independent subsets.
This elastic behavior makes Solana efficient across a wide range of network conditions.
Developers do not need to think about parallelism; the runtime handles it automatically.

## Common Confusion

- Parallel execution is not automatic for all transactions; conflicts on shared accounts force sequential processing.
  Two swaps on the same liquidity pool must be ordered to prevent arbitrage exploitation.
- Solana does not use sharding to parallelize; it parallelizes within a single global state machine by scheduling access patterns.
  Sharding splits state across chains; Solana keeps one global state.
- Read-only accounts can be accessed in parallel by many transactions without conflicts because no state changes occur.
  The System Program is read-only for most transactions and never causes contention.
- Write-write conflicts are detected ahead of time by the transaction scheduler, not during execution, preventing race conditions.
  This pre-analysis is what makes safe parallelization possible.
- Parallel execution does not break atomicity; conflicting transactions are simply ordered deterministically, not dropped.
  Users never lose transactions due to conflicts; they just wait for their turn.
- GPUs are not required for parallel execution; multi-core CPUs with SIMD instructions suffice for Solana's workload.
  GPUs excel at matrix math, not at account-based transaction scheduling.
- Not all blockchains can adopt parallel execution easily; account-based models like Solana's enable it better than UTXO models.
  UTXO models have inherent parallelism but struggle with shared state contracts.
- Parallel execution requires clients to declare all account accesses upfront in the transaction.
  This explicit declaration is what enables the runtime to build an efficient execution schedule.

## Key Properties
## Where It Appears in Our Code

- `src_web3/phase3/proof_of_history_demo.rs` — Simulates transaction dependency analysis for parallel scheduling and conflict detection.
- `docs_web3/phase3/SUMMARY.md` — Connects parallel execution to PoH and Tower BFT as Solana's performance triad.
- `src_web3/phase4/account_model_demo.rs` — Upcoming phase where parallel execution batches modify independent data accounts.
- `src_web3/phase5/dev_environment_check.sh` — Ensures the multi-core CPU requirements for parallel execution are met.
- `docs_web3/phase3/what_is_proof_of_history.md` — Explains the ordering mechanism that provides transactions for the parallel scheduler.

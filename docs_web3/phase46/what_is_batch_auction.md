Why it exists
-------------
When multiple solvers compete to fulfill the same intent, the system needs a
fair way to decide who wins and at what price. A simple first-come-first-
served rule rewards speed over quality and can lead to gas wars. Batch
auctions exist to solve this by collecting all intents and all solver bids
over a fixed time window, then clearing the market in a single optimized
settlement. This prevents front-running, ensures fair price discovery, and
allows batching for gas efficiency. Without batch auctions, intent-based
systems would resemble chaotic races that favor bots with the lowest latency.

Definition
----------
A batch auction is a market mechanism that collects orders or intents during
a discrete time window and then clears them simultaneously using an
optimization algorithm. In the context of intents, a batch auction gathers
all user intents and all solver proposals for a period, then computes the
allocation that maximizes total surplus or user welfare. All trades in the
batch settle at the same time, often with uniform clearing prices. Batch
auctions eliminate temporal ordering advantages and reduce miner extractable
value.

Real-life analogy
-----------------
Imagine a farmers market where instead of vendors shouting prices all day,
every buyer writes their order on a slip and drops it in a box. Every seller
writes their offer and drops it in another box. At exactly noon, a market
manager opens both boxes and calculates the single price that clears the most
produce. All trades happen at noon at that price. Early birds do not get an
advantage, and no one can jump the line. Batch auctions work the same way for
intents: everything is collected, then settled together.

Tiny numeric example
--------------------
During a 60-second batch window, three intents arrive:
- Intent 1: Sell 1 ETH, min 1,900 USDC
- Intent 2: Sell 2 ETH, min 3,800 USDC
- Intent 3: Buy 2.5 ETH, max 4,900 USDC

Two solvers submit fills:
- Solver A: Proposes prices of 1,920, 1,910, and 1,960 USDC/ETH
- Solver B: Proposes prices of 1,930, 1,915, and 1,950 USDC/ETH

The batch auction optimizer selects Solver B for Intent 1 and Intent 2
because those prices are better for sellers, and Solver A for Intent 3
because 1,960 is better for the buyer. The batch settles all three trades in
a single block, and no solver could front-run another because the batch
closed simultaneously.

Common confusion
----------------
- Batch auctions are not continuous. They run in discrete windows, not tick-
  by-tick like traditional order books.
- Batch auctions do not guarantee the best price for every single intent.
  They optimize for the total batch, which may involve trade-offs.
- The clearing price in a batch auction can differ from the spot price at the
  start or end of the window because it is derived from all bids together.
- Batch auctions do not prevent solvers from operating. They change the
  competition from a speed race to a price optimization contest.
- Users do not need to wait indefinitely. Batches have fixed durations, and
  intents that cannot be filled are returned.
- Batch auctions are not the same as Dutch auctions. Dutch auctions lower
  prices over time. Batch auctions collect everything first, then clear.
- Batch auctions do not remove gas costs. They amortize them across many
  intents in a single settlement.

Where it appears in our code
----------------------------
`src_web3/phase46/intent_api.ts` implements a batch auction endpoint that
collects intents over a configurable window, ranks solver proposals, and
clears the batch in a simulated settlement phase.

Key properties
--------------
- Discrete windows: Trades are collected over fixed time intervals.
- Simultaneous clearing: All trades in a batch settle at the same moment.
- Fair ordering: Temporal arrival time within the window does not matter.
- Optimized matching: Algorithms maximize surplus across the whole batch.
- Gas efficiency: Many intents settle in a single transaction bundle.

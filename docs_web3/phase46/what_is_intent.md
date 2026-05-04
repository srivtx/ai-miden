Why it exists
-------------
Traditional blockchain transactions force users to specify exactly how a trade
or action should execute. This is rigid: you must know the exact path, the
exact pool, the exact gas settings, and you bear the risk of front-running
or slippage. Intents exist to solve this by letting users declare what they
want to achieve instead of how to achieve it. A user says "I want to sell 10
ETH for at least 20,000 USDC by tomorrow." The blockchain ecosystem then
competes to fulfill that goal in the best possible way. Without intents,
users are stuck micromanaging execution details that they should not need to
understand. Intents separate the desired outcome from the execution path,
making decentralized applications feel as simple as ordering from a menu.

Definition
----------
An intent is a signed message that expresses a desired end state rather than
a specific execution path. It specifies constraints such as input tokens,
output tokens, minimum amounts, deadlines, and conditions. Solvers then
compete to find the optimal way to satisfy the intent across chains, pools,
and protocols. The user only pays if the intent is fulfilled according to the
constraints. Intents shift execution risk from the user to professional
solvers.

Real-life analogy
-----------------
Imagine you want to send a gift to a friend overseas. The traditional
transaction approach is like packing the box yourself, choosing the airline,
filling out customs forms, and tracking every leg of the journey. An intent
is like walking into a courier shop and saying "I need this package in Tokyo
by Friday for under $50." The shop staff then figure out the best route,
carrier, and customs process. You do not care whether it flies through
Seoul or Anchorage as long as the constraints are met. The courier bears the
operational risk, and you pay only if the package arrives on time.

Tiny numeric example
--------------------
Alice wants to swap 1 ETH for USDC with the following intent:
- Input: 1 ETH
- Minimum output: 1,950 USDC
- Deadline: 30 minutes from now
- Maximum slippage: 1%

Solver A finds a direct pool offering 1,960 USDC and proposes a fill.
Solver B finds a two-hop route through a stablecoin bridge offering 1,970
USDC and proposes a fill. The intent system selects Solver B because it
offers a better outcome for Alice. If no solver can offer at least 1,950
USDC within 30 minutes, the intent expires and Alice pays nothing. Alice
never had to know about pools, hops, or gas limits.

Common confusion
----------------
- Intents are not transactions. A transaction says "swap exactly on Uniswap
  pool X." An intent says "get me the best USDC for my ETH."
- Intents do not guarantee execution. They are conditional offers that expire
  if no solver can satisfy the constraints.
- The user does not pay gas for failed intents. Only the winning solver pays
  execution costs, and only successful fills are settled.
- Intents are not limited to swaps. They can express bridges, limit orders,
  yield allocations, or social recovery actions.
- Solvers are not miners or validators. They are specialized agents that
  compete off-chain to find the best execution path.
- Intent-based systems do not remove trust entirely. Users must trust that
  the solver network is competitive and that the intent contract enforces
  constraints correctly.
- Intents do not automatically give the absolute best price in the universe.
  They give the best price among participating solvers during the open
  period.

Where it appears in our code
----------------------------
`src_web3/phase46/intent_api.ts` implements an Express API where users submit
intents with constraints, solvers propose fills with routes and prices, and
the system selects the winning solver based on user-defined criteria.

Key properties
--------------
- Declarative: Users specify outcomes, not execution steps.
- Conditional: No payment occurs unless constraints are satisfied.
- Competitive: Multiple solvers race to offer the best fill.
- Time-bounded: Intents expire after a deadline to protect users.
- Risk-shifted: Execution complexity moves from users to solvers.

Why it exists
-------------
In an intent-based architecture, someone must actually do the work of
figuring out how to fulfill user requests. Users do not want to manually
compare prices across dozens of pools, bridges, and chains. Solvers exist
to fill that gap. They are specialized agents that monitor intent pools,
evaluate possible execution paths, and compete to deliver the best outcome.
Without solvers, intents would sit unfulfilled because there would be no
party willing to bear the execution risk and complexity. Solvers turn
declarative wishes into concrete blockchain transactions.

Definition
----------
A solver is an off-chain agent or service that competes to fulfill user
intents by finding optimal execution paths across decentralized protocols.
Solvers analyze constraints such as token pairs, minimum output amounts,
deadlines, and chain boundaries. They construct transactions that satisfy
the intent, submit them to an intent settlement contract, and earn fees or
surplus when successful. Solvers may use inventory, borrowed liquidity, or
multi-step routes to achieve the desired outcome.

Real-life analogy
-----------------
Think of a solver as a travel agent competing against other travel agents.
You say "I want to be in Bali next Saturday for under $800." One agent finds
a direct flight for $750. Another finds a flight to Kuala Lumpur plus a
budget airline connection for $720. A third finds a last-minute deal through
a partner airline for $700. The winning agent books the trip, and you pay
$700. You never had to search Skyscanner yourself. The agents bore the
research burden, and only the winner gets the commission. Solvers work the
same way for blockchain execution.

Tiny numeric example
--------------------
Bob runs a solver node. It sees an intent: "Swap 5 ETH for at least 10,000
USDC within 10 minutes."

Bob's solver queries three liquidity sources:
- Direct DEX pool: 10,050 USDC
- Two-hop route via WBTC: 10,120 USDC
- Route across Layer 2 bridge: 10,080 USDC

Bob submits the two-hop route because it offers the highest output. If
selected, Bob earns a 0.05% solver fee on the 10,120 USDC output, which is
5.06 USDC. Bob also bears the gas cost of executing the two-hop transaction.
If gas costs 2 USDC, Bob nets 3.06 USDC profit. Another solver offering only
10,050 USDC would lose the competition.

Common confusion
----------------
- Solvers are not the same as market makers. Market makers provide continuous
  liquidity. Solvers compete opportunistically on discrete intents.
- Solvers do not control user funds. They construct transactions that the
  intent contract verifies before settlement.
- Solvers do not always win. Only the solver with the best proposal earns the
  right to execute, so competition drives efficiency.
- Solvers are not miners. They do not produce blocks. They produce
  transaction bundles that settle on-chain.
- Running a solver is not free. It requires fast infrastructure, inventory,
  and sophisticated pathfinding algorithms.
- Solvers do not guarantee the globally optimal price. They guarantee the
  best price they can find given their data and speed.
- Solvers can fail. If a solver submits a path that no longer exists by the
time the transaction is mined, the fill reverts and the solver loses gas.

Where it appears in our code
----------------------------
`src_web3/phase46/intent_api.ts` implements an Express API with a solver
simulation endpoint where multiple solvers submit proposed fills and the
system ranks them by output amount to select the winner.

Key properties
--------------
- Off-chain: Solvers run outside the blockchain for speed and data access.
- Competitive: Multiple solvers race to offer the best execution.
- Verified: The intent contract checks that the execution meets constraints.
- Incentivized: Solvers earn fees on successful fills.
- Risk-bearing: Solvers pay gas and inventory costs for failed attempts.

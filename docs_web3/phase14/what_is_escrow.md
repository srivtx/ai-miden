Why it exists
-------------
Peer-to-peer trading of tokens is risky. The problem is that if Alice sends
tokens first, Bob might not send his. If Bob sends first, Alice might not send
hers. Traditional exchanges solve this by acting as a trusted middleman, but
that introduces custody risk and counterparty failure. An Escrow program solves
this by holding both parties' assets in a neutral on-chain contract and only
releasing them when both sides have deposited their agreed-upon amounts. If
either side fails, the assets can be returned after a timeout.

Definition
----------
An Escrow is an on-chain smart contract that temporarily holds assets from two
or more parties and automatically releases them only when all agreed conditions
are satisfied.

Real-life analogy
-----------------
Imagine buying a house. You do not hand a suitcase of cash directly to the
seller, and the seller does not hand you the deed first. Instead, both parties
deposit their assets with a neutral escrow agent. The agent holds the cash and
the deed. Once inspections pass and financing clears, the agent simultaneously
hands you the deed and hands the seller the cash. If the deal falls through,
the agent returns each party's original assets. A blockchain escrow program is
that neutral agent, but it operates automatically according to code instead of
human discretion.

Tiny numeric example
--------------------
Alice wants to trade 100 USDC for 1 SOL with Bob.
1. Alice deposits 100 USDC into the escrow program.
2. Bob deposits 1 SOL into the escrow program.
3. The escrow state now shows: Alice_deposit = 100 USDC, Bob_deposit = 1 SOL.
4. Both parties confirm the trade.
5. The escrow program CPI transfers 1 SOL to Alice and 100 USDC to Bob.
If Bob never deposits, Alice can cancel after 24 hours and reclaim her 100 USDC.
If Alice never confirms, Bob can cancel after 24 hours and reclaim his 1 SOL.

Common confusion
----------------
- An escrow does not hold assets forever. It is designed for temporary custody
  during a specific trade and should include expiration logic.
- Escrow programs do not guarantee fair pricing. They only enforce the agreed
  terms. If the market price moves, the escrow still executes at the old rate.
- The escrow program does not need to be a third party in the legal sense. The
  program itself is the neutral party because its logic is public and immutable.
- Escrow state accounts must track both deposits independently. Mixing them
  into a single pool makes it impossible to return the correct asset on cancel.
- Canceling an escrow is not a penalty. It is a safety feature that returns
  funds if the counterparty does not participate.
- Escrows can involve more than two parties. Multi-party escrows are used for
  group purchases, crowdfunding, and complex settlement scenarios.
- An escrow is not a vault. A vault holds assets under long-term rules. An
  escrow holds assets for the duration of a single atomic transaction or trade.

Where it appears in our code
----------------------------
`src_web3/phase14/escrow/src/lib.rs` — implements deposit, confirmation,
cancellation, and release logic for two-party token trades.

Escrow design patterns
----------------------
Escrows vary in complexity based on the trade scenario. A simple two-party
escrow holds one asset from each side and releases on mutual confirmation.
A milestone escrow releases funds in stages as a service provider completes
deliverables. An over-the-counter escrow may include price oracles to verify
fair value before execution. When designing an escrow, always define the
happy path, the cancellation path, and the dispute path. The dispute path is
the most often neglected and the most critical when things go wrong.

Practical Escrow checklist
--------------------------
- Define cancellation conditions and timeouts clearly.
- Store deposits in separate token accounts per side for clean returns.
- Log every state transition with participant public keys.
- Prevent reinitialization or reuse of closed escrow accounts.
- Test both successful trades and cancellation scenarios thoroughly.
- Consider adding a small dispute resolution fee to deter spam.
- Document the escrow lifecycle clearly for all user-facing interfaces.
- Provide example transactions for each escrow state in documentation.

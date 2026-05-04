Why it exists
-------------
Economic security depends on credible threats. If stakers know they can
cheat without consequences, they will cheat. Slashing exists to solve this
by destroying a portion of a staker's collateral when they violate protocol
rules. It is the stick that complements the carrot of staking rewards.
Without slashing, proof-of-stake systems would be vulnerable to double-
signing, censorship, and lazy validation. Slashing turns misbehavior from a
free gamble into a guaranteed loss, aligning validator incentives with
network health. In restaking systems, slashing is especially important
because one stake backs multiple services, and misbehavior on any service
must have real economic consequences.

Definition
----------
Slashing is a penalty mechanism in proof-of-stake and restaking protocols
that destroys or locks a portion of a validator's staked assets when they
act maliciously or negligently. Common slashable offenses include double-
signing two conflicting blocks, signing invalid state transitions, prolonged
offline periods, and violating AVS-specific rules in restaking contexts. The
slashed assets are typically burned or redistributed to honest participants.
Slashing severity varies: some offenses incur a small percentage penalty,
while others result in total ejection from the validator set. Slashing
creates a strong financial disincentive against attacks.

Real-life analogy
-----------------
Imagine a ride-sharing driver who deposits a $1,000 security bond to join
the platform. The rules are clear: no drunk driving, no canceling rides
after acceptance, and no overcharging. If the driver breaks a rule, the
platform deducts money from the bond. A minor offense like a late arrival
costs $50. A major offense like drunk driving costs the entire $1,000 and
a permanent ban. The bond exists so that breaking the rules hurts. Drivers
who follow the rules get their bond back when they leave the platform, plus
their fare earnings. Slashing works the same way: good behavior is rewarded,
bad behavior costs you your collateral.

Tiny numeric example
--------------------
Charlie restakes 64 ETH to secure a decentralized bridge. The bridge AVS
defines three slashing tiers:
- Tier 1: Downtime over 4 hours in a day. Penalty: 1% of stake = 0.64 ETH.
- Tier 2: Signing an invalid withdrawal proof. Penalty: 10% of stake = 6.4
  ETH.
- Tier 3: Double-signing a conflicting block. Penalty: 100% of stake = 64
  ETH.

Charlie's operator goes offline for 6 hours due to a server crash. The AVS
slash contract detects the downtime and deducts 0.64 ETH from Charlie's
restaked balance. Charlie now has 63.36 ETH restaked. If the operator had
double-signed, Charlie would lose the entire 64 ETH. The penalties are
enforced automatically by the bridge's smart contracts without human
intervention.

Common confusion
----------------
- Slashing is not a fee. Fees are paid for service. Slashing is a penalty
  for misbehavior.
- Slashing does not only apply to validators. In restaking, it applies to
  any staker whose operator misbehaves.
- Slashing is not always 100%. Minor offenses often incur small penalties.
- Slashing cannot be reversed by calling customer support. It is enforced
  automatically by on-chain contracts.
- Slashing does not require a court ruling. Smart contracts enforce rules
  based on cryptographic evidence.
- Not all downtime is slashable. Most protocols have a grace period before
  penalties begin.
- Slashing is not unique to proof-of-stake. It can be used in any system
  where staked collateral secures behavior.

Where it appears in our code
----------------------------
`src_web3/phase48/restaking_api.ts` implements an Express API that simulates
slashing events across restaked services, including downtime penalties,
malicious behavior detection, and automated balance reduction.

Key properties
--------------
- Economic deterrence: Penalties make attacks more expensive than rewards.
- Automatic enforcement: Smart contracts apply slashes without human bias.
- Tiered severity: Minor and major offenses carry proportional penalties.
- Irreversible: Slashed assets are typically burned and cannot be recovered.
- Collective impact: In restaking, operator misbehavior affects all
  delegators.
- Transparent rules: Slashing conditions are known in advance and written
  into protocol code.

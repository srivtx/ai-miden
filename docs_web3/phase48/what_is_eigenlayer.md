Why it exists
-------------
New blockchain protocols need economic security to operate. Building a new
validator set from scratch is expensive, slow, and fragments security across
many small networks. EigenLayer exists to solve this by creating a
marketplace where Ethereum stakers can restake their ETH to secure any
protocol that needs trust. Protocols no longer need to launch their own
tokens and validators. They can simply plug into Ethereum's existing
security through EigenLayer. This makes new protocols safer to launch and
makes staked ETH more productive. Without EigenLayer, the blockchain
ecosystem would suffer from thousands of under-secured chains and wasted
capital.

Definition
----------
EigenLayer is a restaking protocol built on Ethereum that allows stakers to
opt in to securing additional services called Actively Validated Services,
or AVSs. Users who have staked ETH natively or through liquid staking
tokens deposit into EigenLayer smart contracts. They then delegate their
restaked ETH to operators who run AVS software. The operators validate the
AVS and earn rewards, which are shared with the restakers. If an operator
misbehaves, the restaked ETH can be slashed by the AVS slashing conditions.
EigenLayer effectively turns Ethereum's economic security into a shared
resource that any protocol can rent.

Real-life analogy
-----------------
Imagine a large security company with thousands of trained guards protecting
city buildings. A new shopping mall opens and needs security, but it cannot
afford to hire and train its own team. EigenLayer is like a platform that
lets the mall rent guards from the existing security company. The guards
still work for the original company, but they also patrol the mall during
certain hours. The mall pays for the extra service, the guards earn
overtime, and the original company manages hiring and discipline. If a guard
steals from the mall, the security company fires them and pays damages. The
mall gets professional security without building its own workforce.

Tiny numeric example
--------------------
Bob holds 100 stETH, a liquid staking token representing 100 ETH staked on
Ethereum. He deposits his 100 stETH into EigenLayer.

He delegates to an operator running two AVSs:
- AVS A: A data availability layer paying 3% annual yield
- AVS B: A decentralized sequencer paying 4% annual yield

Bob's operator earns rewards from both AVSs. After the operator takes a 10%
commission, Bob receives:
- Base Ethereum staking yield: 4%
- AVS A net yield: 3% * 0.9 = 2.7%
- AVS B net yield: 4% * 0.9 = 3.6%

Total annual yield: 10.3% on his 100 stETH. If the operator double-signs
on AVS B, Bob's restaked ETH can be slashed by the AVS B slashing contract,
reducing his balance. The extra yield compensates for this delegated risk.

Common confusion
----------------
- EigenLayer is not a blockchain itself. It is a set of smart contracts on
  Ethereum that manage restaking relationships.
- EigenLayer does not replace Ethereum staking. It adds an optional layer
  on top of existing stakes.
- Operators are not Ethereum validators. They run software for AVSs and use
  restaked ETH as collateral.
- AVSs are not sidechains. They are services that need economic security
  and can be anything from oracles to sequencers to bridges.
- Depositing into EigenLayer does not give you a new token by default.
  Your stake is represented internally by the protocol's accounting.
- EigenLayer does not protect you from slashing. It enforces slashing
  conditions defined by AVSs, which can be strict.
- EigenLayer is not the only restaking protocol, but it is the most
  prominent on Ethereum.

Where it appears in our code
----------------------------
`src_web3/phase48/restaking_api.ts` implements an Express API that simulates
EigenLayer-style restaking, including user deposits, operator delegation,
AVS registration, reward distribution, and slashing enforcement.

Key properties
--------------
- Shared security: Ethereum stakers extend their collateral to new services.
- AVS marketplace: Protocols launch services without native validator sets.
- Operator delegation: Users delegate restaked assets to operators who run
  AVS software.
- Slashing enforcement: AVSs define conditions under which restaked stake
  is penalized.
- Yield stacking: Restakers earn base layer plus AVS rewards.
- Trust minimization: EigenLayer uses smart contracts rather than trusted
  intermediaries.

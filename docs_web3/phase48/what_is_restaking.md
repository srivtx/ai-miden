Why it exists
-------------
In proof-of-stake systems, staked capital is locked to secure one specific
network. That capital earns rewards, but it cannot simultaneously be used for
other productive purposes like securing other protocols, providing
liquidity, or collateralizing loans. Restaking exists to solve this by
allowing already-staked assets to be reused to secure additional services.
Users stake once and then delegate their stake to multiple protocols,
earning extra rewards without deploying new capital. Without restaking,
capital efficiency in decentralized ecosystems would remain extremely low,
and new protocols would struggle to bootstrap their own security.

Definition
----------
Restaking is the practice of using staked assets from one blockchain to
provide economic security for additional protocols or services. Users who
have already staked tokens like ETH can opt to restake them through a
restaking protocol. The restaked assets serve as collateral that can be
slashed if the user or the service they support behaves maliciously. In
exchange, the user earns rewards from the original staking protocol plus
additional rewards from the restaking services. Restaking creates a shared
security marketplace where new protocols can rent economic security instead
of building their own validator sets from scratch.

Real-life analogy
-----------------
Imagine you own a house and use it as collateral to get a low-interest
mortgage. Normally, the bank holds the lien and the house secures only that
loan. Restaking is like a system that lets other trusted lenders also accept
your house as collateral for their loans, as long as the total borrowed does
not exceed the house value. You earn interest from all the loans, and every
lender knows the house can be sold to cover defaults. The house is still
yours, but its collateral value is used more efficiently across multiple
agreements. If you default on any loan, the house is liquidated to cover
losses, just as restaked assets can be slashed for misbehavior.

Tiny numeric example
--------------------
Alice stakes 32 ETH on Ethereum and earns 4% annual rewards, which is 1.28
ETH per year. She then restakes her 32 ETH through a restaking protocol to
secure three additional services:
- Data availability service: 2% annual reward
- Decentralized oracle network: 1.5% annual reward
- Cross-chain bridge: 2.5% annual reward

Alice's total annual yield becomes 4% + 2% + 1.5% + 2.5% = 10%, or 3.2 ETH
per year on her original 32 ETH. However, her 32 ETH is now subject to
slashing conditions from all four protocols. If she misbehaves on any one,
she loses a portion of her stake. The extra yield compensates her for the
additional slashing risk.

Common confusion
----------------
- Restaking does not create new tokens out of thin air. It reuses existing
  staked tokens as collateral for multiple obligations.
- Restaking is not risk-free. The restaked assets can be slashed by any
  protocol they secure, compounding risk.
- Restaking does not unstake your original position. The tokens remain
  staked on the base layer while also being pledged elsewhere.
- Restaking is not the same as liquid staking. Liquid staking gives you a
  receipt token. Restaking pledges the underlying stake to new services.
- Not all restaking services are equal. Some may have higher slashing risk
  or lower reward than others.
- Restaking does not guarantee higher net returns. If a slashing event
  occurs, the losses can exceed the extra rewards.
- Restaking protocols are not base-layer features. They are middleware
  layers built on top of existing staking systems.

Where it appears in our code
----------------------------
`src_web3/phase48/restaking_api.ts` implements an Express API that simulates
staking, restaking to multiple services, reward accrual, and slashing across
base and restaked protocols.

Key properties
--------------
- Capital efficiency: One stake secures multiple services.
- Additional yield: Users earn rewards from both base and restaked layers.
- Shared security: New protocols bootstrap security by renting staked capital.
- Compounded slashing risk: Misbehavior on any secured service can lead to
  stake loss.
- Delegation: Users choose which services to support with their restake.
- Middleware: Restaking protocols sit between base layer staking and
  consumer services.

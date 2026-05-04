## What Is Staking?

**The Problem:**
Blockchain networks and decentralized protocols require tokens to be
committed for long periods to secure the network, provide liquidity,
or align user incentives.

Simply asking users to lock their funds without compensation is
ineffective because capital has opportunity cost.
Users could trade, lend, or invest those tokens elsewhere.
There must be a mechanism to reward participants who voluntarily lock
their assets, creating a mutually beneficial relationship between the
protocol and its users.

**Definition:**
Staking is the process of locking tokens in a smart contract for a
defined period to earn rewards, typically in the form of additional
tokens.

It is used for network security in proof-of-stake blockchains,
governance participation, liquidity incentives, and yield distribution.
The staked tokens act as both a commitment and, in some cases, a
security deposit that can be slashed if the staker acts maliciously.

**Real-life analogy:**
Imagine a community garden where residents can grow their own vegetables.
The garden needs a fence, tools, and a water system, but no one wants
to pay for maintenance upfront.

The neighborhood association proposes a deal: anyone who deposits five
hundred dollars into a community lockbox for one year receives a share
of the harvest profits proportionally.

The locked money ensures you have a vested interest in the garden's
success, and you cannot withdraw early without losing some rewards.
At the end of the year, you get your five hundred dollars back plus a
profit share.

Staking works the same way: you commit capital to a protocol, you
cannot use it elsewhere during the commitment, and you earn a return
for helping the ecosystem thrive.

**Tiny numeric example:**
You stake 10,000 tokens in a pool that pays 0.000001 tokens per second
per staked token.

| Duration | Reward Rate | Tokens Staked | Rewards Earned | Total Value |
|----------|-------------|---------------|----------------|-------------|
| 1 day    | 0.000001/s  | 10,000        | 864            | 10,864      |
| 1 week   | 0.000001/s  | 10,000        | 6,048          | 16,048      |
| 1 month  | 0.000001/s  | 10,000        | 25,920         | 35,920      |
| 1 year   | 0.000001/s  | 10,000        | 315,360        | 325,360     |

Your effective APY is approximately 31.5%.
The rewards scale linearly with time and staked amount because the
rate is constant per token.

**Common confusion:**
- **"Staking is the same as holding."**
  No. Holding means the tokens sit in your wallet doing nothing.
  Staking means they are locked in a smart contract and actively
  generating rewards. The key difference is the lockup and the yield.

- **"Staking is risk-free."**
  No. Smart contract bugs, protocol exploits, and token price drops
  can all cause losses. The staking rewards may not compensate for a
  severe price decline.

- **"You can unstake instantly without penalty."**
  Some protocols allow instant unstaking, but many impose cooldown
  periods or penalty fees. Always read the specific rules of the
  contract you are using.

- **"Staking rewards come from thin air."**
  No. Rewards are funded by protocol emissions, transaction fees, or
  treasury reserves. Excessive staking rewards can dilute existing
  token holders through inflation.

- **"All staking requires running a validator node."**
  No. Direct validation requires a node, but delegated staking and
  liquidity staking allow everyday users to earn without any technical
  infrastructure.

- **"Staking guarantees a fixed return."**
  No. Most DeFi staking rewards fluctuate based on total staked amount,
  fee volume, and token price. The advertised rate is often an
  estimate, not a contractually guaranteed figure.

- **"Staking and lending are the same thing."**
  No. In staking, you usually retain ownership and vote with your stake.
  In lending, you transfer custody to borrowers and earn interest.
  The risks, reward sources, and legal structures differ.

**Where it appears in our code:**
`src_web3/phase18/staking/src/lib.rs` — Solana program that initializes
a staking pool, accepts token deposits, tracks stake time, and
calculates proportional rewards.

`src_web3/phase18/staking_api.ts` — TypeScript Express API that
simulates creating pools, staking, unstaking, and claiming rewards
with real-time APY display.

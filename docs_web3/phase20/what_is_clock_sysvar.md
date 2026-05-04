## What Is the Clock Sysvar?

**The Problem:**
Smart contracts need to make decisions based on time.
They must know when a vesting cliff has passed, when a time lock has
expired, or when a staking reward period has ended.

However, blockchains are distributed systems where different nodes may
have slightly different local clocks.
If contracts trusted the transaction submitter's timestamp, attackers
could forge future timestamps to unlock funds early or backdated
timestamps to steal past rewards.

There must be a decentralized, tamper-proof source of time that all
nodes agree on and that no single participant can manipulate.

**Definition:**
The Clock sysvar is a built-in Solana account that provides trustless,
on-chain time information.

It contains the current slot number, the current epoch, and the Unix
timestamp of the most recent block.
Because the Clock sysvar is maintained by the Solana runtime and
derived from validator consensus, it cannot be forged by individual
users or smart contracts.

Any program can read the Clock sysvar to make time-dependent decisions
without trusting external data sources.

**Real-life analogy:**
Imagine a public atomic clock in a town square, visible to everyone and
synchronized with global time standards.

When two people make a bet about what time an event occurred, they do
not trust each other's watches.
They both point to the town clock because it is maintained by an
independent authority and visible to all.

No one can secretly wind it forward or backward.
The Clock sysvar is the blockchain equivalent of that town square
clock: a single, authoritative time source that every program can
reference without trusting any individual participant.

**Tiny numeric example:**
A vesting contract releases ten percent of tokens per year starting
from a cliff.

| Clock.unix_timestamp | Vesting Start | Elapsed (seconds) | Elapsed (years) | Unlocked % |
|----------------------|---------------|-------------------|-----------------|------------|
| 1,700,000,000        | 1,600,000,000 | 100,000,000       | 3.17            | 31.7%      |
| 1,730,000,000        | 1,600,000,000 | 130,000,000       | 4.12            | 41.2%      |
| 1,780,000,000        | 1,600,000,000 | 180,000,000       | 5.70            | 57.0%      |

The contract reads Clock.unix_timestamp, subtracts the vesting start
time, and divides by seconds per year to determine the unlocked
percentage.
No user can manipulate this calculation because the timestamp comes
from the runtime.

**Common confusion:**
- **"The Clock sysvar is just the validator's local computer time."**
  No. It is derived from network consensus and Proof of History.
  Validators cannot arbitrarily set it because other validators would
  reject blocks with incorrect timestamps.

- **"You can trick a smart contract by sending a transaction with a fake timestamp."**
  No. Transactions do not carry timestamps.
  Programs read the Clock sysvar, which is set by the runtime during
  block production.

- **"Clock sysvar time is exactly the same as real-world time."**
  It is close but not perfectly synchronized.
  Solana timestamps are typically within a few hundred milliseconds of
  real time, but they can drift slightly during network issues.

- **"The Clock sysvar is an optional account you can ignore."**
  No. If your program logic depends on time, you must pass the Clock
  sysvar as an account in the transaction.
  Without it, the program cannot access on-chain time.

- **"Slot number and Unix timestamp are interchangeable."**
  No. Slots are block production units and can be skipped.
  Timestamps measure actual seconds.
  A program should use Unix timestamp for real-time intervals and
  slots for blockchain-native timing.

- **"Clock sysvar guarantees transactions execute at a specific time."**
  No. The Clock sysvar tells you the time when the transaction
  executes. It does not schedule future execution.
  You must submit a transaction after the deadline and the program
  checks the current time.

- **"All blockchains have a Clock sysvar."**
  No. The Clock sysvar is specific to Solana.
  Ethereum uses block.timestamp, which is different in semantics and
  security properties.

**Where it appears in our code:**
`src_web3/phase20/timelock/src/lib.rs` — The program reads
Clock::get()?.unix_timestamp to verify that the current time has passed
the lock expiration before releasing tokens.

`src_web3/phase20/timelock_api.ts` — The Express API uses Date.now() as
a proxy for the Clock sysvar to simulate time-based unlocks and
vesting calculations.

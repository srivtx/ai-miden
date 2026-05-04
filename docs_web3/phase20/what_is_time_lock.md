## What Is a Time Lock?

**The Problem:**
Smart contracts execute instantly and irreversibly.
This is one of their greatest strengths, but it is also a catastrophic
vulnerability when managing large treasuries, protocol upgrades, or
token releases.

A single compromised admin key or a malicious multisig member can drain
a treasury or force a destructive upgrade in a single transaction.
Once executed, there is no undo button.

There must be a mechanism that enforces a mandatory waiting period
between when an action is proposed and when it can be executed, giving
stakeholders time to review, react, and potentially cancel malicious
operations.

**Definition:**
A time lock is a smart contract mechanism that enforces a delay between
the initiation of an action and its execution.

During this delay, the action is visible to all participants but cannot
be finalized. Stakeholders can audit the pending action, and authorized
guardians can cancel it if it is harmful.

Time locks are used for treasury withdrawals, protocol parameter
changes, contract upgrades, and token emissions.
The delay itself is the security feature because it transforms an
instant exploit into a race that defenders can win.

**Real-life analogy:**
Imagine a bank vault with a time-delay lock.
The bank manager can enter the combination, but the door only unlocks
after forty-eight hours.

If robbers force the manager to open the vault, the police have two
full days to respond.
If the manager makes a mistake or acts maliciously, the bank board can
override the combination during the waiting period.

The delay does not prevent bad actions from being initiated, but it
prevents them from being executed instantly and irreversibly.
In blockchain, the time lock serves the same function: it creates a
public, immutable countdown during which the community can organize a
defense.

**Tiny numeric example:**
A protocol treasury holds one million tokens.
The time lock is set to three days.

| Day | Event | Status |
|-----|-------|--------|
| 1   | Admin initiates withdrawal of 1M tokens | Pending |
| 2   | Community spots the transaction and discusses | Pending |
| 3   | Guardians cancel the withdrawal | Cancelled |
| 4   | No execution possible | N/A |

If no one had canceled by day four, the withdrawal would execute.
The three-day window turns a potential instant rug pull into a public,
contestable event.

**Common confusion:**
- **"A time lock prevents bad actions entirely."**
  No. It only delays them.
  If no one monitors or cancels the pending action, it will still
  execute after the delay.

- **"Time locks make protocols slower than traditional finance."**
  No. Three-day delays are common in corporate governance for large
  transfers. Time locks bring blockchain governance in line with
  traditional best practices.

- **"Only admin keys can initiate time-locked actions."**
  No. Some protocols allow anyone to propose an action, and token
  holders vote to approve it before the time lock begins.

- **"Time locks protect against smart contract bugs."**
  No. Time locks protect against malicious or mistaken governance
  actions. A bug in the contract itself can still be exploited
  instantly if it is reachable without governance.

- **"You can bypass a time lock with a higher gas fee."**
  No. The time lock is enforced by the smart contract logic, not by
  transaction ordering. Miners cannot skip the block requirement.

- **"All time locks are the same length."**
  No. Protocols choose different delays based on risk.
  Treasury withdrawals might use seven days, while parameter tweaks
  might use two days.

- **"Time-locked funds are inaccessible during the delay."**
  No. The delay applies to the specific action, not the funds
  themselves. Funds that are not part of a pending withdrawal remain
  fully accessible.

**Where it appears in our code:**
`src_web3/phase20/timelock/src/lib.rs` — Solana program that locks
tokens until a specified Unix timestamp, allows early cancellation by
authorized guardians, and releases funds only after the deadline.

`src_web3/phase20/timelock_api.ts` — TypeScript Express API that
schedules lockups, checks remaining time against the Clock sysvar, and
enforces vesting schedules.

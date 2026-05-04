# What Is a Timelock

## Why It Exists

Even legitimate proposals approved by large majorities can contain subtle bugs, hidden exploits, or unintended consequences.
Voters often miss these issues during the initial review period.
A timelock delays execution after a proposal passes, creating a mandatory window for community review.
During this window, participants can prepare for changes or emergency-cancel a malicious result.
This prevents instant execution of harmful code.
It reduces the damage from compromised governance accounts or social engineering attacks.
Without timelocks, a single flash loan attack on governance tokens could pass and execute a malicious proposal in a single block.
The timelock transforms governance from reactive chaos into deliberate, reversible process.

## Definition

A timelock is a smart contract mechanism that enforces a mandatory delay between the approval of a proposal and its actual execution.
During this delay, authorized guardians or the broader community may veto or cancel the operation.
The cancellation must happen before the action becomes irreversible.
The delay duration is typically defined in the governance parameters.
It applies uniformly to all proposals of a certain risk class.

## Real-Life Analogy

Think of a nuclear launch protocol where the final button does not fire the missile immediately upon the president's order.
Instead, a passed order enters a two-hour countdown displayed on every screen in the command center.
During those two hours, intelligence analysts can verify the target coordinates against satellite imagery.
Military lawyers can review the legality of the strike.
Senior officers can abort if they detect a false alarm or unauthorized command.

The delay does not weaken presidential authority.
It adds a safety net against irreversible mistakes caused by panic, hacking, or miscommunication.
Similarly, in a DAO, the timelock does not diminish voter power.
It protects the community from the irreversible consequences of hasty or fraudulent decisions.
Once the countdown reaches zero, the approved action executes automatically.
No additional human intervention is required.

## Tiny Numeric Example

A protocol sets a 48-hour timelock on all treasury transfers exceeding 10,000 USDC:

| Proposal | Pass Time | Timelock End | Execution Time | Safety Window |
|----------|-----------|--------------|----------------|---------------|
| Transfer 15K | Day 0, 12:00 | Day 2, 12:00 | Day 2, 14:00 | 48 hours |
| Upgrade logic | Day 5, 08:00 | Day 7, 08:00 | Day 7, 09:00 | 48 hours |
| Transfer 5K | Day 10, 10:00 | Immediate | Day 10, 10:05 | No timelock |
| Emergency pause | Day 12, 15:00 | Day 12, 15:10 | Day 12, 15:10 | 10 minutes |

Small transactions skip the delay, while large or sensitive operations enforce the full wait.
Emergency functions may use shorter delays but require multi-signature approval.
This tiered approach balances security with operational flexibility.
It ensures that critical changes receive scrutiny while routine actions proceed efficiently.
Developers must carefully tune timelock durations for their specific use case.
A DeFi protocol handling billions may want a seven-day timelock, while a social app may only need a few hours.
The timelock duration should reflect the potential damage of a malicious proposal.
Higher value at risk justifies longer delays and more extensive community review periods.
Users should monitor the timelock queue regularly to catch any suspicious proposals before they execute.
Automated alerting tools can notify stakeholders when new proposals enter the execution window.

## Common Confusion

- A timelock is not a veto power reserved for a single person.
  It is a delay that may allow collective cancellation under predefined rules.
- Timelocks do not prevent execution entirely.
  They merely postpone it to allow review, preparation, and withdrawal of funds.
- Not all proposals need the same timelock duration.
  Parameter changes may use short delays while code upgrades use long ones.
- Timelocks are not trustless magical delays.
  They rely on a deployed program that must be audited and remain unexploited.
- A canceled proposal during timelock does not refund the gas costs already spent on voting and submission.
- Timelocks do not protect against all governance attacks.
  They only provide a detection and response window.
- Emergency administrative functions can bypass timelocks.
  They typically require multi-signature approval to prevent abuse.

## Key Properties
## Where It Appears in Our Code

The timelock logic is implemented in `src_web3/phase31/governance/src/lib.rs`.
The `execute_proposal` handler verifies the current blockchain slot.
It ensures the slot exceeds the proposal's eta before allowing state changes to occur.
This enforces the mandatory waiting period on every execution attempt.

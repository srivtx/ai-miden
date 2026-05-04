Why it exists
-------------
A signer set alone does not define how many people must agree. The problem is
that if every signer must approve, the system becomes fragile. If only one
signer is needed, there is no security improvement. The threshold is the
specific number of approvals required to execute an action. It is the precise
balance between security and operational flexibility.

Definition
----------
Threshold is the minimum number of distinct signers from the signer set that
must approve a transaction before the multisig program will execute it.

Real-life analogy
-----------------
Think of a nuclear launch protocol in a movie. There are five generals with
launch keys, but the system is designed so that any three keys turned
simultaneously will activate the launch. Two keys are not enough to prevent
accidental launches. Four or five keys work but are unnecessary. The threshold
of three is carefully chosen. It is high enough that a single rogue general
cannot act alone, but low enough that the system still functions if two
generals are unreachable. A multisig threshold is that launch requirement. It
ensures collusion requires multiple parties, while still allowing operations
during absences.

Tiny numeric example
--------------------
A project treasury uses a 3-of-5 multisig:
- Signer set size: 5
- Threshold: 3
Probability of compromise if one key is stolen: 0% (only 1 of 3 needed)
Probability of compromise if two keys are stolen: 0% (only 2 of 3 needed)
Probability of compromise if three keys are stolen: 100% (threshold met)
Operational resilience if two signers are on vacation: 100% (3 of 3 remaining)
Operational resilience if three signers are unavailable: 0% (only 2 of 3)
The threshold creates a trade-off space. Lower thresholds are more convenient.
Higher thresholds are more secure.

Common confusion
----------------
- Threshold is not a percentage. It is an absolute count of signers. A 3-of-5
  multisig has a threshold of 3, not 60 percent.
- Changing the threshold usually requires meeting the current threshold first.
  You cannot unilaterally raise or lower the bar.
- The threshold applies per transaction, not globally over time. Each new
  proposal starts from zero approvals and must reach the threshold independently.
- A threshold of 1 in a multisig is valid but removes all multi-party security.
  It is only useful for testing or as a temporary state during setup.
- Threshold does not limit who can propose a transaction. Usually any signer
  can propose, but only threshold-many can approve and execute.
- There is no universal best threshold. Treasuries often use 3-of-5 or 4-of-7.
  Critical operations might use 5-of-7 or higher.
- Threshold enforcement happens in the program logic. The runtime counts
  signatures on the transaction, but the program decides if that count meets
  the stored threshold.

Where it appears in our code
----------------------------
`src_web3/phase15/multisig/src/lib.rs` — stores the threshold in the multisig
config and validates that approval counts meet or exceed it before execution.

Threshold selection guidelines
------------------------------
Selecting a threshold is a risk management decision. A low threshold such as
2-of-3 offers convenience but is vulnerable if one key is compromised. A high
threshold such as 5-of-7 offers strong security but may stall operations during
vacations or emergencies. A common compromise is 3-of-5 for operational
 treasuries and 4-of-7 for larger or more sensitive funds. Some projects use
a tiered system where smaller transfers require a lower threshold and larger
transfers require a higher one. Document the rationale for your chosen
threshold so future maintainers understand the trade-offs.

Practical Threshold checklist
-----------------------------
- Align the threshold with the value and sensitivity of the assets controlled.
- Ensure enough signers are geographically and operationally distributed.
- Revisit the threshold periodically as the project grows.
- Avoid thresholds of exactly half the signer set to prevent deadlock.
- Test emergency scenarios where multiple signers are unreachable.
- Document the threshold rationale for future maintainers and auditors.

# What is Guardian Staking?

## The Problem
A bridge that trusts anonymous validators has no economic deterrent against collusion. If guardians can vote for free, a sybil attacker can spin up thousands of fake nodes and outvote honest participants. Phase 56 had no economic skin in the game. Phase 56v2 forces guardians to lock capital that is slashed if they sign maliciously.

## Definition
Guardian staking is an economic security mechanism where bridge validators deposit tokens into a programmatic vault. Their voting weight is tied to their staked amount. If a guardian signs an invalid mint or double-release, the bridge authority or an on-chain slashing condition can destroy or redistribute part of their stake.

## How It Works
1. Register: A guardian submits their Solana wallet and Ed25519 public key to the registry.
2. Deposit: The guardian transfers tokens into the stake vault using the `stake` instruction.
3. Validate: The bridge program reads the registry and only counts signatures from guardians with nonzero active stake.
4. Vote: Guardians observe lock events off-chain, sign message hashes, and submit signatures via a relayer.
5. Reward or Slash: Honest participation is tracked for future rewards; fraudulent signatures trigger a `slash` instruction that seizes stake.
6. Withdraw: After an unbonding period, an honest guardian can reclaim their principal.

## Real-life Analogy
Imagine a jury pool where jurors must post a cash bond before hearing a case. If a juror is caught taking a bribe to deliver a false verdict, the court keeps the bond. This bond makes the cost of corruption higher than the benefit, aligning incentives with truth.

## Tiny Numeric Example with Actual Stake Amounts
Guardian A registers and stakes 10,000 tokens.
Guardian B registers and stakes 5,000 tokens.
Guardian C registers and stakes 15,000 tokens.
Bridge threshold is 2 of 3.
Guardian A signs an invalid release (user never burned wrapped tokens).
The bridge authority calls `slash` on Guardian A for 10,000 tokens.
Guardian A's stake drops to 0 and `is_active` flips to false.
The bridge now requires signatures from Guardian B and Guardian C only.

## Common Confusion
- No, holding tokens in a wallet is not staking. Staking requires a programmatic lock that the bridge can verify and slash.
- No, staking once grants eternal voting rights. A guardian can be slashed to zero and deactivated at any time.
- No, slashing requires a court order. In this design, the bridge authority or an automated fraud proof can trigger slashing based on on-chain evidence.
- No, the staked tokens are the wrapped tokens being bridged. Stake is typically a separate governance or utility token to avoid circular collateral.
- No, guardians stake after they sign. Stake must be locked before the signature is accepted so the bridge has recourse.
- No, a guardian can withdraw immediately after a vote. Unbonding periods prevent hit-and-run attacks where a guardian withdraws right before a slash.

## Key Properties
1. Accountability: Every signature is tied to a specific staked identity that can be economically punished.
2. Sybil resistance: Creating fake guardian identities requires real capital, making spam attacks prohibitively expensive.
3. Transparent: Stake amounts and slash events are recorded on-chain and auditable by anyone.
4. Dynamic: New guardians can join, bad actors can be removed, and stake levels can change without redeploying the bridge.
5. Composable: The staking token can be a governance token, liquidity position, or any SPL token the bridge design specifies.

# What Is Bridge Security?

## The Problem

A cross-chain bridge controls more value than most individual protocols, making it the single highest-value target in Web3. If an attacker can trick the target chain into minting tokens that were never locked, or unlock tokens that were never burned, they create infinite money. Historical bridge hacks (Wormhole, Ronin, Nomad) have resulted in hundreds of millions of dollars in losses, often from a single bug in verification logic or a compromised guardian key.

## Definition

Bridge Security is the set of cryptographic, economic, and procedural safeguards that ensure a cross-chain bridge maintains a 1:1 backing between locked assets on the source chain and minted assets on the target chain, while preventing unauthorized minting, double-spending, and premature release.

## How It Works

1. **Lock Verification**: Before any wrapped token is minted, the target chain verifies cryptographic proof that a corresponding lock event occurred on the source chain and was attested by a threshold of guardians.
2. **Nonce Tracking**: Every bridge operation uses a strictly increasing nonce. The target chain records consumed nonces and rejects any replay of old proofs, preventing double-mint from the same lock event.
3. **Burn Verification**: Before releasing original tokens, the source chain verifies proof that wrapped tokens were burned on the target chain, ensuring the wrapped supply decreases 1:1.
4. **Guardian Slashing**: If a guardian signs an invalid attestation, anyone can submit fraud proof on-chain. The guardian's stake is slashed, creating an economic deterrent against collusion.
5. **Rate Limiting**: The bridge enforces daily or hourly caps on total volume. Even if verification is bypassed, the maximum damage is bounded.
6. **Emergency Pause**: A multi-sig or DAO governance can halt all mint and release operations while an investigation occurs, preventing exploit continuation.

## Real-Life Analogy

Imagine a central bank that issues gold-backed certificates. For every certificate created, an ounce of gold must enter the vault. The vault has five independent auditors who must sign off on every deposit. The bank keeps a numbered ledger so no deposit receipt can be cashed twice. If an auditor signs off on fake gold, they are fired and fined. The vault also has a daily limit on how many certificates can be issued. These layers ensure that certificates always equal gold.

## Tiny Numeric Example with Signatures and Thresholds

Consider a bridge with a 24-hour rate limit of 100,000 USDC and a guardian threshold of 3/5.

- Day 1, Hour 0: User A locks 50,000 USDC. Guardians G1, G2, G3 sign. Mint 50,000 wUSDC. Running total: 50,000.
- Day 1, Hour 6: User B locks 50,000 USDC. Guardians G1, G2, G3 sign. Mint 50,000 wUSDC. Running total: 100,000.
- Day 1, Hour 12: User C locks 10,000 USDC. Guardians G1, G2, G3 sign. The target chain rate limit contract checks: 100,000 + 10,000 > 100,000 limit. Mint is rejected and queued for the next window.
- Attacker tries to replay User A's proof with nonce=1 again. The target chain sees nonce=1 is already in `consumed_nonces`. Transaction reverts. Double-mint prevented.
- Attacker compromises G1 and G2. They submit a fake proof. Count = 2, threshold = 3. Transaction reverts. Double-mint prevented.
- Attacker compromises G1, G2, G3. They submit a fake proof for 200,000 USDC. Count = 3, meets threshold. However, the rate limit caps the mint at the remaining 0 in the current window. The attack is limited.

## Common Confusion

- **No.** A bridge cannot be secured by obscurity. Hiding the contract code or guardian identities does not prevent exploitation; only formal verification and audits provide real assurance.
- **No.** Multi-sig on a single EOA is not the same as a guardian network. A multi-sig is a single contract; guardians are independent validators with separate hardware and keys.
- **No.** Audits do not guarantee safety. They reduce risk but cannot catch all bugs. Continuous monitoring and bug bounties are necessary complements.
- **No.** Rate limiting does not prevent all attacks. It only bounds the damage per time window; strong verification is still required.
- **No.** Bridge security is not only about smart contract code. It includes key management, operational security of guardian nodes, and governance processes.
- **No.** A bridge does not need to be fully decentralized on day one to be secure. Security is a spectrum; even federated models with a small, reputable guardian set can be secure if properly engineered.

## Key Properties

1. **1:1 Backing Invariant**: Total wrapped supply must never exceed total locked collateral minus pending releases. This is the fundamental accounting identity of any bridge.
2. **Replay Resistance**: Cryptographic nonces and consumed-proof registries ensure every source event triggers at most one target action.
3. **Economic Deterrence**: Slashing makes the cost of a successful attack proportional to the stake controlled by malicious guardians, not just the gas cost of a transaction.
4. **Bounded Blast Radius**: Rate limits and circuit breakers ensure that even a total compromise cannot drain the entire bridge in a single block.
5. **Transparency**: All guardian attestations, mints, burns, and locks are emitted as on-chain events, allowing real-time monitoring by the community and automated alerting systems.

## Where It Appears

- Wormhole's Governor module (rate limiting per chain)
- Axelar's mandatory key rotations and threshold signatures
- LayerZero's configurable DVN security stacks
- Chainlink CCIP's Risk Management Network and anti-fraud checks
- Every production token bridge that has survived more than one year without a major hack

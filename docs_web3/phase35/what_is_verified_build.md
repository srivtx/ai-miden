# What Is a Verified Build

## Why It Exists

Users interacting with a smart contract have no way to know whether the deployed bytecode matches the advertised open-source code. A malicious developer could publish benign source code while deploying a backdoored binary. Verified builds solve this by using reproducible compilation and on-chain hashing to prove that the deployed program was built from exactly the claimed source repository.

## Definition

A verified build is a deterministic compilation process where the hash of the built binary is compared against the on-chain program data. If they match, the deployment is cryptographically proven to originate from the published source code, eliminating trust in the deployer alone.

## Real-Life Analogy

Imagine buying a prescription drug that ships in a sealed bottle with a QR code. You scan the code and see the exact factory batch, ingredients, and quality inspector who certified it. An independent laboratory publishes the expected chemical fingerprint, and your scan confirms the pills in your hand match that fingerprint exactly. You no longer need to trust the pharmacy blindly because chemistry verifies the claim.

## Tiny Numeric Example

Verification workflow for a Solana program:

| Step | Action | Output |
|------|--------|--------|
| 1 | Build from source hash abc123 | Binary with hash def456 |
| 2 | Fetch on-chain program data | Binary with hash def456 |
| 3 | Compare hashes | Match |
| 4 | Publish verification attestation | Public record confirms source = deployment |

If the on-chain hash were def999 instead, the verification would fail and warn users of a mismatch.

## Common Confusion

- A verified build is not an audit; it proves source fidelity but does not guarantee the code is secure.
- Reproducible builds are not automatic; they require pinned compiler versions and consistent build environments.
- Verified status does not prevent future upgrades; the verification must be rerun after every program redeployment.
- Hash matching is not subjective; it is a strict bitwise comparison with no tolerance for differences.
- Verification tools are not infallible; compromised build machines can still produce false positives.
- Open sourcing code without verification is not equivalent; users must trust that the published code matches deployment.
- Verified builds do not protect against dependency attacks; malicious crates or libraries can still introduce vulnerabilities.

## Key Properties
## Where It Appears in Our Code

The verification script `src_web3/phase35/verify_build.sh` automates deterministic builds and hash comparisons, while `src_web3/phase35/deployment_api.ts` exposes endpoints to query and display verification status per program.

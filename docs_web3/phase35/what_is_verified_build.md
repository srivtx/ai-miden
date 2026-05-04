# What Is a Verified Build

## The Problem

Users interacting with a smart contract have no way to know whether the deployed bytecode matches the advertised open-source code. A malicious developer could publish benign source code while deploying a backdoored binary. Verified builds solve this by using reproducible compilation and on-chain hashing to prove that the deployed program was built from exactly the claimed source repository.

## Definition

A verified build is a deterministic compilation process where the hash of the built binary is compared against the on-chain program data. If they match, the deployment is cryptographically proven to originate from the published source code, eliminating trust in the deployer alone.

## How It Works (Step-by-Step)

1. **Pin the build environment.** The developer records the exact versions of the Solana CLI, Rust toolchain, and BPF linker used for the original build. Any variance in compiler or linker can change the output hash.
2. **Build from source.** The developer runs `solana-verify build` or `cargo build-bpf` inside a clean checkout of the published repository. The tool compiles the source into a deterministic `.so` binary.
3. **Compute the local hash.** The build tool outputs a SHA-256 checksum of the binary, for example `a3f7c9e2b1d4058f6e4a2c7d9b0e1f3a5c8d2e7b4f6a1c3d9e0b2f4a6c8d1e3f5`.
4. **Fetch the on-chain program.** A verifier calls `solana program dump <PROGRAM_ID> onchain.so` to download the live bytecode from the cluster.
5. **Compare hashes.** The verifier runs `sha256sum onchain.so` and compares the result to the local build hash. A single bit difference causes a mismatch.
6. **Publish attestation.** If the hashes match, the developer or a third-party registry publishes a signed attestation that program ID X corresponds to source commit Y. Users can query this record instead of trusting the deployer.

## Real-Life Analogy

Imagine buying a prescription drug that ships in a sealed bottle with a QR code. You scan the code and see the exact factory batch, ingredients, and quality inspector who certified it. An independent laboratory publishes the expected chemical fingerprint, and your scan confirms the pills in your hand match that fingerprint exactly. You no longer need to trust the pharmacy blindly because chemistry verifies the claim.

## Tiny Numeric Example

Verification workflow for a Solana program using reproducible builds:

| Step | Action | Hash |
|------|--------|------|
| 1 | Build from source commit `9a4b2c1d` | `a3f7c9e2b1d4058f6e4a2c7d9b0e1f3a5c8d2e7b4f6a1c3d9e0b2f4a6c8d1e3f5` |
| 2 | Fetch on-chain program data | `a3f7c9e2b1d4058f6e4a2c7d9b0e1f3a5c8d2e7b4f6a1c3d9e0b2f4a6c8d1e3f5` |
| 3 | Compare hashes | Match |
| 4 | Publish verification attestation | Public record confirms source = deployment |

If a malicious actor had deployed a modified binary, the on-chain hash might have been `b4e8d0f3c2e5169a7f5b3d8e0c1f2a4b6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2`, and the comparison in step 3 would fail with a clear mismatch warning.

## Common Confusion

- No, a verified build is not a security audit; it proves source fidelity but does not guarantee the code is safe.
- No, reproducible builds are not automatic; they require pinned compiler versions and consistent build environments.
- No, verified status does not prevent future upgrades; verification must be rerun after every program redeployment.
- No, hash matching is not subjective; it is a strict bitwise comparison with zero tolerance for differences.
- No, verification tools are not infallible; compromised build machines can still produce false positives.
- No, open sourcing code without verification is not equivalent; users must trust that the published code matches deployment.

## Key Properties

- Deterministic compilation produces identical bytecode from identical source.
- Cryptographic hash comparison binds the on-chain binary to the published source.
- Public attestation registries allow users to query verification status by program ID.
- Pinned tooling versions eliminate environmental variance that could alter output.
- Rerunnable on demand by any third party, not just the original deployer.

## Where It Appears in Our Code

The verification script `src_web3/phase35/verify_build.sh` automates deterministic builds and hash comparisons, while `src_web3/phase35/deployment_api.ts` exposes endpoints to query and display verification status per program.

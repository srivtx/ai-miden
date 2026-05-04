# What Is Devnet

## Why It Exists

Deploying untested smart contracts directly to mainnet risks catastrophic financial loss from bugs, misconfigurations, or economic exploits. Devnet exists as a public testing environment where developers can deploy programs, mint fake tokens, and simulate attacks without spending real SOL or endangering user funds. It provides a realistic Solana runtime for integration testing while remaining completely separate from production value.

## Definition

Devnet is a public Solana cluster maintained by the core team where tokens have no real value and the ledger is periodically reset. It mirrors mainnet consensus rules and program behavior, allowing developers to validate deployments before promoting them to production.

## Real-Life Analogy

Imagine a Formula One team building a new car. Before racing in Monaco, they spend weeks on a private test track using the same tires, fuel, and regulations but without championship points at stake. Crashes on the test track teach engineers what to fix. Devnet is that test track: identical physics, zero real consequences.

## Tiny Numeric Example

Cost and behavior comparison for deploying a program:

| Environment | SOL Cost | Ledger Persistence | Airdrop Available | Recommended Use |
|-------------|----------|--------------------|-------------------|-----------------|
| Localnet | Zero | Reset on restart | Unlimited | Unit tests |
| Devnet | ~6 SOL (rent-exempt) | Reset monthly | 2 SOL/request | Integration tests |
| Mainnet | ~6 SOL (real value) | Permanent | None | Production |

A developer deploys to devnet three times, fixing bugs each iteration, before one final mainnet deployment.

## Common Confusion

- Devnet is not a private local validator; it is a public cluster shared by all developers worldwide.
- Devnet SOL has no monetary value; treating it as valuable is a mistake that leads to scam vulnerabilities.
- Devnet resets erase state; do not store permanent data or rely on addresses persisting forever.
- Passing devnet tests does not guarantee mainnet success; mainnet has higher congestion and real economic incentives.
- Devnet airdrops are not instant money faucets; they are rate-limited to prevent abuse.
- Programs on devnet are not automatically copied to mainnet; each environment requires an independent deployment.
- Devnet validators are not the same as mainnet validators; performance and geography differ.

## Key Properties
## Where It Appears in Our Code

Deployment scripts in `src_web3/phase35/deploy_pipeline.sh` target devnet for smoke testing before mainnet promotion, and the API in `src_web3/phase35/deployment_api.ts` tracks which environments host each program version.

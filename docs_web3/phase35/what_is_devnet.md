# What Is Devnet

## The Problem

Deploying untested smart contracts directly to mainnet risks catastrophic financial loss from bugs, misconfigurations, or economic exploits. Devnet exists as a public testing environment where developers can deploy programs, mint fake tokens, and simulate attacks without spending real SOL or endangering user funds. It provides a realistic Solana runtime for integration testing while remaining completely separate from production value.

## Definition

Devnet is a public Solana cluster maintained by the core team where tokens have no real value and the ledger is periodically reset. It mirrors mainnet consensus rules and program behavior, allowing developers to validate deployments before promoting them to production.

## How It Works (Step-by-Step)

1. **Generate a devnet keypair.** If you do not already have one, run `solana-keygen new --outfile ~/.config/solana/devnet.json` to create a wallet that will only be used on devnet.
2. **Request an airdrop.** Run `solana airdrop 5` after switching to devnet with `solana config set --url devnet`. The CLI contacts a devnet faucet and credits your wallet with 5 free SOL.
3. **Compile the program.** Use `cargo build-bpf` in your program directory to produce a `.so` binary. This is the exact artifact you will deploy.
4. **Deploy the program.** Run `solana program deploy target/deploy/your_program.so --keypair ~/.config/solana/devnet.json`. The CLI uploads the bytecode, creates a program account, and deducts the rent-exempt balance from your wallet.
5. **Check the deployed account.** Query the program with `solana program show <PROGRAM_ID>` to confirm the deployment slot, data size, and authority. You can also inspect associated accounts with `solana account <ACCOUNT_PUBKEY>`.
6. **Test a transaction.** Invoke your program through the CLI or a TypeScript client. Verify that instructions execute correctly, accounts mutate as expected, and error cases are handled before you consider a mainnet deployment.

## Real-Life Analogy

Imagine a Formula One team building a new car. Before racing in Monaco, they spend weeks on a private test track using the same tires, fuel, and regulations but without championship points at stake. Crashes on the test track teach engineers what to fix. Devnet is that test track: identical physics, zero real consequences.

## Tiny Numeric Example

A developer tests a program on devnet before mainnet:

| Step | Action | SOL Balance | Cost |
|------|--------|-------------|------|
| 1 | Airdrop requested | 5.000000 SOL | 0 SOL |
| 2 | Deploy program | 2.500000 SOL | 2.500000 SOL (rent-exempt) |
| 3 | Create test account | 2.499500 SOL | 0.000500 SOL |
| 4 | Invoke instruction | 2.499495 SOL | 0.000005 SOL |
| 5 | Second bug-fix deploy | 0.499495 SOL | 2.000000 SOL (redeploy) |
| 6 | Final mainnet deploy | -- | 2.500000 SOL (real value) |

The developer spent 4.500495 SOL of fake devnet funds across two iterations. Only the final mainnet deployment consumed real SOL.

## Common Confusion

- No, devnet is not a private local validator; it is a public cluster shared by all developers worldwide.
- No, devnet SOL has no monetary value; treating it as valuable leads to scam vulnerabilities.
- No, devnet state does not persist forever; ledger resets erase data periodically.
- No, passing devnet tests does not guarantee mainnet success; mainnet has higher congestion and real economic incentives.
- No, devnet airdrops are not unlimited instant money; they are rate-limited to prevent abuse.
- No, programs on devnet are not automatically copied to mainnet; each environment requires an independent deployment.

## Key Properties

- Public cluster with free airdrops and no real value at risk.
- Ledger resets periodically to keep storage manageable.
- Mirrors mainnet consensus rules and program runtime behavior.
- Supports full deployment, account creation, and transaction testing.
- Serves as the final integration gate before mainnet promotion.

## Where It Appears in Our Code

Deployment scripts in `src_web3/phase35/deploy_pipeline.sh` target devnet for smoke testing before mainnet promotion, and the API in `src_web3/phase35/deployment_api.ts` tracks which environments host each program version.

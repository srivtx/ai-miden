#!/bin/bash
# Build and deploy script for the Phase 54 DAO platform.
# This script compiles both Solana programs and deploys them to the cluster.

set -e
# Exit immediately if any command fails so partial deployments are avoided.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Resolve the script directory so relative paths work regardless of where the script is invoked.

cd "$SCRIPT_DIR"
# Move into the phase54 directory so Cargo and Solana CLI targets are correct.

echo "=== Building Governance Program ==="
# Print a header so the user knows which program is compiling.

cd governance
# Enter the governance program workspace.

cargo build-bpf
# Compile the Rust source into a Solana BPF shared object for on-chain deployment.

cd ..
# Return to the phase54 root to prepare for the next build.

echo "=== Building Treasury Program ==="
# Print a header so the user knows which program is compiling.

cd treasury
# Enter the treasury program workspace.

cargo build-bpf
# Compile the Rust source into a Solana BPF shared object for on-chain deployment.

cd ..
# Return to the phase54 root to prepare for deployment.

echo "=== Deploying Governance Program ==="
# Print a header so the user knows which program is being deployed.

solana program deploy governance/target/deploy/governance.so
# Deploy the governance BPF binary to the currently configured Solana cluster.
# The CLI returns the program ID which the user should save for API configuration.

echo "=== Deploying Treasury Program ==="
# Print a header so the user knows which program is being deployed.

solana program deploy treasury/target/deploy/treasury.so
# Deploy the treasury BPF binary to the currently configured Solana cluster.
# The CLI returns the program ID which the user should save for API configuration.

echo "=== Deployment Complete ==="
# Print a final confirmation so the user knows all steps succeeded.

echo "Update GOVERNANCE_PROGRAM_ID and TREASURY_PROGRAM_ID in dao_api.ts with the deployed addresses."
# Remind the user to update the TypeScript API constants so it routes transactions correctly.

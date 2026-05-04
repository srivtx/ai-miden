#!/usr/bin/env bash
# deploy.sh builds and deploys the Phase 53 NFT Marketplace programs to Solana.
# This script must be run from the project root after dependencies are installed.

# Exit immediately if any command fails to prevent partial deployments.
set -e

# Change to the script's directory so relative paths resolve correctly regardless of where the user invokes the script.
cd "$(dirname "$0")"

# Set the Solana cluster to devnet for testing before mainnet deployment.
solana config set --url devnet

# Verify the Solana CLI is installed and the wallet keypair exists.
if [ ! -f ~/.config/solana/id.json ]; then
  # If no keypair exists, generate one so the deployer has an identity.
  solana-keygen new --no-passphrase --silent
fi

# Airdrop devnet SOL to the deployer if the balance is low so account creation succeeds.
BALANCE=$(solana balance | awk '{print $1}')
# Convert balance to integer for comparison by removing the decimal portion.
BALANCE_INT=${BALANCE%.*}
if [ "$BALANCE_INT" -lt 5 ]; then
  echo "Airdropping 2 SOL for deployment fees"
  solana airdrop 2
fi

# Build the Escrow program first because the Marketplace program references it.
echo "Building Escrow program..."
cd escrow
# cargo build-bpf compiles the Rust code to Solana BPF bytecode.
cargo build-bpf
# Return to the phase53 directory to continue with the next program.
cd ..

# Deploy the Escrow program to devnet and capture its program ID.
echo "Deploying Escrow program..."
ESCROW_DEPLOY_OUTPUT=$(solana program deploy target/deploy/nft_escrow.so --output json)
# Extract the program ID from the JSON output using grep and sed so it can be passed to the marketplace build.
ESCROW_PROGRAM_ID=$(echo "$ESCROW_DEPLOY_OUTPUT" | grep -o '"programId": "[^"]*"' | sed 's/"programId": "//;s/"$//')
echo "Escrow Program ID: $ESCROW_PROGRAM_ID"

# Build the Marketplace program.
echo "Building Marketplace program..."
cd marketplace
# Compile the marketplace program to BPF.
cargo build-bpf
# Return to the phase53 directory.
cd ..

# Deploy the Marketplace program to devnet.
echo "Deploying Marketplace program..."
MARKETPLACE_DEPLOY_OUTPUT=$(solana program deploy target/deploy/nft_marketplace.so --output json)
MARKETPLACE_PROGRAM_ID=$(echo "$MARKETPLACE_DEPLOY_OUTPUT" | grep -o '"programId": "[^"]*"' | sed 's/"programId": "//;s/"$//')
echo "Marketplace Program ID: $MARKETPLACE_PROGRAM_ID"

# Export the program IDs as environment variables for the API server.
export ESCROW_PROGRAM_ID="$ESCROW_PROGRAM_ID"
export MARKETPLACE_PROGRAM_ID="$MARKETPLACE_PROGRAM_ID"

# Write the program IDs to a .env file so the API server can load them on startup.
echo "ESCROW_PROGRAM_ID=$ESCROW_PROGRAM_ID" > .env
echo "MARKETPLACE_PROGRAM_ID=$MARKETPLACE_PROGRAM_ID" >> .env
echo "SOLANA_RPC=https://api.devnet.solana.com" >> .env

# Display instructions for running the API server.
echo ""
echo "Deployment complete."
echo "Program IDs saved to .env"
echo "To start the API server, run:"
echo "  npm install express @solana/web3.js @solana/spl-token bs58"
echo "  npx ts-node marketplace_api.ts"

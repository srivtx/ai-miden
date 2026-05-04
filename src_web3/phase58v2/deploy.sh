#!/bin/bash
# WHY: This script automates building and deploying the Phase 58v2 launchpad programs to devnet

set -e # WHY: Exit immediately if any command fails to prevent partial deployments

echo "=== Phase 58v2: Building Launchpad Programs ===" # WHY: Header for user clarity

# WHY: Check if Anchor CLI is installed
if ! command -v anchor &> /dev/null; then
    echo "ERROR: Anchor CLI not found. Install with: npm install -g @coral-xyz/anchor-cli" # WHY: Anchor is required for building
    exit 1 # WHY: Cannot proceed without Anchor
fi

# WHY: Check if Solana CLI is installed
if ! command -v solana &> /dev/null; then
    echo "ERROR: Solana CLI not found. Install from https://docs.solana.com/cli/install" # WHY: Solana CLI required for deployment
    exit 1
fi

# WHY: Ensure wallet is configured
if [ -z "$ANCHOR_WALLET" ]; then
    export ANCHOR_WALLET="$HOME/.config/solana/id.json" # WHY: Default Solana keypair location
    echo "Using default wallet: $ANCHOR_WALLET" # WHY: Inform user of wallet path
fi

# WHY: Ensure devnet configuration
solana config set --url devnet # WHY: Target devnet for safe testing

echo "=== Building Launchpad Program ===" # WHY: Section header
cd src_web3/phase58v2/launchpad # WHY: Navigate to project directory
anchor build # WHY: Compile Rust to BPF bytecode

echo "=== Building Vesting Program ===" # WHY: Section header
# WHY: Vesting program is in the same workspace, built together by anchor build

echo "=== Deploying to Devnet ===" # WHY: Section header
anchor deploy # WHY: Deploy compiled programs to devnet

echo "=== Extracting Program IDs ===" # WHY: Section header
# WHY: Get deployed program IDs from Anchor logs
LAUNCHPAD_ID=$(solana address -k target/deploy/launchpad-keypair.json) # WHY: Read launchpad program ID
VESTING_ID=$(solana address -k target/deploy/vesting-keypair.json) # WHY: Read vesting program ID

echo "Launchpad Program ID: $LAUNCHPAD_ID" # WHY: Display for user to save
echo "Vesting Program ID: $VESTING_ID" # WHY: Display for user to save

# WHY: Write program IDs to .env for API usage
cat > .env <<EOF
LAUNCHPAD_PROGRAM_ID=$LAUNCHPAD_ID
VESTING_PROGRAM_ID=$VESTING_ID
SOLANA_RPC=https://api.devnet.solana.com
EOF

echo "=== Deployment Complete ===" # WHY: Success message
echo "Program IDs saved to .env" # WHY: Inform user of saved config
echo "" # WHY: Spacing for readability
echo "Next steps:" # WHY: Guide user on what to do next
echo "1. Copy the Program IDs above into your API config" # WHY: API needs program IDs
echo "2. Fund your wallet with devnet SOL: solana airdrop 2" # WHY: Devnet requires SOL for transactions
echo "3. Start the API: npx ts-node ../launchpad_api.ts" # WHY: Run the backend service

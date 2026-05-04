#!/bin/bash // WHY: Shebang for bash execution
set -e // WHY: Exit immediately if any command fails, preventing partial deployments

echo "=== Phase 55v2 Farm Deployment ===" // WHY: Identify deployment script in logs

# WHY: Verify Solana CLI is installed and available
if ! command -v solana &> /dev/null // WHY: Check for solana binary in PATH
    then // WHY: Binary not found
    echo "Solana CLI not found. Please install it first." // WHY: Inform user
    exit 1 // WHY: Exit with error code
fi // WHY: Check complete

# WHY: Verify Anchor CLI is installed and available
if ! command -v anchor &> /dev/null // WHY: Check for anchor binary in PATH
    then // WHY: Binary not found
    echo "Anchor CLI not found. Please install it first." // WHY: Inform user
    exit 1 // WHY: Exit with error code
fi // WHY: Check complete

# WHY: Ensure we are on devnet for safety (prevent accidental mainnet deployment)
CURRENT_CLUSTER=$(solana config get | grep "RPC URL" | awk '{print $3}') // WHY: Read current cluster from config
echo "Current cluster: $CURRENT_CLUSTER" // WHY: Log cluster

if [[ "$CURRENT_CLUSTER" != *"devnet"* ]] // WHY: Check if URL contains devnet
    then // WHY: Not on devnet
    echo "WARNING: Not on devnet. Switching to devnet..." // WHY: Warn user
    solana config set --url devnet // WHY: Force devnet to prevent mainnet accidents
fi // WHY: Cluster check complete

# WHY: Ensure payer wallet has sufficient balance for deployment
PAYER_BALANCE=$(solana balance | awk '{print $1}') // WHY: Get SOL balance
echo "Payer balance: $PAYER_BALANCE SOL" // WHY: Log balance

if (( $(echo "$PAYER_BALANCE < 2" | bc -l) )) // WHY: Need at least 2 SOL for program deployment and rent
    then // WHY: Insufficient balance
    echo "Insufficient balance. Requesting airdrop..." // WHY: Inform user
    solana airdrop 2 // WHY: Request 2 SOL from devnet faucet
fi // WHY: Balance check complete

echo "Building programs..." // WHY: Inform user of build start

# WHY: Build all programs in workspace with optimization
anchor build // WHY: Compile Rust programs to BPF bytecode

echo "Build complete. Verifying IDL..." // WHY: Inform user

# WHY: Verify IDL files were generated for client compatibility
if [ ! -f "./target/idl/farm.json" ] // WHY: Check farm IDL exists
    then // WHY: IDL missing
    echo "Farm IDL not found. Build may have failed." // WHY: Inform user
    exit 1 // WHY: Exit with error
fi // WHY: Check complete

if [ ! -f "./target/idl/boost.json" ] // WHY: Check boost IDL exists
    then // WHY: IDL missing
    echo "Boost IDL not found. Build may have failed." // WHY: Inform user
    exit 1 // WHY: Exit with error
fi // WHY: Check complete

echo "Deploying to devnet..." // WHY: Inform user

# WHY: Deploy programs to devnet
anchor deploy // WHY: Upload BPF bytecode to devnet and initialize program accounts

echo "Deployment complete!" // WHY: Inform user of success

# WHY: Extract deployed program IDs from Anchor.toml or deployment output
echo "Program IDs:" // WHY: Header for program IDs

grep -A 2 "\[programs.devnet\]" Anchor.toml // WHY: Display configured devnet program IDs

echo "Updating TypeScript clients with new program IDs..." // WHY: Inform user

# WHY: Update API and compounder with deployed program IDs if they changed
# WHY: In production, this would be automated via environment variables

echo "=== Deployment Summary ===" // WHY: Header for summary
echo "Farm program deployed to devnet" // WHY: Confirm farm deployment
echo "Boost program deployed to devnet" // WHY: Confirm boost deployment
echo "IDL files available in ./target/idl/" // WHY: Confirm client schemas
echo "Run 'anchor test --provider.cluster devnet' to execute integration tests" // WHY: Next step for user

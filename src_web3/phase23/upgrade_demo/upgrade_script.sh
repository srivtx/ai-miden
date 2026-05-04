#!/bin/bash
# This script demonstrates how to upgrade a Solana program using the CLI.
# It creates a buffer, writes the new ELF, and deploys it atomically.

# Exit immediately if any command fails to prevent partial upgrades.
set -e

# Define the program ID so the CLI knows which account to upgrade.
PROGRAM_ID="Upgrade33333333333333333333333333333333333333"

# Define the path to the compiled ELF binary produced by cargo build-sbf.
ELF_PATH="./target/deploy/upgrade_demo.so"

# Define the keypair of the account that holds upgrade authority.
UPGRADE_AUTHORITY="~/.config/solana/id.json"

# Define the RPC endpoint; use devnet for testing to avoid mainnet risks.
RPC_URL="https://api.devnet.solana.com"

# Step 1: Build the program to generate the latest ELF binary.
# We use build-sbf because Solana programs compile to the Berkeley Packet Filter format.
echo "Building program..."
cargo build-sbf

# Step 2: Create a buffer account to hold the new ELF bytecode temporarily.
# This avoids overwriting the live program during a potentially long upload.
echo "Creating buffer account..."
solana program write-buffer "$ELF_PATH" --buffer-authority "$UPGRADE_AUTHORITY" --url "$RPC_URL"

# Capture the buffer address printed by the CLI so we can deploy from it.
BUFFER_ADDRESS=$(solana program show --programs --url "$RPC_URL" | grep "Buffer" | tail -1 | awk '{print $1}')

# Step 3: Deploy the buffer contents into the live program account.
# This copies the verified buffer into the executable program account atomically.
echo "Deploying buffer to program $PROGRAM_ID..."
solana program deploy --program-id "$PROGRAM_ID" --buffer "$BUFFER_ADDRESS" --upgrade-authority "$UPGRADE_AUTHORITY" --url "$RPC_URL"

# Step 4: Verify the program was upgraded by checking its deployed slot.
# A higher last-deployed slot confirms the upgrade succeeded.
echo "Verifying upgrade..."
solana program show "$PROGRAM_ID" --url "$RPC_URL"

# Step 5: Close the buffer account to reclaim the rent deposit.
# Temporary buffers should always be cleaned up after deployment.
echo "Closing buffer account to reclaim rent..."
solana program close --buffers --buffer-authority "$UPGRADE_AUTHORITY" --url "$RPC_URL"

echo "Upgrade complete."

#!/usr/bin/env bash
# WHY: We use bash because it is universally available and makes it easy to chain build and deploy commands.
set -e
# WHY: set -e causes the script to exit immediately if any command fails, preventing partial or broken deployments.

# WHY: We determine the script's directory so we can reference project files with relative paths regardless of where the script is invoked from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# WHY: We define the base path for all source code so the script knows where the Rust programs live.
SRC_DIR="${SCRIPT_DIR}"

echo "========================================"
echo "Building AMM Pool Program"
echo "========================================"
# WHY: We change into the amm_pool directory because cargo build-bpf must run from the crate root.
cd "${SRC_DIR}/amm_pool"
# WHY: We build the program for the BPF target so it can be deployed to the Solana runtime.
cargo build-bpf
# WHY: We verify the build artifact exists before attempting deployment.
AMM_SO="${SRC_DIR}/amm_pool/target/deploy/amm_pool.so"
if [ ! -f "$AMM_SO" ]; then
  echo "ERROR: AMM pool build artifact not found at $AMM_SO"
  exit 1
fi
echo "AMM Pool built successfully: $AMM_SO"

echo ""
echo "========================================"
echo "Building Limit Order Program"
echo "========================================"
# WHY: We change into the limit_order directory for the same reason as above.
cd "${SRC_DIR}/limit_order"
cargo build-bpf
# WHY: We verify the build artifact exists before attempting deployment.
LIMIT_SO="${SRC_DIR}/limit_order/target/deploy/limit_order.so"
if [ ! -f "$LIMIT_SO" ]; then
  echo "ERROR: Limit order build artifact not found at $LIMIT_SO"
  exit 1
fi
echo "Limit Order built successfully: $LIMIT_SO"

echo ""
echo "========================================"
echo "Deploying to Devnet"
echo "========================================"
# WHY: We ensure the Solana CLI is configured for devnet so we do not accidentally deploy to mainnet.
solana config set --url devnet
# WHY: We airdrop a small amount of SOL to the default keypair so there are enough funds for deployment rent.
echo "Requesting airdrop if needed..."
solana airdrop 2 || true
# WHY: We use || true because airdrop can fail if the account already has enough SOL, and we do not want that to stop the script.

echo ""
echo "Deploying AMM Pool..."
# WHY: We capture the program ID output by solana program deploy so we can log it for the user.
AMM_OUTPUT=$(solana program deploy "$AMM_SO" 2>&1)
echo "$AMM_OUTPUT"
# WHY: We extract the program ID from the deployment output using grep and awk so the user can copy it into their API config.
AMM_PROGRAM_ID=$(echo "$AMM_OUTPUT" | grep "Program Id:" | awk '{print $3}')
if [ -z "$AMM_PROGRAM_ID" ]; then
  echo "ERROR: Failed to extract AMM Pool program ID"
  exit 1
fi
echo "AMM Pool Program ID: $AMM_PROGRAM_ID"

echo ""
echo "Deploying Limit Order..."
LIMIT_OUTPUT=$(solana program deploy "$LIMIT_SO" 2>&1)
echo "$LIMIT_OUTPUT"
LIMIT_PROGRAM_ID=$(echo "$LIMIT_OUTPUT" | grep "Program Id:" | awk '{print $3}')
if [ -z "$LIMIT_PROGRAM_ID" ]; then
  echo "ERROR: Failed to extract Limit Order program ID"
  exit 1
fi
echo "Limit Order Program ID: $LIMIT_PROGRAM_ID"

echo ""
echo "========================================"
echo "Deployment Complete"
echo "========================================"
# WHY: We print a summary so the user knows exactly what to put in their environment variables or API configuration.
echo "Update your API configuration with these values:"
echo "AMM_POOL_PROGRAM_ID=${AMM_PROGRAM_ID}"
echo "LIMIT_ORDER_PROGRAM_ID=${LIMIT_PROGRAM_ID}"
# WHY: We remind the user to fund their wallet because devnet airdrops are not always sufficient for large binaries.
echo ""
echo "NOTE: If deployment failed due to insufficient funds, run 'solana airdrop 2' again and retry."
